"""
Tests for connector registry functionality.

Tests connector registration, factory creation, and listing.
"""
import pytest
from typing import Any

from backend.app.services.connectors.base import (
    ConnectorBase,
    ConnectorType,
    AuthType,
    ConnectorCapability,
    ConnectionTest,
    SchemaInfo,
)
from backend.app.services.connectors.registry import (
    CONNECTOR_REGISTRY,
    register_connector,
    get_connector,
    list_connectors,
    get_connector_info,
    list_connectors_by_type,
)


# =============================================================================
# Mock Connector for Testing
# =============================================================================

class MockTestConnector(ConnectorBase):
    """Mock connector for testing registry."""

    connector_id = "mock_test"
    connector_name = "Mock Test Connector"
    connector_type = ConnectorType.DATABASE
    auth_types = [AuthType.BASIC]
    capabilities = [ConnectorCapability.READ, ConnectorCapability.QUERY]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._test_value = config.get("test_value", "default")

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        return ConnectionTest(success=True, latency_ms=1.0)

    async def discover_schema(self) -> SchemaInfo:
        return SchemaInfo(tables=[], views=[], schemas=[])

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_value": {"type": "string"},
            },
        }


# =============================================================================
# Registration Tests
# =============================================================================

class TestConnectorRegistration:
    """Tests for connector registration."""

    def test_register_connector_decorator(self):
        """@register_connector should add connector to registry."""
        # Create a unique connector for this test
        @register_connector
        class UniqueConnector(ConnectorBase):
            connector_id = "unique_test_connector"
            connector_name = "Unique Test"
            connector_type = ConnectorType.DATABASE
            auth_types = [AuthType.NONE]
            capabilities = [ConnectorCapability.READ]
            free_tier = True

            async def connect(self) -> bool:
                return True

            async def disconnect(self) -> None:
                pass

            async def test_connection(self) -> ConnectionTest:
                return ConnectionTest(success=True, latency_ms=1.0)

            async def discover_schema(self) -> SchemaInfo:
                return SchemaInfo(tables=[])

            @classmethod
            def get_config_schema(cls) -> dict[str, Any]:
                return {}

        assert "unique_test_connector" in CONNECTOR_REGISTRY
        assert CONNECTOR_REGISTRY["unique_test_connector"] == UniqueConnector

        # Cleanup
        del CONNECTOR_REGISTRY["unique_test_connector"]

    def test_register_connector_without_id_raises(self):
        """Registering connector without connector_id should raise."""

        class NoIdConnector(ConnectorBase):
            connector_id = ""  # Empty ID
            connector_name = "No ID"
            connector_type = ConnectorType.DATABASE
            auth_types = []
            capabilities = []

        with pytest.raises(ValueError, match="must have a connector_id"):
            register_connector(NoIdConnector)

    def test_register_connector_overwrites_existing(self):
        """Re-registering same ID should overwrite."""
        @register_connector
        class First(ConnectorBase):
            connector_id = "overwrite_test"
            connector_name = "First"
            connector_type = ConnectorType.DATABASE
            auth_types = []
            capabilities = []
            free_tier = True

            async def connect(self): return True
            async def disconnect(self): pass
            async def test_connection(self): return ConnectionTest(success=True, latency_ms=1.0)
            async def discover_schema(self): return SchemaInfo(tables=[])
            @classmethod
            def get_config_schema(cls): return {}

        @register_connector
        class Second(ConnectorBase):
            connector_id = "overwrite_test"
            connector_name = "Second"
            connector_type = ConnectorType.DATABASE
            auth_types = []
            capabilities = []
            free_tier = True

            async def connect(self): return True
            async def disconnect(self): pass
            async def test_connection(self): return ConnectionTest(success=True, latency_ms=1.0)
            async def discover_schema(self): return SchemaInfo(tables=[])
            @classmethod
            def get_config_schema(cls): return {}

        assert CONNECTOR_REGISTRY["overwrite_test"].connector_name == "Second"

        # Cleanup
        del CONNECTOR_REGISTRY["overwrite_test"]


# =============================================================================
# Factory Tests
# =============================================================================

