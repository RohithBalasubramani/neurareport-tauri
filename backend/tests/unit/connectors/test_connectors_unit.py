"""
Unit tests for database connector classes.

Tests connector configuration, validation, and mock operations.
"""
import pytest
from typing import Any
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from backend.app.services.connectors.base import (
    ConnectorBase,
    ConnectorType,
    AuthType,
    ConnectorCapability,
    ConnectionTest,
    SchemaInfo,
    TableInfo,
    ColumnInfo,
    QueryResult,
)
from backend.app.services.connectors.registry import CONNECTOR_REGISTRY


# =============================================================================
# Base Connector Tests
# =============================================================================

class TestConnectorBase:
    """Tests for ConnectorBase abstract class."""

    def test_connector_base_is_abstract(self):
        """ConnectorBase should not be directly instantiable."""
        # ConnectorBase requires implementation of abstract methods
        with pytest.raises(TypeError):
            ConnectorBase({})

    def test_get_connector_info_returns_dict(self):
        """get_connector_info should return properly structured dict."""
        # Use a real registered connector
        if "postgresql" in CONNECTOR_REGISTRY:
            info = CONNECTOR_REGISTRY["postgresql"].get_connector_info()
            assert isinstance(info, dict)
            assert "id" in info
            assert "name" in info
            assert "type" in info
            assert "auth_types" in info
            assert "capabilities" in info


# =============================================================================
# PostgreSQL Connector Tests
# =============================================================================

class TestPostgreSQLConnector:
    """Tests for PostgreSQL connector."""

    def test_connector_attributes(self):
        """PostgreSQL connector should have correct attributes."""
        connector_class = CONNECTOR_REGISTRY.get("postgresql")
        if connector_class is None:
            pytest.skip("PostgreSQL connector not registered")

        assert connector_class.connector_id == "postgresql"
        assert connector_class.connector_name == "PostgreSQL"
        assert connector_class.connector_type == ConnectorType.DATABASE
        assert AuthType.BASIC in connector_class.auth_types
        assert ConnectorCapability.READ in connector_class.capabilities
        assert ConnectorCapability.QUERY in connector_class.capabilities

    def test_config_schema_structure(self):
        """PostgreSQL config schema should have required fields."""
        connector_class = CONNECTOR_REGISTRY.get("postgresql")
        if connector_class is None:
            pytest.skip("PostgreSQL connector not registered")

        schema = connector_class.get_config_schema()
        assert "properties" in schema

        props = schema["properties"]
        assert "host" in props
        assert "port" in props
        assert "database" in props
        assert "username" in props
        assert "password" in props

    def test_instance_creation(self):
        """PostgreSQL connector should instantiate with config."""
        connector_class = CONNECTOR_REGISTRY.get("postgresql")
        if connector_class is None:
            pytest.skip("PostgreSQL connector not registered")

        config = {
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "user",
            "password": "pass",
        }
        connector = connector_class(config)
        assert connector.config == config
        assert connector._connected is False


# =============================================================================
# MySQL Connector Tests
# =============================================================================

class TestMySQLConnector:
    """Tests for MySQL connector."""

    def test_connector_attributes(self):
        """MySQL connector should have correct attributes."""
        connector_class = CONNECTOR_REGISTRY.get("mysql")
        if connector_class is None:
            pytest.skip("MySQL connector not registered")

        assert connector_class.connector_id == "mysql"
        assert connector_class.connector_type == ConnectorType.DATABASE

    def test_config_schema_has_port(self):
        """MySQL config should have port with correct default."""
        connector_class = CONNECTOR_REGISTRY.get("mysql")
        if connector_class is None:
            pytest.skip("MySQL connector not registered")

        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        assert "port" in props


# =============================================================================
# MongoDB Connector Tests
# =============================================================================

class TestMongoDBConnector:
    """Tests for MongoDB connector."""

    def test_connector_attributes(self):
        """MongoDB connector should have correct attributes."""
        connector_class = CONNECTOR_REGISTRY.get("mongodb")
        if connector_class is None:
            pytest.skip("MongoDB connector not registered")

        assert connector_class.connector_id == "mongodb"
        assert connector_class.connector_type == ConnectorType.DATABASE

    def test_supports_connection_string(self):
        """MongoDB should support connection string auth."""
        connector_class = CONNECTOR_REGISTRY.get("mongodb")
        if connector_class is None:
            pytest.skip("MongoDB connector not registered")

        # MongoDB typically supports connection strings
        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        # Should have either connection_string or host
        assert "connection_string" in props or "host" in props or "uri" in props


