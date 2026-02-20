"""
Integration tests for database connectors.

Tests end-to-end connector functionality with mock databases.
"""
import pytest
import asyncio
from typing import Any
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from backend.app.services.connectors.base import (
    ConnectionTest,
    SchemaInfo,
    TableInfo,
    ColumnInfo,
    QueryResult,
)
from backend.app.services.connectors.registry import CONNECTOR_REGISTRY, get_connector
from backend.app.services.connectors.resilience import (
    with_retry,
    ConnectionHealth,
)


# =============================================================================
# DuckDB Integration Tests (Real In-Memory DB)
# =============================================================================

class TestDuckDBIntegration:
    """Integration tests with real DuckDB in-memory database."""

    @pytest.fixture
    def duckdb_connector(self):
        """Create DuckDB connector with in-memory database."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        config = {"database": ":memory:"}
        return connector_class(config)

    @pytest.mark.asyncio
    async def test_duckdb_connect_disconnect(self, duckdb_connector):
        """Test basic connect/disconnect cycle."""
        try:
            result = await duckdb_connector.connect()
            assert result is True
            assert duckdb_connector._connected is True
        finally:
            await duckdb_connector.disconnect()
            assert duckdb_connector._connected is False

    @pytest.mark.asyncio
    async def test_duckdb_test_connection(self, duckdb_connector):
        """Test connection test returns valid result."""
        try:
            test_result = await duckdb_connector.test_connection()
            assert isinstance(test_result, ConnectionTest)
            assert test_result.success is True
            assert test_result.latency_ms >= 0
        finally:
            await duckdb_connector.disconnect()

    @pytest.mark.asyncio
    async def test_duckdb_execute_query(self, duckdb_connector):
        """Test query execution."""
        try:
            await duckdb_connector.connect()

            # Execute a simple query
            result = await duckdb_connector.execute_query("SELECT 1 as num, 'hello' as str")

            assert isinstance(result, QueryResult)
            assert result.error is None
            assert result.row_count >= 1
            assert "num" in result.columns or "str" in result.columns
        finally:
            await duckdb_connector.disconnect()

    @pytest.mark.asyncio
    async def test_duckdb_schema_discovery(self, duckdb_connector):
        """Test schema discovery."""
        try:
            await duckdb_connector.connect()

            # Create a test table
            await duckdb_connector.execute_query(
                "CREATE TABLE test_table (id INTEGER, name VARCHAR)"
            )

            schema = await duckdb_connector.discover_schema()

            assert isinstance(schema, SchemaInfo)
            # Should find our test table
            table_names = [t.name for t in schema.tables]
            assert "test_table" in table_names
        finally:
            await duckdb_connector.disconnect()

    @pytest.mark.asyncio
    async def test_duckdb_query_with_limit(self, duckdb_connector):
        """Test query limit is applied."""
        try:
            await duckdb_connector.connect()

            # Create table with multiple rows
            await duckdb_connector.execute_query(
                "CREATE TABLE numbers AS SELECT * FROM range(100) t(n)"
            )

            # Query with limit
            result = await duckdb_connector.execute_query(
                "SELECT * FROM numbers",
                limit=10
            )

            assert result.row_count <= 10
        finally:
            await duckdb_connector.disconnect()


# =============================================================================
# Connector Lifecycle Tests
# =============================================================================

class TestConnectorLifecycle:
    """Tests for connector lifecycle management."""

    @pytest.mark.asyncio
    async def test_multiple_connect_disconnect_cycles(self):
        """Test multiple connect/disconnect cycles."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})

        for i in range(3):
            await connector.connect()
            assert connector._connected is True

            result = await connector.test_connection()
            assert result.success is True

            await connector.disconnect()
            assert connector._connected is False

    @pytest.mark.asyncio
    async def test_query_auto_connects(self):
        """Test that query auto-connects if not connected."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})

        # Don't explicitly connect - query should auto-connect
        try:
            result = await connector.execute_query("SELECT 1")
            assert result.error is None
            assert connector._connected is True
        finally:
            await connector.disconnect()


# =============================================================================
# Health Tracking Integration Tests
# =============================================================================

class TestHealthTrackingIntegration:
    """Integration tests for health tracking with real operations."""

    @pytest.mark.asyncio
    async def test_health_tracks_successful_queries(self):
        """Health should track successful query operations."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})
        health = ConnectionHealth()

        try:
            await connector.connect()

            for i in range(5):
                result = await connector.execute_query(f"SELECT {i}")
                if result.error is None:
                    health.record_success(latency_ms=result.execution_time_ms)
                else:
                    health.record_failure(Exception(result.error))

            assert health.successful_requests == 5
            assert health.status == "healthy"
        finally:
            await connector.disconnect()

    @pytest.mark.asyncio
    async def test_health_tracks_query_errors(self):
        """Health should track query errors."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})
        health = ConnectionHealth()

        try:
            await connector.connect()

            # Execute an invalid query
            result = await connector.execute_query("SELECT * FROM nonexistent_table")
            if result.error:
                health.record_failure(Exception(result.error))

            assert health.failed_requests >= 1
        finally:
            await connector.disconnect()


# =============================================================================
# Retry Integration Tests
# =============================================================================

class TestRetryIntegration:
    """Integration tests for retry logic with connectors."""

    @pytest.mark.asyncio
    async def test_retry_recovers_from_transient_failure(self):
        """Retry should recover from simulated transient failure."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Simulated transient failure")
            return "success"

        result = await flaky_operation()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_with_real_connector(self):
        """Test retry decorator with real connector operations."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})

        @with_retry(max_attempts=2, min_wait=0.01)
        async def query_with_retry():
            if not connector._connected:
                await connector.connect()
            return await connector.execute_query("SELECT 42 as answer")

        try:
            result = await query_with_retry()
            assert result.error is None
            assert result.row_count == 1
        finally:
            await connector.disconnect()


# =============================================================================
# Multi-Connector Tests
# =============================================================================

class TestMultipleConnectors:
    """Tests for using multiple connectors simultaneously."""

    @pytest.mark.asyncio
    async def test_multiple_duckdb_instances(self):
        """Test multiple DuckDB connectors work independently."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        conn1 = connector_class({"database": ":memory:"})
        conn2 = connector_class({"database": ":memory:"})

        try:
            await conn1.connect()
            await conn2.connect()

            # Create different tables in each
            await conn1.execute_query("CREATE TABLE t1 (id INTEGER)")
            await conn2.execute_query("CREATE TABLE t2 (id INTEGER)")

            # Verify they're independent
            schema1 = await conn1.discover_schema()
            schema2 = await conn2.discover_schema()

            table_names1 = [t.name for t in schema1.tables]
            table_names2 = [t.name for t in schema2.tables]

            assert "t1" in table_names1
            assert "t2" in table_names2
            assert "t1" not in table_names2  # Independent databases
            assert "t2" not in table_names1
        finally:
            await conn1.disconnect()
            await conn2.disconnect()


