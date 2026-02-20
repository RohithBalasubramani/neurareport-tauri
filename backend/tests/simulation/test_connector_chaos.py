"""
Chaos engineering tests for database connectors.

Tests system resilience under:
1. Connection failures
2. Network partitions (simulated)
3. Timeout scenarios
4. Resource exhaustion
5. Concurrent access
"""
import asyncio
import pytest
import random
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from concurrent.futures import ThreadPoolExecutor
import threading
import time

from backend.app.services.connectors.resilience import (
    with_retry,
    ConnectionHealth,
    is_transient_error,
    is_permanent_error,
    TRANSIENT_ERRORS,
)
from backend.app.services.connectors.registry import CONNECTOR_REGISTRY, get_connector


# =============================================================================
# Connection Failure Chaos Tests
# =============================================================================

class TestConnectionFailureChaos:
    """Chaos tests for connection failures."""

    @pytest.mark.asyncio
    async def test_random_connection_failures(self):
        """System should handle random connection failures gracefully."""
        failure_rate = 0.3  # 30% failure rate
        call_count = 0
        success_count = 0

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def flaky_connect():
            nonlocal call_count, success_count
            call_count += 1
            if random.random() < failure_rate:
                raise ConnectionError("Random connection failure")
            success_count += 1
            return "connected"

        results = []
        for _ in range(20):
            try:
                result = await flaky_connect()
                results.append(("success", result))
            except ConnectionError:
                results.append(("failure", None))

        # With 3 retries and 30% failure, most should succeed
        successes = sum(1 for r in results if r[0] == "success")
        assert successes >= 10, "Too many failures with retry enabled"

    @pytest.mark.asyncio
    async def test_cascading_failures(self):
        """System should handle cascading failures with backoff."""
        failure_sequence = [True, True, True, False]  # Fail 3 times, then succeed
        attempt = 0

        @with_retry(max_attempts=5, min_wait=0.01, max_wait=0.1)
        async def cascading_operation():
            nonlocal attempt
            if attempt < len(failure_sequence) and failure_sequence[attempt]:
                attempt += 1
                raise ConnectionError(f"Cascade failure {attempt}")
            attempt += 1
            return "success"

        result = await cascading_operation()
        assert result == "success"
        assert attempt == 4  # 3 failures + 1 success

    @pytest.mark.asyncio
    async def test_permanent_failure_after_transient(self):
        """Permanent errors should not be retried even after transient ones."""
        attempt = 0

        @with_retry(max_attempts=5, min_wait=0.01)
        async def mixed_failure():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise ConnectionError("Transient failure")
            raise ValueError("Permanent configuration error")

        with pytest.raises(ValueError):
            await mixed_failure()

        assert attempt == 3  # 2 transient retries + 1 permanent


# =============================================================================
# Timeout Chaos Tests
# =============================================================================

class TestTimeoutChaos:
    """Chaos tests for timeout scenarios."""

    @pytest.mark.asyncio
    async def test_slow_operation_with_retry(self):
        """Slow operations should be retried on timeout."""
        attempt = 0

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def slow_operation():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise TimeoutError("Operation timed out")
            return "completed"

        result = await slow_operation()
        assert result == "completed"
        assert attempt == 3

    @pytest.mark.asyncio
    async def test_variable_latency_operations(self):
        """System should handle variable latency gracefully."""
        health = ConnectionHealth()

        async def variable_latency():
            latency = random.uniform(0.001, 0.1)
            await asyncio.sleep(latency)
            return latency * 1000  # Return latency in ms

        for _ in range(10):
            latency_ms = await variable_latency()
            health.record_success(latency_ms=latency_ms)

        # All should be successful
        assert health.successful_requests == 10
        assert health.status == "healthy"


# =============================================================================
# Resource Exhaustion Chaos Tests
# =============================================================================

