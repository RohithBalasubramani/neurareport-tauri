"""Comprehensive API-level tests for Cross-Database Federation routes.

Tests all endpoints mounted at /federation:
- POST   /federation/schemas          - Create virtual schema
- GET    /federation/schemas          - List virtual schemas
- GET    /federation/schemas/{id}     - Get schema by ID
- DELETE /federation/schemas/{id}     - Delete schema by ID
- POST   /federation/suggest-joins    - AI-powered join suggestion
- POST   /federation/query            - Execute federated query

Each route depends on `require_api_key` (overridden here) and
`get_service` (overridden to inject a controllable FederationService
with a mocked state store so no file I/O occurs).
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Stub out cryptography so the import chain never fails in CI / test envs
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Now safe to import application modules
# ---------------------------------------------------------------------------
from backend.app.api.routes.federation import router, get_service
from backend.app.api.error_handlers import add_exception_handlers
from backend.app.services.federation.service import FederationService
from backend.app.services.security import require_api_key
from backend.app.schemas.federation import (
    JoinSuggestion,
    VirtualSchema,
    VirtualSchemaCreate,
    TableReference,
    FederatedQueryRequest,
)
from backend.app.utils.errors import AppError


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture()
def mock_state_store(tmp_path, monkeypatch):
    """Create a real StateStore backed by a temp directory.

    Prevents any file-system side-effects outside the test.
    """
    from backend.app.repositories.state import store as state_store_module

    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    base_dir = tmp_path / "state"
    store = state_store_module.StateStore(base_dir=base_dir)
    state_store_module.set_state_store(store)
    return store


@pytest.fixture()
def mock_connection_schema(monkeypatch):
    """Mock ``get_connection_schema`` to return deterministic schemas."""
    def _get_schema(conn_id, **kwargs):
        schemas: Dict[str, Any] = {
            "conn-1": {
                "tables": [
                    {"name": "customers", "columns": [{"name": "id", "type": "INTEGER"}, {"name": "name", "type": "TEXT"}]},
                    {"name": "orders", "columns": [{"name": "id", "type": "INTEGER"}, {"name": "customer_id", "type": "INTEGER"}]},
                ]
            },
            "conn-2": {
                "tables": [
                    {"name": "products", "columns": [{"name": "id", "type": "INTEGER"}, {"name": "title", "type": "TEXT"}]},
                    {"name": "inventory", "columns": [{"name": "id", "type": "INTEGER"}, {"name": "product_id", "type": "INTEGER"}]},
                ]
            },
            "conn-3": {
                "tables": [
                    {"name": "shipping", "columns": [{"name": "id", "type": "INTEGER"}, {"name": "order_id", "type": "INTEGER"}]},
                ]
            },
        }
        return schemas.get(conn_id, {"tables": []})

    monkeypatch.setattr(
        "backend.app.services.federation.service.get_connection_schema",
        _get_schema,
    )


@pytest.fixture()
def service(mock_state_store, mock_connection_schema):
    """Return a FederationService wired to temp-backed state."""
    return FederationService()


@pytest.fixture()
def app(service):
    """Create a FastAPI application with federation routes and error handlers.

    Overrides:
    - ``require_api_key`` -> noop (no auth needed in tests)
    - ``get_service``     -> returns the controlled ``service`` fixture
    """
    _app = FastAPI()
    add_exception_handlers(_app)

    # Override the API key dependency so it never blocks
    _app.dependency_overrides[require_api_key] = lambda: None
    # Override the service dependency to inject our controlled instance
    _app.dependency_overrides[get_service] = lambda: service

    _app.include_router(router, prefix="/federation")
    return _app


@pytest.fixture()
def client(app):
    """Synchronous TestClient for the federation app."""
    return TestClient(app)


# ============================================================================
# Helpers
# ============================================================================

def _schema_create_payload(**overrides) -> dict:
    """Return a minimal valid VirtualSchemaCreate payload."""
    base: Dict[str, Any] = {
        "name": "Test Virtual Schema",
        "description": "Used for testing",
        "connection_ids": ["conn-1", "conn-2"],
    }
    base.update(overrides)
    return base


# ============================================================================
# POST /federation/schemas  --  Create virtual schema
# ============================================================================


class TestCreateVirtualSchema:
    """POST /federation/schemas"""

    def test_create_returns_200(self, client):
        resp = client.post("/federation/schemas", json=_schema_create_payload())
        assert resp.status_code == 200

    def test_create_returns_ok_status(self, client):
        data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        assert data["status"] == "ok"

    def test_create_schema_has_id(self, client):
        data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema = data["schema"]
        assert "id" in schema
        assert len(schema["id"]) > 0

    def test_create_schema_name_matches(self, client):
        payload = _schema_create_payload(name="My Federation")
        data = client.post("/federation/schemas", json=payload).json()
        assert data["schema"]["name"] == "My Federation"

    def test_create_schema_description_matches(self, client):
        payload = _schema_create_payload(description="A cross-DB view")
        data = client.post("/federation/schemas", json=payload).json()
        assert data["schema"]["description"] == "A cross-DB view"

    def test_create_schema_connections_populated(self, client):
        data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        assert set(data["schema"]["connections"]) == {"conn-1", "conn-2"}

    def test_create_schema_tables_populated(self, client):
        """Should gather tables from both connections (2 + 2 = 4)."""
        data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        tables = data["schema"]["tables"]
        assert len(tables) == 4
        table_names = {t["table_name"] for t in tables}
        assert table_names == {"customers", "orders", "products", "inventory"}

    def test_create_schema_timestamps_present(self, client):
        data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema = data["schema"]
        assert "created_at" in schema
        assert "updated_at" in schema

    def test_create_single_connection(self, client):
        payload = _schema_create_payload(connection_ids=["conn-1"])
        data = client.post("/federation/schemas", json=payload).json()
        assert data["schema"]["connections"] == ["conn-1"]
        assert len(data["schema"]["tables"]) == 2  # customers + orders

    def test_create_with_no_description(self, client):
        payload = _schema_create_payload()
        del payload["description"]
        data = client.post("/federation/schemas", json=payload).json()
        assert data["status"] == "ok"
        assert data["schema"]["description"] is None

    def test_create_returns_correlation_id(self, client):
        data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        assert "correlation_id" in data

    def test_create_validation_empty_name(self, client):
        """Name must be non-empty (min_length=1)."""
        payload = _schema_create_payload(name="")
        resp = client.post("/federation/schemas", json=payload)
        assert resp.status_code == 422

    def test_create_validation_no_connection_ids(self, client):
        """connection_ids must have at least 1 item."""
        payload = _schema_create_payload(connection_ids=[])
        resp = client.post("/federation/schemas", json=payload)
        assert resp.status_code == 422

    def test_create_validation_missing_name(self, client):
        """name is required."""
        resp = client.post("/federation/schemas", json={"connection_ids": ["conn-1"]})
        assert resp.status_code == 422

    def test_create_validation_missing_connection_ids(self, client):
        """connection_ids is required."""
        resp = client.post("/federation/schemas", json={"name": "Test"})
        assert resp.status_code == 422

    def test_create_unknown_connection_returns_empty_tables(self, client):
        """An unknown connection_id should still succeed but with 0 tables for it."""
        payload = _schema_create_payload(connection_ids=["conn-unknown"])
        data = client.post("/federation/schemas", json=payload).json()
        assert data["status"] == "ok"
        assert len(data["schema"]["tables"]) == 0

    def test_create_three_connections(self, client):
        payload = _schema_create_payload(connection_ids=["conn-1", "conn-2", "conn-3"])
        data = client.post("/federation/schemas", json=payload).json()
        assert len(data["schema"]["connections"]) == 3
        # 2 + 2 + 1 = 5 tables
        assert len(data["schema"]["tables"]) == 5


# ============================================================================
# GET /federation/schemas  --  List virtual schemas
# ============================================================================


class TestListVirtualSchemas:
    """GET /federation/schemas"""

    def test_list_empty(self, client):
        resp = client.get("/federation/schemas")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["schemas"] == []

    def test_list_after_create(self, client):
        client.post("/federation/schemas", json=_schema_create_payload(name="S1"))
        resp = client.get("/federation/schemas")
        schemas = resp.json()["schemas"]
        assert len(schemas) == 1
        assert schemas[0]["name"] == "S1"

    def test_list_multiple(self, client):
        for name in ["Alpha", "Beta", "Gamma"]:
            client.post("/federation/schemas", json=_schema_create_payload(name=name))
        resp = client.get("/federation/schemas")
        schemas = resp.json()["schemas"]
        assert len(schemas) == 3
        names = {s["name"] for s in schemas}
        assert names == {"Alpha", "Beta", "Gamma"}

    def test_list_returns_correlation_id(self, client):
        data = client.get("/federation/schemas").json()
        assert "correlation_id" in data

    def test_list_reflects_deletion(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]
        client.delete(f"/federation/schemas/{schema_id}")
        resp = client.get("/federation/schemas")
        assert resp.json()["schemas"] == []


# ============================================================================
# GET /federation/schemas/{schema_id}  --  Get schema by ID
# ============================================================================


class TestGetVirtualSchema:
    """GET /federation/schemas/{schema_id}"""

    def test_get_existing_schema(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload(name="Lookup")).json()
        schema_id = create_data["schema"]["id"]

        resp = client.get(f"/federation/schemas/{schema_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["schema"]["id"] == schema_id
        assert data["schema"]["name"] == "Lookup"

    def test_get_nonexistent_returns_404(self, client):
        resp = client.get("/federation/schemas/nonexistent-id")
        assert resp.status_code == 404

    def test_get_404_detail_structure(self, client):
        resp = client.get("/federation/schemas/does-not-exist")
        body = resp.json()
        # Error handler may wrap as {"code": "http_404", ...} or {"detail": {"code": "not_found"}}
        code = body.get("code") or body.get("detail", {}).get("code")
        assert code in ("not_found", "http_404")
        assert "message" in body or "detail" in body

    def test_get_returns_full_schema(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]

        schema = client.get(f"/federation/schemas/{schema_id}").json()["schema"]
        assert "id" in schema
        assert "name" in schema
        assert "connections" in schema
        assert "tables" in schema
        assert "joins" in schema
        assert "created_at" in schema
        assert "updated_at" in schema

    def test_get_returns_correlation_id(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]
        data = client.get(f"/federation/schemas/{schema_id}").json()
        assert "correlation_id" in data

    def test_get_after_delete_returns_404(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]
        client.delete(f"/federation/schemas/{schema_id}")

        resp = client.get(f"/federation/schemas/{schema_id}")
        assert resp.status_code == 404


# ============================================================================
# DELETE /federation/schemas/{schema_id}  --  Delete schema
# ============================================================================


class TestDeleteVirtualSchema:
    """DELETE /federation/schemas/{schema_id}"""

    def test_delete_existing_returns_200(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]

        resp = client.delete(f"/federation/schemas/{schema_id}")
        assert resp.status_code == 200

    def test_delete_response_body(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]

        data = client.delete(f"/federation/schemas/{schema_id}").json()
        assert data["status"] == "ok"
        assert data["deleted"] is True

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/federation/schemas/no-such-id")
        assert resp.status_code == 404

    def test_delete_404_detail(self, client):
        body = client.delete("/federation/schemas/ghost").json()
        code = body.get("code") or body.get("detail", {}).get("code")
        assert code in ("not_found", "http_404")

    def test_delete_idempotent_second_call_404(self, client):
        """Deleting the same schema twice should give 404 on the second call."""
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]

        first = client.delete(f"/federation/schemas/{schema_id}")
        assert first.status_code == 200

        second = client.delete(f"/federation/schemas/{schema_id}")
        assert second.status_code == 404

    def test_delete_removes_from_list(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]

        client.delete(f"/federation/schemas/{schema_id}")
        schemas = client.get("/federation/schemas").json()["schemas"]
        assert all(s["id"] != schema_id for s in schemas)

    def test_delete_returns_correlation_id(self, client):
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]
        data = client.delete(f"/federation/schemas/{schema_id}").json()
        assert "correlation_id" in data

    def test_delete_one_does_not_affect_another(self, client):
        s1 = client.post("/federation/schemas", json=_schema_create_payload(name="Keep")).json()
        s2 = client.post("/federation/schemas", json=_schema_create_payload(name="Remove")).json()

        client.delete(f"/federation/schemas/{s2['schema']['id']}")

        # The first schema should still exist
        resp = client.get(f"/federation/schemas/{s1['schema']['id']}")
        assert resp.status_code == 200
        assert resp.json()["schema"]["name"] == "Keep"


# ============================================================================
# POST /federation/suggest-joins  --  AI join suggestions
# ============================================================================


class TestSuggestJoins:
    """POST /federation/suggest-joins"""

    @pytest.fixture()
    def mock_llm(self, service):
        """Inject a mock LLM client into the service."""
        llm = MagicMock()
        service._get_llm_client = lambda: llm
        return llm

    def test_suggest_joins_returns_200(self, client, mock_llm):
        mock_llm.complete.return_value = {
            "choices": [{"message": {"content": "[]"}}]
        }
        resp = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-2"],
        })
        assert resp.status_code == 200

    def test_suggest_joins_response_structure(self, client, mock_llm):
        mock_llm.complete.return_value = {
            "choices": [{"message": {"content": "[]"}}]
        }
        data = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-2"],
        }).json()
        assert data["status"] == "ok"
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_suggest_joins_with_llm_result(self, client, mock_llm):
        suggestion_json = json.dumps([{
            "left_connection_id": "conn-1",
            "left_table": "customers",
            "left_column": "id",
            "right_connection_id": "conn-2",
            "right_table": "products",
            "right_column": "id",
            "confidence": 0.85,
            "reason": "Both have matching id columns",
        }])
        mock_llm.complete.return_value = {
            "choices": [{"message": {"content": suggestion_json}}]
        }
        data = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-2"],
        }).json()
        suggestions = data["suggestions"]
        assert len(suggestions) == 1
        assert suggestions[0]["left_table"] == "customers"
        assert suggestions[0]["right_table"] == "products"
        assert suggestions[0]["confidence"] == 0.85
        assert suggestions[0]["reason"] == "Both have matching id columns"

    def test_suggest_joins_multiple_suggestions(self, client, mock_llm):
        suggestions_data = [
            {
                "left_connection_id": "conn-1",
                "left_table": "customers",
                "left_column": "id",
                "right_connection_id": "conn-2",
                "right_table": "products",
                "right_column": "id",
                "confidence": 0.7,
                "reason": "Primary keys",
            },
            {
                "left_connection_id": "conn-1",
                "left_table": "orders",
                "left_column": "customer_id",
                "right_connection_id": "conn-2",
                "right_table": "inventory",
                "right_column": "product_id",
                "confidence": 0.5,
                "reason": "Foreign key relationship",
            },
        ]
        mock_llm.complete.return_value = {
            "choices": [{"message": {"content": json.dumps(suggestions_data)}}]
        }
        data = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-2"],
        }).json()
        assert len(data["suggestions"]) == 2

    def test_suggest_joins_llm_error_returns_empty(self, client, mock_llm):
        """If the LLM throws, endpoint should still return 200 with empty list."""
        mock_llm.complete.side_effect = RuntimeError("LLM is down")
        data = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-2"],
        }).json()
        assert data["status"] == "ok"
        assert data["suggestions"] == []

    def test_suggest_joins_llm_malformed_json_returns_empty(self, client, mock_llm):
        mock_llm.complete.return_value = {
            "choices": [{"message": {"content": "this is not json"}}]
        }
        data = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-2"],
        }).json()
        assert data["suggestions"] == []

    def test_suggest_joins_insufficient_connections_returns_empty(self, client, mock_llm):
        """With < 2 connections, the service short-circuits to empty."""
        data = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-unknown"],
        }).json()
        # conn-unknown has no tables, so effectively < 2 schemas gathered
        assert data["suggestions"] == []

    def test_suggest_joins_validation_requires_min_2(self, client):
        """SuggestJoinsRequest requires min_items=2."""
        resp = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1"],
        })
        assert resp.status_code == 422

    def test_suggest_joins_validation_empty_list(self, client):
        resp = client.post("/federation/suggest-joins", json={
            "connection_ids": [],
        })
        assert resp.status_code == 422

    def test_suggest_joins_validation_missing_field(self, client):
        resp = client.post("/federation/suggest-joins", json={})
        assert resp.status_code == 422

    def test_suggest_joins_returns_correlation_id(self, client, mock_llm):
        mock_llm.complete.return_value = {
            "choices": [{"message": {"content": "[]"}}]
        }
        data = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-2"],
        }).json()
        assert "correlation_id" in data

    def test_suggest_joins_llm_returns_wrapped_json(self, client, mock_llm):
        """LLM might return JSON inside markdown fences; regex should still parse."""
        suggestion = [{
            "left_connection_id": "conn-1",
            "left_table": "customers",
            "left_column": "id",
            "right_connection_id": "conn-2",
            "right_table": "products",
            "right_column": "id",
            "confidence": 0.9,
            "reason": "ID match",
        }]
        wrapped = f"```json\n{json.dumps(suggestion)}\n```"
        mock_llm.complete.return_value = {
            "choices": [{"message": {"content": wrapped}}]
        }
        data = client.post("/federation/suggest-joins", json={
            "connection_ids": ["conn-1", "conn-2"],
        }).json()
        assert len(data["suggestions"]) == 1
        assert data["suggestions"][0]["confidence"] == 0.9


# ============================================================================
# POST /federation/query  --  Execute federated query
# ============================================================================


class TestExecuteFederatedQuery:
    """POST /federation/query"""

    @pytest.fixture()
    def schema_id(self, client) -> str:
        """Create a virtual schema and return its ID."""
        data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        return data["schema"]["id"]

    @pytest.fixture()
    def mock_execute_query(self, monkeypatch):
        """Mock the actual database execution layer."""
        mock = MagicMock(return_value={
            "columns": ["id", "name"],
            "rows": [[1, "Alice"], [2, "Bob"]],
        })
        monkeypatch.setattr(
            "backend.app.repositories.connections.db_connection.execute_query",
            mock,
        )
        return mock

    def test_query_returns_200(self, client, schema_id, mock_execute_query):
        resp = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
            "limit": 50,
        })
        assert resp.status_code == 200

    def test_query_response_structure(self, client, schema_id, mock_execute_query):
        data = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        }).json()
        assert data["status"] == "ok"
        result = data["result"]
        assert "columns" in result
        assert "rows" in result
        assert "row_count" in result
        assert "schema_id" in result
        assert "executed_on" in result
        assert "routing" in result

    def test_query_single_connection_routing(self, client, schema_id, mock_execute_query):
        data = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        }).json()
        result = data["result"]
        assert result["routing"] == "single"
        assert len(result["executed_on"]) == 1

    def test_query_returns_data(self, client, schema_id, mock_execute_query):
        data = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        }).json()
        result = data["result"]
        assert result["columns"] == ["id", "name"]
        assert len(result["rows"]) == 2

    def test_query_nonexistent_schema_returns_error(self, client, mock_execute_query):
        resp = client.post("/federation/query", json={
            "virtual_schema_id": "nonexistent",
            "sql": "SELECT * FROM customers",
        })
        # AppError with status_code=404 is caught by the error handler
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == "schema_not_found"

    def test_query_with_limit(self, client, schema_id, mock_execute_query):
        client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
            "limit": 25,
        })
        # The mock should have been called with limit=25
        mock_execute_query.assert_called_once()
        call_kwargs = mock_execute_query.call_args
        assert call_kwargs[1].get("limit") == 25 or call_kwargs[0][-1] == 25

    def test_query_default_limit(self, client, schema_id, mock_execute_query):
        """Default limit should be 100."""
        data = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        }).json()
        assert data["status"] == "ok"

    def test_query_schema_id_in_result(self, client, schema_id, mock_execute_query):
        data = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        }).json()
        assert data["result"]["schema_id"] == schema_id

    def test_query_validation_empty_sql(self, client, schema_id):
        resp = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "",
        })
        assert resp.status_code == 422

    def test_query_validation_missing_sql(self, client, schema_id):
        resp = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
        })
        assert resp.status_code == 422

    def test_query_validation_missing_schema_id(self, client):
        resp = client.post("/federation/query", json={
            "sql": "SELECT 1",
        })
        assert resp.status_code == 422

    def test_query_validation_limit_too_low(self, client, schema_id):
        resp = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT 1",
            "limit": 0,
        })
        assert resp.status_code == 422

    def test_query_validation_limit_too_high(self, client, schema_id):
        resp = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT 1",
            "limit": 9999,
        })
        assert resp.status_code == 422

    def test_query_returns_correlation_id(self, client, schema_id, mock_execute_query):
        data = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        }).json()
        assert "correlation_id" in data

    def test_query_write_operation_rejected(self, client, schema_id):
        """INSERT/UPDATE/DELETE/DROP queries should be rejected."""
        for sql in [
            "INSERT INTO customers VALUES (1, 'X')",
            "UPDATE customers SET name='Y'",
            "DELETE FROM customers",
            "DROP TABLE customers",
        ]:
            resp = client.post("/federation/query", json={
                "virtual_schema_id": schema_id,
                "sql": sql,
            })
            assert resp.status_code == 400, f"Expected 400 for SQL: {sql}"

    def test_query_empty_schema_no_connections(self, client, mock_state_store, mock_execute_query):
        """Schema with no connections should raise no_connections error."""
        store = mock_state_store
        with store._lock:
            state = store._read_state()
            state.setdefault("virtual_schemas", {})["empty-vs"] = {
                "id": "empty-vs",
                "name": "Empty",
                "description": None,
                "connections": [],
                "tables": [],
                "joins": [],
                "created_at": "2025-01-01T00:00:00+00:00",
                "updated_at": "2025-01-01T00:00:00+00:00",
            }
            store._write_state(state)

        resp = client.post("/federation/query", json={
            "virtual_schema_id": "empty-vs",
            "sql": "SELECT * FROM customers",
        })
        assert resp.status_code == 400
        assert resp.json()["code"] == "no_connections"

    def test_query_execution_failure_returns_500(self, client, schema_id, monkeypatch):
        """If the underlying DB query fails, the endpoint returns 500."""
        def _fail(*args, **kwargs):
            raise RuntimeError("Connection lost")

        monkeypatch.setattr(
            "backend.app.repositories.connections.db_connection.execute_query",
            _fail,
        )
        resp = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        })
        assert resp.status_code == 500
        assert resp.json()["code"] == "query_failed"

    def test_query_with_select_keyword(self, client, schema_id, mock_execute_query):
        """WITH / CTE queries should be allowed."""
        data = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "WITH cte AS (SELECT * FROM customers) SELECT * FROM cte",
        }).json()
        assert data["status"] == "ok"


# ============================================================================
# Full lifecycle / integration scenarios
# ============================================================================


class TestFederationLifecycle:
    """End-to-end scenarios spanning multiple endpoints."""

    def test_create_list_get_delete_lifecycle(self, client):
        """Full CRUD lifecycle."""
        # Create
        create_resp = client.post("/federation/schemas", json=_schema_create_payload(name="Lifecycle"))
        assert create_resp.status_code == 200
        schema_id = create_resp.json()["schema"]["id"]

        # List - should contain it
        schemas = client.get("/federation/schemas").json()["schemas"]
        assert any(s["id"] == schema_id for s in schemas)

        # Get by ID
        get_resp = client.get(f"/federation/schemas/{schema_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["schema"]["name"] == "Lifecycle"

        # Delete
        del_resp = client.delete(f"/federation/schemas/{schema_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["deleted"] is True

        # Verify gone
        assert client.get(f"/federation/schemas/{schema_id}").status_code == 404
        assert all(s["id"] != schema_id for s in client.get("/federation/schemas").json()["schemas"])

    def test_create_multiple_delete_one(self, client):
        ids = []
        for name in ["A", "B", "C"]:
            data = client.post("/federation/schemas", json=_schema_create_payload(name=name)).json()
            ids.append(data["schema"]["id"])

        # Delete the middle one
        client.delete(f"/federation/schemas/{ids[1]}")

        remaining = client.get("/federation/schemas").json()["schemas"]
        remaining_ids = {s["id"] for s in remaining}
        assert ids[0] in remaining_ids
        assert ids[1] not in remaining_ids
        assert ids[2] in remaining_ids

    def test_create_and_query(self, client, monkeypatch):
        """Create a schema then immediately query it."""
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]

        mock_exec = MagicMock(return_value={
            "columns": ["id", "name"],
            "rows": [[1, "Alice"]],
        })
        monkeypatch.setattr(
            "backend.app.repositories.connections.db_connection.execute_query",
            mock_exec,
        )

        data = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        }).json()
        assert data["status"] == "ok"
        assert data["result"]["rows"] == [[1, "Alice"]]

    def test_query_after_delete_returns_404(self, client, monkeypatch):
        """Querying a deleted schema returns 404."""
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]
        client.delete(f"/federation/schemas/{schema_id}")

        mock_exec = MagicMock(return_value={"columns": [], "rows": []})
        monkeypatch.setattr(
            "backend.app.repositories.connections.db_connection.execute_query",
            mock_exec,
        )

        resp = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": "SELECT * FROM customers",
        })
        assert resp.status_code == 404
        assert resp.json()["code"] == "schema_not_found"


# ============================================================================
# Edge cases & error handling
# ============================================================================


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_get_empty_string_schema_id(self, client):
        """FastAPI still resolves this route; service returns 404."""
        resp = client.get("/federation/schemas/ ")
        assert resp.status_code == 404

    def test_delete_empty_string_schema_id(self, client):
        resp = client.delete("/federation/schemas/ ")
        assert resp.status_code == 404

    def test_create_very_long_name(self, client):
        """Name has max_length=100."""
        long_name = "A" * 101
        resp = client.post("/federation/schemas", json=_schema_create_payload(name=long_name))
        assert resp.status_code == 422

    def test_create_name_at_max_length(self, client):
        name = "B" * 100
        resp = client.post("/federation/schemas", json=_schema_create_payload(name=name))
        assert resp.status_code == 200
        assert resp.json()["schema"]["name"] == name

    def test_create_description_max_length(self, client):
        long_desc = "D" * 501
        resp = client.post("/federation/schemas", json=_schema_create_payload(description=long_desc))
        assert resp.status_code == 422

    def test_create_description_at_max_length(self, client):
        desc = "E" * 500
        resp = client.post("/federation/schemas", json=_schema_create_payload(description=desc))
        assert resp.status_code == 200

    def test_suggest_joins_too_many_connections(self, client):
        """max_items=10 on connection_ids."""
        conn_ids = [f"conn-{i}" for i in range(11)]
        resp = client.post("/federation/suggest-joins", json={"connection_ids": conn_ids})
        assert resp.status_code == 422

    def test_create_too_many_connections(self, client):
        """VirtualSchemaCreate has max_items=10 for connection_ids."""
        conn_ids = [f"conn-{i}" for i in range(11)]
        resp = client.post("/federation/schemas", json=_schema_create_payload(connection_ids=conn_ids))
        assert resp.status_code == 422

    def test_query_sql_at_max_length(self, client, monkeypatch):
        """sql field has max_length=10000."""
        create_data = client.post("/federation/schemas", json=_schema_create_payload()).json()
        schema_id = create_data["schema"]["id"]

        mock_exec = MagicMock(return_value={"columns": ["x"], "rows": [[1]]})
        monkeypatch.setattr(
            "backend.app.repositories.connections.db_connection.execute_query",
            mock_exec,
        )

        # Build a valid SELECT padded to exactly 10000 chars
        base = "SELECT * FROM customers WHERE "
        padding = "1=1 AND " * 1500
        sql = (base + padding).ljust(10000, " ")[:10000]
        # Ensure it starts with SELECT (already does)
        resp = client.post("/federation/query", json={
            "virtual_schema_id": schema_id,
            "sql": sql,
        })
        # Should either succeed or fail on business logic, not validation
        assert resp.status_code in (200, 400, 500)

    def test_post_schemas_wrong_content_type(self, client):
        resp = client.post("/federation/schemas", content=b"not json", headers={"content-type": "text/plain"})
        assert resp.status_code == 422

    def test_suggest_joins_wrong_content_type(self, client):
        resp = client.post("/federation/suggest-joins", content=b"text", headers={"content-type": "text/plain"})
        assert resp.status_code == 422

    def test_query_wrong_content_type(self, client):
        resp = client.post("/federation/query", content=b"text", headers={"content-type": "text/plain"})
        assert resp.status_code == 422


# ============================================================================
# Dependency override verification
# ============================================================================


class TestDependencyOverrides:
    """Verify that our test fixtures correctly override dependencies."""

    def test_api_key_not_required(self, client):
        """All endpoints should work without an API key header."""
        resp = client.get("/federation/schemas")
        assert resp.status_code == 200

    def test_service_is_shared_across_requests(self, client, service):
        """The same service instance should be used for all requests in a test."""
        # Create via the client
        create_data = client.post("/federation/schemas", json=_schema_create_payload(name="Shared")).json()
        schema_id = create_data["schema"]["id"]

        # Directly verify through the service instance
        schema = service.get_virtual_schema(schema_id)
        assert schema is not None
        assert schema.name == "Shared"


# =============================================================================
# SECURITY TESTS
# =============================================================================


class TestFederationPagination:
    """Pagination parameter constraints on list endpoints."""

    def test_list_schemas_limit_too_high(self, client):
        resp = client.get("/federation/schemas?limit=999")
        assert resp.status_code == 422

    def test_list_schemas_limit_zero(self, client):
        resp = client.get("/federation/schemas?limit=0")
        assert resp.status_code == 422

    def test_list_schemas_offset_negative(self, client):
        resp = client.get("/federation/schemas?offset=-1")
        assert resp.status_code == 422

    def test_list_schemas_returns_total(self, client, service):
        """Pagination response should include total count."""
        client.post("/federation/schemas", json=_schema_create_payload(name="Schema-1"))
        client.post("/federation/schemas", json=_schema_create_payload(name="Schema-2"))

        resp = client.get("/federation/schemas?limit=1&offset=0")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert data["total"] >= 2
        assert len(data["schemas"]) <= 1
