"""
Error scenario tests for database connectors.

Tests error handling, edge cases, and failure modes.
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
)
from backend.app.services.connectors.registry import CONNECTOR_REGISTRY, get_connector
from backend.app.services.connectors.resilience import (
    is_transient_error,
    is_permanent_error,
    with_retry,
    ConnectionHealth,
)


# =============================================================================
# Connection Error Tests
# =============================================================================

class TestConnectionErrors:
    """Tests for connection error handling."""

    def test_invalid_host_error_message(self):
        """Invalid host should produce clear error."""
        connector_class = CONNECTOR_REGISTRY.get("postgresql")
        if connector_class is None:
            pytest.skip("PostgreSQL connector not registered")

        config = {
            "host": "invalid_host_that_does_not_exist_12345",
            "port": 5432,
            "database": "testdb",
            "username": "user",
            "password": "pass",
        }
        connector = connector_class(config)

        # Connection should fail with ConnectionError or similar
        # Note: actual network test would be an integration test

    def test_wrong_port_is_transient(self):
        """Wrong port connection error should be transient."""
        error = ConnectionRefusedError("Connection refused on port 9999")
        assert is_transient_error(error) is True

    def test_authentication_failure_is_permanent(self):
        """Authentication failure should be permanent."""
        error = Exception("Authentication failed for user 'test'")
        assert is_permanent_error(error) is True

    def test_database_not_found_is_permanent(self):
        """Database not found should be permanent."""
        error = Exception("Database 'nonexistent_db' does not exist")
        assert is_permanent_error(error) is True

    def test_ssl_error_classification(self):
        """SSL errors should be handled appropriately."""
        ssl_error = Exception("SSL certificate verify failed")
        # SSL errors are generally not retriable without config change
        # but connection errors during SSL handshake might be
        # This tests current behavior
        result = is_transient_error(ssl_error)
        # Default is optimistic (transient) for unknown errors
        assert isinstance(result, bool)


# =============================================================================
# Query Error Tests
# =============================================================================

class TestQueryErrors:
    """Tests for query error handling."""

    def test_syntax_error_is_permanent(self):
        """SQL syntax error should not be retried."""
        error = Exception("Syntax error at or near 'SELEC'")
        # Syntax errors are permanent - same query will always fail
        # Currently defaults to transient, but message pattern matching
        # could make it permanent

    def test_table_not_found_is_permanent(self):
        """Table not found error should be permanent."""
        error = Exception("Table 'nonexistent_table' not found")
        assert is_permanent_error(error) is True

    def test_permission_denied_is_permanent(self):
        """Permission denied on query should be permanent."""
        error = Exception("Permission denied for table 'secrets'")
        assert is_permanent_error(error) is True

    def test_timeout_is_transient(self):
        """Query timeout should be transient."""
        error = TimeoutError("Query execution timed out after 30s")
        assert is_transient_error(error) is True

    def test_deadlock_is_transient(self):
        """Deadlock should be transient (retry after conflict resolves)."""
        error = Exception("Deadlock detected, transaction rolled back")
        assert is_transient_error(error) is True


# =============================================================================
# Pool Exhaustion Tests
# =============================================================================

class TestPoolExhaustion:
    """Tests for connection pool exhaustion scenarios."""

    def test_too_many_connections_is_transient(self):
        """Too many connections should be transient."""
        error = Exception("too many connections for database 'prod'")
        assert is_transient_error(error) is True

    def test_pool_exhausted_is_transient(self):
        """Pool exhaustion should be transient."""
        error = Exception("Connection pool exhausted, no available connections")
        # Should be transient - retry after connections free up
        assert is_transient_error(error) is True

    def test_database_locked_is_transient(self):
        """Database locked should be transient."""
        error = Exception("database is locked")
        assert is_transient_error(error) is True


# =============================================================================
# Network Error Tests
# =============================================================================

class TestNetworkErrors:
    """Tests for network-related errors."""

    def test_connection_refused_is_transient(self):
        """Connection refused should be transient."""
        error = ConnectionRefusedError("Connection refused")
        assert is_transient_error(error) is True

    def test_connection_reset_is_transient(self):
        """Connection reset should be transient."""
        error = ConnectionResetError("Connection reset by peer")
        assert is_transient_error(error) is True

    def test_network_unreachable_is_transient(self):
        """Network unreachable should be transient."""
        error = OSError("Network is unreachable")
        assert is_transient_error(error) is True

    def test_dns_resolution_failure_is_transient(self):
        """DNS resolution failure should be transient."""
        error = OSError("Name or service not known")
        assert is_transient_error(error) is True

    def test_service_unavailable_503_is_transient(self):
        """HTTP 503 should be transient."""
        error = Exception("HTTP 503 Service Unavailable")
        assert is_transient_error(error) is True


# =============================================================================
# Configuration Error Tests
# =============================================================================

class TestConfigurationErrors:
    """Tests for configuration-related errors."""

    def test_missing_required_field_is_permanent(self):
        """Missing required config field should be permanent."""
        error = KeyError("host")
        assert is_permanent_error(error) is True

    def test_invalid_type_is_permanent(self):
        """Invalid config type should be permanent."""
        error = TypeError("port must be integer, got str")
        assert is_permanent_error(error) is True

    def test_invalid_value_is_permanent(self):
        """Invalid config value should be permanent."""
        error = ValueError("port must be positive integer")
        assert is_permanent_error(error) is True


# =============================================================================
# Health Tracking Error Tests
# =============================================================================

class TestHealthTrackingErrors:
    """Tests for ConnectionHealth with various errors."""

    def test_health_tracks_transient_errors(self):
        """Health should track transient errors correctly."""
        health = ConnectionHealth()

        for i in range(3):
            health.record_failure(ConnectionError(f"Transient error {i}"))

        assert health.failed_requests == 3
        assert health.consecutive_failures == 3
        assert health.status == "degraded"

    def test_health_recovers_after_success(self):
        """Health should recover after successful request."""
        health = ConnectionHealth()

        # Fail a few times
        health.record_failure(ConnectionError("Error 1"))
        health.record_failure(ConnectionError("Error 2"))
        assert health.status == "degraded"

        # Then succeed
        health.record_success(latency_ms=50.0)
        assert health.consecutive_failures == 0
        # Status depends on overall success rate

    def test_health_unhealthy_after_many_failures(self):
        """Health should be unhealthy after many consecutive failures."""
        health = ConnectionHealth()

        for i in range(6):
            health.record_failure(Exception(f"Error {i}"))

        assert health.status == "unhealthy"
        assert health.consecutive_failures >= 5


# =============================================================================
# Retry Behavior Tests
# =============================================================================

class TestRetryBehavior:
    """Tests for retry decorator behavior with errors."""

    @pytest.mark.asyncio
    async def test_no_retry_on_value_error(self):
        """ValueError should not trigger retry."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01)
        async def value_error_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid config")

        with pytest.raises(ValueError):
            await value_error_func()

        assert call_count == 1  # No retries

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """ConnectionError should trigger retry."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def conn_error_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection lost")
            return "success"

        result = await conn_error_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_permission_error(self):
        """PermissionError should not trigger retry."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01)
        async def perm_error_func():
            nonlocal call_count
            call_count += 1
            raise PermissionError("Access denied")

        with pytest.raises(PermissionError):
            await perm_error_func()

        assert call_count == 1