class TestResourceExhaustionChaos:
    """Chaos tests for resource exhaustion scenarios."""

    @pytest.mark.asyncio
    async def test_pool_exhaustion_recovery(self):
        """System should recover from pool exhaustion."""
        pool_size = 3
        active_connections = 0
        max_active = 0

        @with_retry(max_attempts=5, min_wait=0.01, max_wait=0.1)
        async def acquire_connection():
            nonlocal active_connections, max_active
            if active_connections >= pool_size:
                raise Exception("too many connections")
            active_connections += 1
            max_active = max(max_active, active_connections)
            await asyncio.sleep(0.01)  # Simulate work
            active_connections -= 1
            return "acquired"

        results = []
        for _ in range(10):
            try:
                result = await acquire_connection()
                results.append(result)
            except Exception:
                results.append("exhausted")

        # Should eventually recover and complete some operations
        assert results.count("acquired") > 0

    @pytest.mark.asyncio
    async def test_memory_pressure_simulation(self):
        """System should handle memory pressure gracefully."""
        health = ConnectionHealth()

        for i in range(100):
            if i % 5 == 0:  # 20% failure rate
                # Simulate memory pressure causing failures
                health.record_failure(MemoryError("Out of memory"))
            else:
                health.record_success(latency_ms=float(i))

        # Should track all events
        assert health.total_requests == 100
        assert health.failed_requests == 20
        # 80% success rate is below 90% threshold, so should be degraded
        assert health.status == "degraded"


# =============================================================================
# Concurrent Access Chaos Tests
# =============================================================================