# =============================================================================
# Query Result Tests
# =============================================================================

class TestQueryResults:
    """Tests for query result handling."""

    @pytest.mark.asyncio
    async def test_query_returns_correct_types(self):
        """Query results should have correct data types."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})

        try:
            await connector.connect()

            result = await connector.execute_query("""
                SELECT
                    42 as int_col,
                    3.14 as float_col,
                    'hello' as str_col,
                    true as bool_col
            """)

            assert result.error is None
            assert len(result.rows) == 1
            assert len(result.columns) == 4
        finally:
            await connector.disconnect()

    @pytest.mark.asyncio
    async def test_query_error_captured(self):
        """Query errors should be captured in result."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})

        try:
            await connector.connect()

            result = await connector.execute_query("INVALID SQL SYNTAX HERE")

            assert result.error is not None
            assert result.row_count == 0
        finally:
            await connector.disconnect()

    @pytest.mark.asyncio
    async def test_empty_result_handled(self):
        """Empty query results should be handled correctly."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})

        try:
            await connector.connect()

            # Create empty table
            await connector.execute_query("CREATE TABLE empty_table (id INTEGER)")

            # Query empty table
            result = await connector.execute_query("SELECT * FROM empty_table")

            assert result.error is None
            assert result.row_count == 0
            assert result.rows == []
        finally:
            await connector.disconnect()


# =============================================================================
# Schema Discovery Tests
# =============================================================================

class TestSchemaDiscovery:
    """Tests for schema discovery functionality."""

    @pytest.mark.asyncio
    async def test_discover_table_columns(self):
        """Schema discovery should include column information."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})

        try:
            await connector.connect()

            # Create table with various column types
            await connector.execute_query("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    email VARCHAR,
                    age INTEGER
                )
            """)

            schema = await connector.discover_schema()

            # Find our table
            users_table = None
            for table in schema.tables:
                if table.name == "users":
                    users_table = table
                    break

            assert users_table is not None
            assert len(users_table.columns) >= 4

            col_names = [c.name for c in users_table.columns]
            assert "id" in col_names
            assert "name" in col_names
            assert "email" in col_names
            assert "age" in col_names
        finally:
            await connector.disconnect()

    @pytest.mark.asyncio
    async def test_discover_multiple_tables(self):
        """Schema discovery should find all tables."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")

        connector = connector_class({"database": ":memory:"})

        try:
            await connector.connect()

            # Create multiple tables
            await connector.execute_query("CREATE TABLE table_a (id INTEGER)")
            await connector.execute_query("CREATE TABLE table_b (id INTEGER)")
            await connector.execute_query("CREATE TABLE table_c (id INTEGER)")

            schema = await connector.discover_schema()

            table_names = [t.name for t in schema.tables]
            assert "table_a" in table_names
            assert "table_b" in table_names
            assert "table_c" in table_names
        finally:
            await connector.disconnect()