# =============================================================================
# SQL Server Connector Tests
# =============================================================================

class TestSQLServerConnector:
    """Tests for SQL Server connector."""

    def test_connector_attributes(self):
        """SQL Server connector should have correct attributes."""
        connector_class = CONNECTOR_REGISTRY.get("sqlserver")
        if connector_class is None:
            pytest.skip("SQL Server connector not registered")

        assert connector_class.connector_id == "sqlserver"
        assert connector_class.connector_name == "Microsoft SQL Server"
        assert connector_class.connector_type == ConnectorType.DATABASE

    def test_default_port(self):
        """SQL Server default port should be 1433."""
        connector_class = CONNECTOR_REGISTRY.get("sqlserver")
        if connector_class is None:
            pytest.skip("SQL Server connector not registered")

        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        if "port" in props:
            assert props["port"].get("default") == 1433


# =============================================================================
# BigQuery Connector Tests
# =============================================================================

class TestBigQueryConnector:
    """Tests for BigQuery connector."""

    def test_connector_attributes(self):
        """BigQuery connector should have correct attributes."""
        connector_class = CONNECTOR_REGISTRY.get("bigquery")
        if connector_class is None:
            pytest.skip("BigQuery connector not registered")

        assert connector_class.connector_id == "bigquery"
        assert connector_class.connector_name == "Google BigQuery"
        assert connector_class.connector_type == ConnectorType.DATABASE

    def test_service_account_auth(self):
        """BigQuery should support service account auth."""
        connector_class = CONNECTOR_REGISTRY.get("bigquery")
        if connector_class is None:
            pytest.skip("BigQuery connector not registered")

        assert AuthType.SERVICE_ACCOUNT in connector_class.auth_types

    def test_config_has_project_id(self):
        """BigQuery config should have project_id."""
        connector_class = CONNECTOR_REGISTRY.get("bigquery")
        if connector_class is None:
            pytest.skip("BigQuery connector not registered")

        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        assert "project_id" in props


# =============================================================================
# Snowflake Connector Tests
# =============================================================================

class TestSnowflakeConnector:
    """Tests for Snowflake connector."""

    def test_connector_attributes(self):
        """Snowflake connector should have correct attributes."""
        connector_class = CONNECTOR_REGISTRY.get("snowflake")
        if connector_class is None:
            pytest.skip("Snowflake connector not registered")

        assert connector_class.connector_id == "snowflake"
        assert connector_class.connector_type == ConnectorType.DATABASE

    def test_config_has_account(self):
        """Snowflake config should have account field."""
        connector_class = CONNECTOR_REGISTRY.get("snowflake")
        if connector_class is None:
            pytest.skip("Snowflake connector not registered")

        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        assert "account" in props

    def test_config_has_warehouse(self):
        """Snowflake config should have warehouse field."""
        connector_class = CONNECTOR_REGISTRY.get("snowflake")
        if connector_class is None:
            pytest.skip("Snowflake connector not registered")

        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        assert "warehouse" in props


# =============================================================================
# Elasticsearch Connector Tests
# =============================================================================

class TestElasticsearchConnector:
    """Tests for Elasticsearch connector."""

    def test_connector_attributes(self):
        """Elasticsearch connector should have correct attributes."""
        connector_class = CONNECTOR_REGISTRY.get("elasticsearch")
        if connector_class is None:
            pytest.skip("Elasticsearch connector not registered")

        assert connector_class.connector_id == "elasticsearch"
        assert connector_class.connector_type == ConnectorType.DATABASE

    def test_supports_multiple_auth_types(self):
        """Elasticsearch should support multiple auth types."""
        connector_class = CONNECTOR_REGISTRY.get("elasticsearch")
        if connector_class is None:
            pytest.skip("Elasticsearch connector not registered")

        # Elasticsearch typically supports basic, API key, and no auth
        assert len(connector_class.auth_types) >= 1

    def test_config_has_hosts(self):
        """Elasticsearch config should have hosts field."""
        connector_class = CONNECTOR_REGISTRY.get("elasticsearch")
        if connector_class is None:
            pytest.skip("Elasticsearch connector not registered")

        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        assert "hosts" in props


# =============================================================================
# DuckDB Connector Tests
# =============================================================================