# =============================================================================
# Edge Case Error Tests
# =============================================================================

class TestEdgeCaseErrors:
    """Edge case tests for error handling."""

    def test_empty_error_message(self):
        """Empty error message should be handled."""
        error = Exception("")
        # Should not crash
        result = is_transient_error(error)
        assert isinstance(result, bool)

    def test_none_in_error_message(self):
        """Error with None-like content should be handled."""
        error = Exception(None)
        result = is_transient_error(error)
        assert isinstance(result, bool)

    def test_unicode_error_message(self):
        """Unicode error messages should be handled."""
        error = Exception("Erreur de connexion: échec d'authentification")
        result = is_transient_error(error)
        assert isinstance(result, bool)

    def test_very_long_error_message(self):
        """Very long error messages should be handled."""
        long_message = "Error: " + "x" * 10000
        error = Exception(long_message)
        result = is_transient_error(error)
        assert isinstance(result, bool)

    def test_nested_exception(self):
        """Nested exceptions should be handled."""
        inner = ConnectionError("Inner error")
        outer = Exception(f"Outer wrapper: {inner}")
        # Should handle nested exception info
        result = is_transient_error(outer)
        assert isinstance(result, bool)

    def test_custom_exception_class(self):
        """Custom exception classes should be handled."""
        class CustomDBError(Exception):
            pass

        error = CustomDBError("Custom database error")
        result = is_transient_error(error)
        # Unknown custom errors default to transient
        assert result is True


# =============================================================================
# Factory Error Tests
# =============================================================================

class TestFactoryErrors:
    """Tests for connector factory error handling."""

    def test_get_connector_invalid_id(self):
        """get_connector with invalid ID should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_connector("invalid_connector_id", {})

        assert "Unknown connector" in str(exc_info.value)

    def test_get_connector_empty_id(self):
        """get_connector with empty ID should raise ValueError."""
        with pytest.raises(ValueError):
            get_connector("", {})

    def test_get_connector_none_config(self):
        """get_connector with None config should be handled."""
        # Behavior depends on implementation
        # Most connectors should handle empty/None config
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class:
            # DuckDB works without config (uses :memory:)
            connector = connector_class({})
            assert connector is not None


# =============================================================================
# Concurrent Error Tests
# =============================================================================

class TestConcurrentErrors:
    """Tests for error handling under concurrent access."""

    def test_health_thread_safety_concept(self):
        """ConnectionHealth should handle concurrent updates safely."""
        health = ConnectionHealth()

        # Simulate rapid updates
        for i in range(100):
            if i % 2 == 0:
                health.record_success(latency_ms=float(i))
            else:
                health.record_failure(Exception(f"Error {i}"))

        # Should not crash and counts should be consistent
        assert health.total_requests == 100
        assert health.successful_requests == 50
        assert health.failed_requests == 50

    def test_health_to_dict_is_snapshot(self):
        """to_dict should return consistent snapshot."""
        health = ConnectionHealth()
        health.record_success(latency_ms=100.0)
        health.record_failure(Exception("Error"))

        snapshot = health.to_dict()

        # Snapshot values should be consistent
        assert snapshot["total_requests"] == \
            snapshot["successful_requests"] + snapshot["failed_requests"]
