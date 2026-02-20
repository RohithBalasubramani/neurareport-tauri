"""
Property-based tests for database connectors.

Uses hypothesis to test invariants that should always hold.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import Any

from backend.app.services.connectors.resilience import (
    is_transient_error,
    is_permanent_error,
    ConnectionHealth,
    TRANSIENT_ERRORS,
    PERMANENT_ERRORS,
)
from backend.app.services.connectors.base import (
    ConnectionTest,
    QueryResult,
    ColumnInfo,
    TableInfo,
    SchemaInfo,
)


# =============================================================================
# Error Classification Properties
# =============================================================================

class TestErrorClassificationProperties:
    """Property-based tests for error classification."""

    @given(st.text(min_size=1, max_size=500))
    @settings(max_examples=50)
    def test_error_classification_never_crashes(self, message: str):
        """Error classification should never crash on any input."""
        error = Exception(message)
        # Both functions should return bool without crashing
        transient = is_transient_error(error)
        permanent = is_permanent_error(error)

        assert isinstance(transient, bool)
        assert isinstance(permanent, bool)

    @given(st.text(min_size=1, max_size=500))
    @settings(max_examples=50)
    def test_transient_permanent_are_opposites(self, message: str):
        """Transient and permanent should be logical opposites."""
        error = Exception(message)
        transient = is_transient_error(error)
        permanent = is_permanent_error(error)

        # They should be opposite
        assert transient != permanent

    @given(st.sampled_from(list(TRANSIENT_ERRORS)))
    def test_transient_error_types_are_transient(self, error_type):
        """All TRANSIENT_ERROR types should classify as transient."""
        error = error_type("test error")
        assert is_transient_error(error) is True

    @given(st.sampled_from(list(PERMANENT_ERRORS)))
    def test_permanent_error_types_are_permanent(self, error_type):
        """All PERMANENT_ERROR types should classify as permanent."""
        error = error_type("test error")
        assert is_permanent_error(error) is True


# =============================================================================
# ConnectionHealth Properties
# =============================================================================

class TestConnectionHealthProperties:
    """Property-based tests for ConnectionHealth."""

    @given(
        successes=st.integers(min_value=0, max_value=1000),
        failures=st.integers(min_value=0, max_value=1000),
    )
    @settings(max_examples=50)
    def test_health_counts_are_consistent(self, successes: int, failures: int):
        """Health counts should always be consistent."""
        health = ConnectionHealth()

        for _ in range(successes):
            health.record_success(latency_ms=10.0)

        for _ in range(failures):
            health.record_failure(Exception("error"))

        # Total should equal sum of successes and failures
        assert health.total_requests == successes + failures
        assert health.successful_requests == successes
        assert health.failed_requests == failures

    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=30)
    def test_success_rate_is_valid_percentage(self, count: int):
        """Success rate should always be 0-100."""
        health = ConnectionHealth()

        for _ in range(count):
            health.record_success(latency_ms=10.0)

        rate = health.success_rate
        assert 0 <= rate <= 100

    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=30)
    def test_average_latency_is_positive(self, count: int):
        """Average latency should always be non-negative."""
        health = ConnectionHealth()

        for i in range(count):
            health.record_success(latency_ms=float(i + 1))

        assert health.average_latency_ms >= 0

    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=20)
    def test_status_transitions(self, failure_count: int):
        """Status should follow expected transitions based on failures."""
        health = ConnectionHealth()

        for _ in range(failure_count):
            health.record_failure(Exception("error"))

        status = health.status

        if failure_count >= 5:
            assert status == "unhealthy"
        elif failure_count >= 2:
            assert status == "degraded"
        else:
            # Could be healthy or degraded based on success rate
            assert status in ["healthy", "degraded"]

    @given(st.lists(st.floats(min_value=0.1, max_value=1000.0), min_size=1, max_size=100))
    @settings(max_examples=30)
    def test_average_latency_calculation(self, latencies):
        """Average latency should be calculated correctly."""
        assume(len(latencies) > 0)

        health = ConnectionHealth()

        for lat in latencies:
            health.record_success(latency_ms=lat)

        expected_avg = sum(latencies) / len(latencies)
        actual_avg = health.average_latency_ms

        # Allow small floating point differences
        assert abs(actual_avg - expected_avg) < 0.01


# =============================================================================
# Data Model Properties
# =============================================================================

class TestDataModelProperties:
    """Property-based tests for data models."""

    @given(
        success=st.booleans(),
        latency=st.floats(min_value=0.0, max_value=10000.0),
    )
    @settings(max_examples=30)
    def test_connection_test_preserves_values(self, success: bool, latency: float):
        """ConnectionTest should preserve all input values."""
        test = ConnectionTest(success=success, latency_ms=latency)

        assert test.success == success
        assert test.latency_ms == latency

    @given(
        columns=st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=20),
        row_count=st.integers(min_value=0, max_value=1000),
    )
    @settings(max_examples=30)
    def test_query_result_structure(self, columns: list, row_count: int):
        """QueryResult should maintain consistent structure."""
        rows = [[i] * len(columns) for i in range(row_count)]

        result = QueryResult(
            columns=columns,
            rows=rows,
            row_count=row_count,
            execution_time_ms=10.0,
        )

        assert result.columns == columns
        assert result.row_count == row_count
        assert len(result.rows) == row_count

    @given(
        name=st.text(min_size=1, max_size=100),
        data_type=st.text(min_size=1, max_size=50),
        nullable=st.booleans(),
    )
    @settings(max_examples=30)
    def test_column_info_preserves_values(
        self, name: str, data_type: str, nullable: bool
    ):
        """ColumnInfo should preserve all attribute values."""
        col = ColumnInfo(name=name, data_type=data_type, nullable=nullable)

        assert col.name == name
        assert col.data_type == data_type
        assert col.nullable == nullable


# =============================================================================
# Edge Case Properties
# =============================================================================

class TestEdgeCaseProperties:
    """Property-based tests for edge cases."""

    @given(st.text())
    @settings(max_examples=50)
    def test_error_message_unicode_handling(self, message: str):
        """Error classification should handle all unicode strings."""
        error = Exception(message)

        # Should not raise any exceptions
        try:
            is_transient_error(error)
            is_permanent_error(error)
        except Exception as e:
            pytest.fail(f"Error classification crashed: {e}")

    @given(
        st.lists(
            st.tuples(st.booleans(), st.floats(min_value=0.1, max_value=100.0)),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=30)
    def test_health_mixed_operations(self, operations):
        """Health should handle mixed success/failure sequences."""
        health = ConnectionHealth()

        for is_success, value in operations:
            if is_success:
                health.record_success(latency_ms=value)
            else:
                health.record_failure(Exception(f"Error {value}"))

        # Counts should be consistent
        total = health.total_requests
        assert total == len(operations)
        assert health.successful_requests + health.failed_requests == total

        # Status should be valid
        assert health.status in ["healthy", "degraded", "unhealthy"]

    @given(st.integers(min_value=0, max_value=100))
    @settings(max_examples=20)
    def test_consecutive_failures_reset(self, success_count: int):
        """Consecutive failures should reset after any number of successes."""
        health = ConnectionHealth()

        # Add some failures
        health.record_failure(Exception("e1"))
        health.record_failure(Exception("e2"))
        assert health.consecutive_failures == 2

        # Add successes
        for _ in range(success_count):
            health.record_success(latency_ms=10.0)

        # After any success, consecutive failures should be 0
        if success_count > 0:
            assert health.consecutive_failures == 0


# =============================================================================
# Invariant Properties
# =============================================================================

class TestInvariantProperties:
    """Tests for invariants that should always hold."""

    @given(st.integers(min_value=1, max_value=50))
    @settings(max_examples=20)
    def test_health_success_rate_bounds(self, n: int):
        """Success rate should always be between 0 and 100."""
        health = ConnectionHealth()

        # Random mix of successes and failures
        for i in range(n):
            if i % 3 == 0:
                health.record_failure(Exception("error"))
            else:
                health.record_success(latency_ms=10.0)

        rate = health.success_rate
        assert 0 <= rate <= 100

    @given(
        st.lists(st.floats(min_value=0.1, max_value=100.0), min_size=1, max_size=50)
    )
    @settings(max_examples=20)
    def test_latency_average_within_range(self, latencies):
        """Average latency should be within min/max of recorded values."""
        health = ConnectionHealth()

        for lat in latencies:
            health.record_success(latency_ms=lat)

        avg = health.average_latency_ms
        # Allow for floating point precision errors
        assert min(latencies) - 1e-10 <= avg <= max(latencies) + 1e-10

    def test_empty_health_defaults(self):
        """Empty health should have sensible defaults."""
        health = ConnectionHealth()

        # No requests yet
        assert health.total_requests == 0
        assert health.success_rate == 100.0  # Optimistic default
        assert health.average_latency_ms == 0.0
        assert health.status == "healthy"
        assert health.consecutive_failures == 0
        assert health.last_error is None