class TestConnectorFactory:
    """Tests for connector factory function."""

    def test_get_connector_creates_instance(self):
        """get_connector should create configured instance."""
        # First register our mock
        CONNECTOR_REGISTRY["mock_test"] = MockTestConnector

        config = {"test_value": "custom_value"}
        connector = get_connector("mock_test", config)

        assert isinstance(connector, MockTestConnector)
        assert connector._test_value == "custom_value"

        # Cleanup
        del CONNECTOR_REGISTRY["mock_test"]

    def test_get_connector_unknown_raises(self):
        """get_connector with unknown ID should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown connector"):
            get_connector("nonexistent_connector", {})

    def test_get_connector_error_shows_available(self):
        """Error message should list available connectors."""
        try:
            get_connector("bad_id", {})
        except ValueError as e:
            error_msg = str(e)
            assert "Available:" in error_msg


# =============================================================================
# Listing Tests
# =============================================================================

class TestConnectorListing:
    """Tests for connector listing functions."""

    def test_list_connectors_returns_list(self):
        """list_connectors should return list of connector info."""
        connectors = list_connectors()
        assert isinstance(connectors, list)

        # Each item should be a dict with expected keys
        for conn_info in connectors:
            assert "id" in conn_info
            assert "name" in conn_info
            assert "type" in conn_info

    def test_get_connector_info_returns_info(self):
        """get_connector_info should return info for valid ID."""
        # Use a known registered connector
        if "postgresql" in CONNECTOR_REGISTRY:
            info = get_connector_info("postgresql")
            assert info is not None
            assert info["id"] == "postgresql"
            assert "name" in info

    def test_get_connector_info_unknown_returns_none(self):
        """get_connector_info with unknown ID should return None."""
        info = get_connector_info("definitely_not_a_real_connector")
        assert info is None

    def test_list_connectors_by_type(self):
        """list_connectors_by_type should filter correctly."""
        database_connectors = list_connectors_by_type("database")

        for conn_info in database_connectors:
            assert conn_info["type"] == "database"


# =============================================================================
# Registered Connector Verification
# =============================================================================

class TestRegisteredConnectors:
    """Verify all expected connectors are registered."""

    def test_postgresql_registered(self):
        """PostgreSQL connector should be registered."""
        assert "postgresql" in CONNECTOR_REGISTRY

    def test_mysql_registered(self):
        """MySQL connector should be registered."""
        assert "mysql" in CONNECTOR_REGISTRY

    def test_mongodb_registered(self):
        """MongoDB connector should be registered."""
        assert "mongodb" in CONNECTOR_REGISTRY

    def test_sqlserver_registered(self):
        """SQL Server connector should be registered."""
        assert "sqlserver" in CONNECTOR_REGISTRY

    def test_bigquery_registered(self):
        """BigQuery connector should be registered."""
        assert "bigquery" in CONNECTOR_REGISTRY

    def test_snowflake_registered(self):
        """Snowflake connector should be registered."""
        assert "snowflake" in CONNECTOR_REGISTRY

    def test_elasticsearch_registered(self):
        """Elasticsearch connector should be registered."""
        assert "elasticsearch" in CONNECTOR_REGISTRY

    def test_duckdb_registered(self):
        """DuckDB connector should be registered."""
        assert "duckdb" in CONNECTOR_REGISTRY

    def test_all_8_database_connectors_registered(self):
        """All 8 database connectors should be registered."""
        expected_connectors = [
            "postgresql",
            "mysql",
            "mongodb",
            "sqlserver",
            "bigquery",
            "snowflake",
            "elasticsearch",
            "duckdb",
        ]

        for connector_id in expected_connectors:
            assert connector_id in CONNECTOR_REGISTRY, f"Missing: {connector_id}"


# =============================================================================
# Connector Info Validation
# =============================================================================

class TestConnectorInfo:
    """Tests for connector info structure."""

    def test_connector_info_has_required_fields(self):
        """Connector info should have all required fields."""
        connectors = list_connectors()

        required_fields = ["id", "name", "type", "auth_types", "capabilities"]

        for conn_info in connectors:
            for field in required_fields:
                assert field in conn_info, f"Missing {field} in {conn_info.get('id')}"

    def test_connector_has_config_schema(self):
        """Each connector should have a config schema."""
        for connector_id, connector_class in CONNECTOR_REGISTRY.items():
            schema = connector_class.get_config_schema()
            assert isinstance(schema, dict), f"{connector_id} config schema not dict"

    def test_connector_has_valid_type(self):
        """Each connector should have valid ConnectorType."""
        for connector_id, connector_class in CONNECTOR_REGISTRY.items():
            assert hasattr(connector_class, "connector_type")
            assert isinstance(connector_class.connector_type, ConnectorType)
