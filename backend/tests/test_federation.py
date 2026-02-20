"""Comprehensive tests for Cross-Database Federation feature.

This module tests:
- Virtual schema creation and management
- SQL table extraction and parsing
- Table-to-connection mapping
- Multi-database query routing
- Result merging (union and join)
- Join suggestion via LLM
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Stub cryptography module for tests
fernet_module = types.ModuleType("cryptography.fernet")


class _DummyFernet:
    def __init__(self, key):
        self.key = key

    @staticmethod
    def generate_key():
        return b"A" * 44

    def encrypt(self, payload: bytes) -> bytes:
        return payload

    def decrypt(self, token: bytes) -> bytes:
        return token


setattr(fernet_module, "Fernet", _DummyFernet)
setattr(fernet_module, "InvalidToken", Exception)
crypto_module = types.ModuleType("cryptography")
setattr(crypto_module, "fernet", fernet_module)
sys.modules.setdefault("cryptography", crypto_module)
sys.modules.setdefault("cryptography.fernet", fernet_module)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


# =============================================================================
# FEDERATION SERVICE TESTS
# =============================================================================


class TestFederationService:
    """Tests for FederationService."""

    @pytest.fixture
    def mock_state_store(self, tmp_path, monkeypatch):
        """Create a mock state store."""
        from backend.app.repositories.state import store as state_store_module

        # Clear NEURA_STATE_DIR to prevent .env override
        monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
        base_dir = tmp_path / "state"
        store = state_store_module.StateStore(base_dir=base_dir)
        state_store_module.set_state_store(store)
        return store

    @pytest.fixture
    def service(self, mock_state_store):
        """Create a FederationService instance."""
        from backend.app.services.federation.service import FederationService
        return FederationService()

    def test_extract_table_names_simple_select(self, service):
        """Extract table names from simple SELECT."""
        sql = "SELECT * FROM customers"
        tables = service._extract_table_names(sql)
        assert "customers" in tables

    def test_extract_table_names_select_with_alias(self, service):
        """Extract table names from SELECT with alias."""
        sql = "SELECT c.name FROM customers c"
        tables = service._extract_table_names(sql)
        assert "customers" in tables

    def test_extract_table_names_join(self, service):
        """Extract table names from JOIN query."""
        sql = "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id"
        tables = service._extract_table_names(sql)
        assert "orders" in tables
        assert "customers" in tables

    def test_extract_table_names_multiple_joins(self, service):
        """Extract table names from multiple JOINs."""
        sql = """
            SELECT * FROM orders
            JOIN customers ON orders.customer_id = customers.id
            JOIN products ON orders.product_id = products.id
            LEFT JOIN shipping ON orders.id = shipping.order_id
        """
        tables = service._extract_table_names(sql)
        assert "orders" in tables
        assert "customers" in tables
        assert "products" in tables
        assert "shipping" in tables

    def test_extract_table_names_comma_separated(self, service):
        """Extract table names from comma-separated tables."""
        sql = "SELECT * FROM orders, customers WHERE orders.customer_id = customers.id"
        tables = service._extract_table_names(sql)
        assert "orders" in tables
        assert "customers" in tables

    def test_extract_table_names_insert(self, service):
        """Extract table name from INSERT statement."""
        sql = "INSERT INTO orders (customer_id, product_id) VALUES (1, 2)"
        tables = service._extract_table_names(sql)
        assert "orders" in tables

    def test_extract_table_names_update(self, service):
        """Extract table name from UPDATE statement."""
        sql = "UPDATE customers SET name = 'John' WHERE id = 1"
        tables = service._extract_table_names(sql)
        assert "customers" in tables


class TestVirtualSchemaManagement:
    """Tests for virtual schema CRUD operations."""

    @pytest.fixture
    def mock_state_store(self, tmp_path, monkeypatch):
        """Create a mock state store."""
        from backend.app.repositories.state import store as state_store_module

        # Clear NEURA_STATE_DIR to prevent .env override
        monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
        base_dir = tmp_path / "state"
        store = state_store_module.StateStore(base_dir=base_dir)
        state_store_module.set_state_store(store)
        return store

    @pytest.fixture
    def service(self, mock_state_store):
        """Create a FederationService instance."""
        from backend.app.services.federation.service import FederationService
        return FederationService()

    @pytest.fixture
    def mock_connection_schema(self, monkeypatch):
        """Mock connection schema retrieval."""
        def mock_get_schema(conn_id, **kwargs):
            schemas = {
                "conn-1": {
                    "tables": [
                        {"name": "customers", "columns": [{"name": "id", "type": "INTEGER"}]},
                        {"name": "orders", "columns": [{"name": "id", "type": "INTEGER"}]},
                    ]
                },
                "conn-2": {
                    "tables": [
                        {"name": "products", "columns": [{"name": "id", "type": "INTEGER"}]},
                        {"name": "inventory", "columns": [{"name": "id", "type": "INTEGER"}]},
                    ]
                },
            }
            return schemas.get(conn_id, {"tables": []})

        monkeypatch.setattr(
            "backend.app.services.federation.service.get_connection_schema",
            mock_get_schema
        )

    def test_create_virtual_schema(self, service, mock_connection_schema):
        """Test creating a virtual schema."""
        from backend.app.schemas.federation import VirtualSchemaCreate

        request = VirtualSchemaCreate(
            name="Test Schema",
            description="A test schema",
            connection_ids=["conn-1", "conn-2"],
        )

        schema = service.create_virtual_schema(request)

        assert schema is not None
        assert schema.name == "Test Schema"
        assert schema.description == "A test schema"
        assert len(schema.connections) == 2
        assert len(schema.tables) == 4  # 2 tables per connection

    def test_list_virtual_schemas(self, service, mock_connection_schema):
        """Test listing virtual schemas."""
        from backend.app.schemas.federation import VirtualSchemaCreate

        # Create a schema first
        request = VirtualSchemaCreate(
            name="Schema 1",
            connection_ids=["conn-1"],
        )
        created = service.create_virtual_schema(request)

        schemas = service.list_virtual_schemas()
        assert len(schemas) == 1
        assert schemas[0].id == created.id

    def test_get_virtual_schema(self, service, mock_connection_schema):
        """Test getting a specific virtual schema."""
        from backend.app.schemas.federation import VirtualSchemaCreate

        request = VirtualSchemaCreate(
            name="Schema to Get",
            connection_ids=["conn-1"],
        )
        created = service.create_virtual_schema(request)

        retrieved = service.get_virtual_schema(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Schema to Get"

    def test_get_nonexistent_schema_returns_none(self, service):
        """Getting nonexistent schema should return None."""
        result = service.get_virtual_schema("nonexistent-id")
        assert result is None

    def test_delete_virtual_schema(self, service, mock_connection_schema):
        """Test deleting a virtual schema."""
        from backend.app.schemas.federation import VirtualSchemaCreate

        request = VirtualSchemaCreate(
            name="Schema to Delete",
            connection_ids=["conn-1"],
        )
        created = service.create_virtual_schema(request)

        result = service.delete_virtual_schema(created.id)
        assert result is True

        # Verify it's gone
        retrieved = service.get_virtual_schema(created.id)
        assert retrieved is None

    def test_delete_nonexistent_schema_returns_false(self, service):
        """Deleting nonexistent schema should return False."""
        result = service.delete_virtual_schema("nonexistent-id")
        assert result is False


class TestTableToConnectionMapping:
    """Tests for table-to-connection mapping."""

    @pytest.fixture
    def mock_state_store(self, tmp_path, monkeypatch):
        """Create a mock state store."""
        from backend.app.repositories.state import store as state_store_module

        # Clear NEURA_STATE_DIR to prevent .env override
        monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
        base_dir = tmp_path / "state"
        store = state_store_module.StateStore(base_dir=base_dir)
        state_store_module.set_state_store(store)
        return store

    @pytest.fixture
    def service(self, mock_state_store):
        """Create a FederationService instance."""
        from backend.app.services.federation.service import FederationService
        return FederationService()

    def test_map_tables_to_connections(self, service):
        """Test mapping tables to their connections."""
        from backend.app.schemas.federation import VirtualSchema, TableReference

        schema = VirtualSchema(
            id="test-schema",
            name="Test",
            description=None,
            connections=["conn-1", "conn-2"],
            tables=[
                TableReference(connection_id="conn-1", table_name="customers", alias="conn_customers"),
                TableReference(connection_id="conn-1", table_name="orders", alias="conn_orders"),
                TableReference(connection_id="conn-2", table_name="products", alias="conn_products"),
            ],
            joins=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        mapping = service._map_tables_to_connections(
            ["customers", "products"],
            schema
        )

        assert "conn-1" in mapping
        assert "conn-2" in mapping
        assert "customers" in mapping["conn-1"]
        assert "products" in mapping["conn-2"]

    def test_map_tables_by_alias(self, service):
        """Test mapping tables by their alias."""
        from backend.app.schemas.federation import VirtualSchema, TableReference

        schema = VirtualSchema(
            id="test-schema",
            name="Test",
            description=None,
            connections=["conn-1"],
            tables=[
                TableReference(connection_id="conn-1", table_name="customers", alias="c1_customers"),
            ],
            joins=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        # Map by alias
        mapping = service._map_tables_to_connections(["c1_customers"], schema)
        assert "conn-1" in mapping


class TestResultMerging:
    """Tests for merging results from multiple connections."""

    @pytest.fixture
    def mock_state_store(self, tmp_path, monkeypatch):
        """Create a mock state store."""
        from backend.app.repositories.state import store as state_store_module

        # Clear NEURA_STATE_DIR to prevent .env override
        monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
        base_dir = tmp_path / "state"
        store = state_store_module.StateStore(base_dir=base_dir)
        state_store_module.set_state_store(store)
        return store

    @pytest.fixture
    def service(self, mock_state_store):
        """Create a FederationService instance."""
        from backend.app.services.federation.service import FederationService
        return FederationService()

    def test_merge_single_result(self, service):
        """Single result should be returned as-is."""
        results = [
            {"columns": ["id", "name"], "rows": [[1, "Alice"], [2, "Bob"]]}
        ]

        merged = service._merge_results(results)

        assert merged["columns"] == ["id", "name"]
        assert len(merged["rows"]) == 2

    def test_merge_union_results(self, service):
        """Multiple results should be unioned without join keys."""
        results = [
            {"columns": ["id", "name"], "rows": [[1, "Alice"]]},
            {"columns": ["id", "name"], "rows": [[2, "Bob"]]},
        ]

        merged = service._merge_results(results, None)

        assert merged["columns"] == ["id", "name"]
        assert len(merged["rows"]) == 2
        assert merged["merge_type"] == "union"

    def test_merge_results_different_columns(self, service):
        """Merging results with different columns should include all."""
        results = [
            {"columns": ["id", "name"], "rows": [[1, "Alice"]]},
            {"columns": ["id", "email"], "rows": [[2, "bob@example.com"]]},
        ]

        merged = service._merge_results(results, None)

        assert "id" in merged["columns"]
        assert "name" in merged["columns"]
        assert "email" in merged["columns"]

    def test_merge_with_join_key(self, service):
        """Merging with join key should perform join."""
        results = [
            {"columns": ["id", "name"], "rows": [[1, "Alice"], [2, "Bob"]]},
            {"columns": ["id", "email"], "rows": [[1, "alice@example.com"], [3, "charlie@example.com"]]},
        ]

        merged = service._merge_results(results, ["id"])

        assert merged["merge_type"] == "join"
        # Only row with id=1 should match
        assert len(merged["rows"]) == 1
        assert merged["rows"][0][0] == 1  # id
        assert merged["rows"][0][1] == "Alice"  # name

    def test_merge_empty_results(self, service):
        """Merging empty results should return empty."""
        merged = service._merge_results([])

        assert merged["columns"] == []
        assert merged["rows"] == []
        assert merged["row_count"] == 0


class TestFederatedQueryExecution:
    """Tests for federated query execution."""

    @pytest.fixture
    def mock_state_store(self, tmp_path, monkeypatch):
        """Create a mock state store."""
        from backend.app.repositories.state import store as state_store_module

        # Clear NEURA_STATE_DIR to prevent .env override
        monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
        base_dir = tmp_path / "state"
        store = state_store_module.StateStore(base_dir=base_dir)
        state_store_module.set_state_store(store)
        return store

    @pytest.fixture
    def service(self, mock_state_store):
        """Create a FederationService instance."""
        from backend.app.services.federation.service import FederationService
        return FederationService()

    @pytest.fixture
    def mock_connection_schema(self, monkeypatch):
        """Mock connection schema retrieval."""
        def mock_get_schema(conn_id, **kwargs):
            schemas = {
                "conn-1": {
                    "tables": [
                        {"name": "customers", "columns": [{"name": "id", "type": "INTEGER"}]},
                    ]
                },
                "conn-2": {
                    "tables": [
                        {"name": "orders", "columns": [{"name": "id", "type": "INTEGER"}]},
                    ]
                },
            }
            return schemas.get(conn_id, {"tables": []})

        monkeypatch.setattr(
            "backend.app.services.federation.service.get_connection_schema",
            mock_get_schema
        )

    def test_execute_query_single_connection(self, service, mock_connection_schema, monkeypatch):
        """Query on single connection should execute directly."""
        from backend.app.schemas.federation import (
            VirtualSchemaCreate,
            FederatedQueryRequest,
        )

        # Create schema
        request = VirtualSchemaCreate(
            name="Single Connection Schema",
            connection_ids=["conn-1"],
        )
        schema = service.create_virtual_schema(request)

        # Mock query execution
        def mock_execute(connection_id, sql, limit=None):
            return {
                "columns": ["id", "name"],
                "rows": [[1, "Alice"]],
            }

        monkeypatch.setattr(
            "backend.app.repositories.connections.db_connection.execute_query",
            mock_execute
        )

        query_request = FederatedQueryRequest(
            virtual_schema_id=schema.id,
            sql="SELECT * FROM customers",
            limit=100,
        )

        result = service.execute_query(query_request)

        assert result is not None
        assert result["routing"] == "single"
        assert len(result["executed_on"]) == 1

    def test_execute_query_schema_not_found(self, service):
        """Query on nonexistent schema should raise error."""
        from backend.app.schemas.federation import FederatedQueryRequest
        from backend.app.utils.errors import AppError

        query_request = FederatedQueryRequest(
            virtual_schema_id="nonexistent",
            sql="SELECT * FROM customers",
        )

        with pytest.raises(AppError) as exc_info:
            service.execute_query(query_request)

        assert exc_info.value.code == "schema_not_found"

    def test_execute_query_no_connections(self, service, mock_state_store):
        """Query on schema with no connections should raise error."""
        from backend.app.schemas.federation import FederatedQueryRequest
        from backend.app.utils.errors import AppError

        # Manually create a schema with no connections
        store = mock_state_store
        with store._lock:
            state = store._read_state()
            state.setdefault("virtual_schemas", {})["empty-schema"] = {
                "id": "empty-schema",
                "name": "Empty",
                "connections": [],
                "tables": [],
                "joins": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
            store._write_state(state)

        query_request = FederatedQueryRequest(
            virtual_schema_id="empty-schema",
            sql="SELECT * FROM customers",
        )

        with pytest.raises(AppError) as exc_info:
            service.execute_query(query_request)

        assert exc_info.value.code == "no_connections"


class TestJoinSuggestion:
    """Tests for AI-powered join suggestion."""

    @pytest.fixture
    def mock_state_store(self, tmp_path, monkeypatch):
        """Create a mock state store."""
        from backend.app.repositories.state import store as state_store_module

        # Clear NEURA_STATE_DIR to prevent .env override
        monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
        base_dir = tmp_path / "state"
        store = state_store_module.StateStore(base_dir=base_dir)
        state_store_module.set_state_store(store)
        return store

    @pytest.fixture
    def service(self, mock_state_store):
        """Create a FederationService instance."""
        from backend.app.services.federation.service import FederationService
        return FederationService()

    @pytest.fixture
    def mock_connection_schema(self, monkeypatch):
        """Mock connection schema retrieval."""
        def mock_get_schema(conn_id, **kwargs):
            schemas = {
                "conn-1": {
                    "tables": [
                        {
                            "name": "customers",
                            "columns": [
                                {"name": "id", "type": "INTEGER"},
                                {"name": "name", "type": "TEXT"},
                            ]
                        },
                    ]
                },
                "conn-2": {
                    "tables": [
                        {
                            "name": "orders",
                            "columns": [
                                {"name": "id", "type": "INTEGER"},
                                {"name": "customer_id", "type": "INTEGER"},
                            ]
                        },
                    ]
                },
            }
            return schemas.get(conn_id, {"tables": []})

        monkeypatch.setattr(
            "backend.app.services.federation.service.get_connection_schema",
            mock_get_schema
        )

    def test_suggest_joins_with_mock_llm(self, service, mock_connection_schema, monkeypatch):
        """Test join suggestion with mocked LLM response."""
        mock_llm = MagicMock()
        mock_llm.complete.return_value = {
            "choices": [{
                "message": {
                    "content": """[
                        {
                            "left_connection_id": "conn-1",
                            "left_table": "customers",
                            "left_column": "id",
                            "right_connection_id": "conn-2",
                            "right_table": "orders",
                            "right_column": "customer_id",
                            "confidence": 0.95,
                            "reason": "customer_id in orders references id in customers"
                        }
                    ]"""
                }
            }]
        }

        monkeypatch.setattr(service, "_get_llm_client", lambda: mock_llm)

        suggestions = service.suggest_joins(["conn-1", "conn-2"])

        assert len(suggestions) == 1
        assert suggestions[0].left_table == "customers"
        assert suggestions[0].right_table == "orders"
        assert suggestions[0].confidence == 0.95

    def test_suggest_joins_insufficient_connections(self, service, mock_connection_schema):
        """Join suggestion with < 2 connections should return empty."""
        suggestions = service.suggest_joins(["conn-1"])
        assert suggestions == []

    def test_suggest_joins_llm_error(self, service, mock_connection_schema, monkeypatch):
        """Join suggestion should handle LLM errors gracefully."""
        mock_llm = MagicMock()
        mock_llm.complete.side_effect = Exception("LLM error")

        monkeypatch.setattr(service, "_get_llm_client", lambda: mock_llm)

        suggestions = service.suggest_joins(["conn-1", "conn-2"])
        assert suggestions == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