class TestConcurrentAccessChaos:
    """Chaos tests for concurrent access scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_health_tracking(self):
        """Health tracking should handle concurrent updates."""
        health = ConnectionHealth()

        async def random_update():
            for _ in range(100):
                if random.random() < 0.7:
                    health.record_success(latency_ms=random.uniform(1, 100))
                else:
                    health.record_failure(Exception("Random error"))
                await asyncio.sleep(0)  # Yield control

        # Run multiple concurrent updaters
        await asyncio.gather(*[random_update() for _ in range(5)])

        # Total should match expected
        assert health.total_requests == 500
        assert health.status in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_concurrent_retry_operations(self):
        """Multiple concurrent retrying operations should work correctly."""
        call_counts = {}
        lock = asyncio.Lock()

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def concurrent_op(op_id: int):
            async with lock:
                if op_id not in call_counts:
                    call_counts[op_id] = 0
                call_counts[op_id] += 1
                count = call_counts[op_id]

            if count < 2:
                raise ConnectionError(f"Op {op_id} attempt {count}")
            return f"op_{op_id}_complete"

        # Run 10 concurrent operations
        results = await asyncio.gather(
            *[concurrent_op(i) for i in range(10)],
            return_exceptions=True
        )

        # All should succeed (each retries once then succeeds)
        successes = [r for r in results if isinstance(r, str)]
        assert len(successes) == 10


# =============================================================================
# Error Classification Chaos Tests
# =============================================================================

class TestErrorClassificationChaos:
    """Chaos tests for error classification under stress."""

    def test_random_error_classification_stability(self):
        """Error classification should be stable under random input."""
        for _ in range(100):
            # Generate random error messages
            message = "".join(
                random.choices(
                    "abcdefghijklmnopqrstuvwxyz 0123456789",
                    k=random.randint(10, 200)
                )
            )
            error = Exception(message)

            # Classification should never crash
            transient = is_transient_error(error)
            permanent = is_permanent_error(error)

            # Should be opposites
            assert transient != permanent

    def test_error_types_under_stress(self):
        """Error type classification should be consistent under load."""
        results = []

        for error_type in TRANSIENT_ERRORS:
            for _ in range(100):
                error = error_type(f"Error {random.random()}")
                results.append(is_transient_error(error))

        # All transient error types should classify as transient
        assert all(results)


# =============================================================================
# Recovery Chaos Tests
# =============================================================================

class TestRecoveryChaos:
    """Chaos tests for system recovery scenarios."""

    @pytest.mark.asyncio
    async def test_recovery_after_total_failure(self):
        """System should recover after complete failure."""
        health = ConnectionHealth()

        # Simulate total failure
        for _ in range(10):
            health.record_failure(Exception("Total failure"))

        assert health.status == "unhealthy"

        # Simulate recovery
        for _ in range(20):
            health.record_success(latency_ms=50.0)

        # Should recover to healthy
        assert health.consecutive_failures == 0
        # Status depends on overall success rate
        assert health.success_rate >= 60

    @pytest.mark.asyncio
    async def test_intermittent_failure_pattern(self):
        """System should handle intermittent failure patterns."""
        health = ConnectionHealth()

        # Simulate intermittent pattern: 3 success, 1 failure
        for i in range(100):
            if i % 4 == 3:
                health.record_failure(Exception(f"Intermittent error {i}"))
            else:
                health.record_success(latency_ms=float(i))

        assert health.total_requests == 100
        assert health.success_rate == 75.0
        assert health.status == "degraded"  # 75% < 90%

    @pytest.mark.asyncio
    async def test_burst_failure_recovery(self):
        """System should recover from burst of failures."""
        health = ConnectionHealth()

        # Normal operation
        for _ in range(50):
            health.record_success(latency_ms=10.0)

        # Burst of failures
        for _ in range(10):
            health.record_failure(Exception("Burst failure"))

        assert health.consecutive_failures == 10
        assert health.status == "unhealthy"

        # Recovery
        for _ in range(5):
            health.record_success(latency_ms=10.0)

        assert health.consecutive_failures == 0


# =============================================================================
# DuckDB Chaos Tests
# =============================================================================

class TestDuckDBChaos:
    """Chaos tests with real DuckDB connector."""

    @pytest.fixture
    def duckdb_connector(self):
        """Create DuckDB connector for chaos testing."""
        connector_class = CONNECTOR_REGISTRY.get("duckdb")
        if connector_class is None:
            pytest.skip("DuckDB connector not registered")
        return connector_class({"database": ":memory:"})

    @pytest.mark.asyncio
    async def test_rapid_connect_disconnect(self, duckdb_connector):
        """System should handle rapid connect/disconnect cycles."""
        for _ in range(20):
            await duckdb_connector.connect()
            await duckdb_connector.disconnect()

        # Should end in disconnected state
        assert duckdb_connector._connected is False

    @pytest.mark.asyncio
    async def test_query_after_disconnect(self, duckdb_connector):
        """Query after disconnect should auto-reconnect."""
        await duckdb_connector.connect()
        await duckdb_connector.disconnect()

        # Query should auto-connect
        result = await duckdb_connector.execute_query("SELECT 1")
        assert result.error is None

        await duckdb_connector.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_queries(self, duckdb_connector):
        """System should handle concurrent queries."""
        await duckdb_connector.connect()

        async def run_query(i):
            return await duckdb_connector.execute_query(f"SELECT {i} as num")

        results = await asyncio.gather(*[run_query(i) for i in range(10)])

        for i, result in enumerate(results):
            assert result.error is None

        await duckdb_connector.disconnect()

    @pytest.mark.asyncio
    async def test_invalid_query_recovery(self, duckdb_connector):
        """System should recover after invalid queries."""
        await duckdb_connector.connect()

        # Invalid query
        result1 = await duckdb_connector.execute_query("INVALID SQL")
        assert result1.error is not None

        # Valid query should still work
        result2 = await duckdb_connector.execute_query("SELECT 42")
        assert result2.error is None
        assert result2.row_count == 1

        await duckdb_connector.disconnect()


# =============================================================================
# State Corruption Tests
# =============================================================================

class TestStateCorruption:
    """Tests for handling corrupted state."""

    def test_health_handles_negative_latency(self):
        """Health should handle negative latency gracefully."""
        health = ConnectionHealth()

        # Negative latency (shouldn't happen, but might due to clock issues)
        health.record_success(latency_ms=-10.0)

        # Should still work
        assert health.total_requests == 1
        assert health.successful_requests == 1

    def test_health_handles_extreme_values(self):
        """Health should handle extreme latency values."""
        health = ConnectionHealth()

        health.record_success(latency_ms=0.0)
        health.record_success(latency_ms=999999.99)
        health.record_success(latency_ms=float('inf'))

        # Should track without crashing
        assert health.total_requests == 3

    def test_error_with_null_message(self):
        """Error classification should handle null-like messages."""
        test_cases = [
            Exception(None),
            Exception(""),
            Exception(0),
            Exception([]),
            Exception({}),
        ]

        for error in test_cases:
            # Should not crash
            result = is_transient_error(error)
            assert isinstance(result, bool)