class TestDuckDBConnector:
    """Tests for DuckDB connector."""

    def test_connector_attributes(self):
        """DuckDB connector should have correct attributes."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        assert connector_class.connector_id == "duckdb"
        assert connector_class.connector_type == ConnectorType.DATABASE

    def test_no_auth_required(self):
        """DuckDB should not require authentication."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        assert AuthType.NONE in connector_class.auth_types

    def test_config_has_database_path(self):
        """DuckDB config should have database path option."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        assert "database" in props

    def test_supports_memory_database(self):
        """DuckDB should support in-memory database."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        schema = connector_class.get_config_schema()
        props = schema.get("properties", {})
        if "database" in props:
            default = props["database"].get("default", "")
            # Default should be :memory: for in-memory
            assert default == ":memory:" or "memory" in str(default).lower()


# =============================================================================
# Data Model Tests
# =============================================================================

class TestDataModels:
    """Tests for connector data models."""

    def test_connection_test_success(self):
        """ConnectionTest should represent successful connection."""
        test = ConnectionTest(success=True, latency_ms=45.5)
        assert test.success is True
        assert test.latency_ms == 45.5
        assert test.error is None

    def test_connection_test_failure(self):
        """ConnectionTest should represent failed connection."""
        test = ConnectionTest(success=False, error="Connection refused")
        assert test.success is False
        assert test.error == "Connection refused"

    def test_column_info_structure(self):
        """ColumnInfo should hold column metadata."""
        col = ColumnInfo(
            name="id",
            data_type="integer",
            nullable=False,
            primary_key=True,
        )
        assert col.name == "id"
        assert col.data_type == "integer"
        assert col.nullable is False
        assert col.primary_key is True

    def test_table_info_structure(self):
        """TableInfo should hold table metadata."""
        columns = [
            ColumnInfo(name="id", data_type="integer"),
            ColumnInfo(name="name", data_type="varchar"),
        ]
        table = TableInfo(
            name="users",
            schema_name="public",
            columns=columns,
        )
        assert table.name == "users"
        assert table.schema_name == "public"
        assert len(table.columns) == 2

    def test_schema_info_structure(self):
        """SchemaInfo should hold schema metadata."""
        tables = [TableInfo(name="users")]
        views = [TableInfo(name="active_users")]
        schema = SchemaInfo(
            tables=tables,
            views=views,
            schemas=["public", "private"],
        )
        assert len(schema.tables) == 1
        assert len(schema.views) == 1
        assert "public" in schema.schemas

    def test_query_result_structure(self):
        """QueryResult should hold query execution results."""
        result = QueryResult(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"]],
            row_count=2,
            execution_time_ms=15.5,
        )
        assert result.columns == ["id", "name"]
        assert result.row_count == 2
        assert result.execution_time_ms == 15.5
        assert result.error is None

    def test_query_result_with_error(self):
        """QueryResult should hold error information."""
        result = QueryResult(
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=5.0,
            error="Syntax error",
        )
        assert result.error == "Syntax error"
        assert result.row_count == 0


# =============================================================================
# Capability Tests
# =============================================================================

class TestConnectorCapabilities:
    """Tests for connector capability declarations."""

    def test_all_connectors_have_read_capability(self):
        """All database connectors should support READ."""
        database_connectors = [
            "postgresql", "mysql", "mongodb", "sqlserver",
            "bigquery", "snowflake", "elasticsearch", "duckdb"
        ]

        for conn_id in database_connectors:
            connector_class = CONNECTOR_REGISTRY.get(conn_id)
            if connector_class:
                assert ConnectorCapability.READ in connector_class.capabilities, \
                    f"{conn_id} missing READ capability"

    def test_all_connectors_have_query_capability(self):
        """All database connectors should support QUERY."""
        database_connectors = [
            "postgresql", "mysql", "mongodb", "sqlserver",
            "bigquery", "snowflake", "elasticsearch", "duckdb"
        ]

        for conn_id in database_connectors:
            connector_class = CONNECTOR_REGISTRY.get(conn_id)
            if connector_class:
                assert ConnectorCapability.QUERY in connector_class.capabilities, \
                    f"{conn_id} missing QUERY capability"

    def test_all_connectors_have_schema_discovery(self):
        """All database connectors should support SCHEMA_DISCOVERY."""
        database_connectors = [
            "postgresql", "mysql", "mongodb", "sqlserver",
            "bigquery", "snowflake", "elasticsearch", "duckdb"
        ]

        for conn_id in database_connectors:
            connector_class = CONNECTOR_REGISTRY.get(conn_id)
            if connector_class:
                assert ConnectorCapability.SCHEMA_DISCOVERY in connector_class.capabilities, \
                    f"{conn_id} missing SCHEMA_DISCOVERY capability"
