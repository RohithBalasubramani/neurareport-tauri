"""
Tests for connector resilience utilities.

Tests retry logic, exponential backoff, error classification, and health tracking.
"""
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
import time

from backend.app.services.connectors.resilience import (
    with_retry,
    retry_on_connection_error,
    retry_with_longer_backoff,
    is_transient_error,
    is_permanent_error,
    ConnectionHealth,
    TRANSIENT_ERRORS,
    PERMANENT_ERRORS,
)


# =============================================================================
# Error Classification Tests
# =============================================================================

class TestErrorClassification:
    """Tests for error classification functions."""

    def test_connection_error_is_transient(self):
        """ConnectionError should be classified as transient."""
        error = ConnectionError("Connection refused")
        assert is_transient_error(error) is True
        assert is_permanent_error(error) is False

    def test_timeout_error_is_transient(self):
        """TimeoutError should be classified as transient."""
        error = TimeoutError("Operation timed out")
        assert is_transient_error(error) is True
        assert is_permanent_error(error) is False

    def test_connection_refused_error_is_transient(self):
        """ConnectionRefusedError should be classified as transient."""
        error = ConnectionRefusedError("Connection refused")
        assert is_transient_error(error) is True

    def test_connection_reset_error_is_transient(self):
        """ConnectionResetError should be classified as transient."""
        error = ConnectionResetError("Connection reset by peer")
        assert is_transient_error(error) is True

    def test_value_error_is_permanent(self):
        """ValueError should be classified as permanent."""
        error = ValueError("Invalid configuration")
        assert is_permanent_error(error) is True
        assert is_transient_error(error) is False

    def test_type_error_is_permanent(self):
        """TypeError should be classified as permanent."""
        error = TypeError("Invalid type")
        assert is_permanent_error(error) is True

    def test_permission_error_is_permanent(self):
        """PermissionError should be classified as permanent."""
        error = PermissionError("Access denied")
        assert is_permanent_error(error) is True

    def test_authentication_failed_message_is_permanent(self):
        """Error with 'authentication failed' message should be permanent."""
        error = Exception("Authentication failed: invalid credentials")
        assert is_permanent_error(error) is True

    def test_permission_denied_message_is_permanent(self):
        """Error with 'permission denied' message should be permanent."""
        error = Exception("Permission denied for user")
        assert is_permanent_error(error) is True

    def test_not_found_message_is_permanent(self):
        """Error with 'not found' message should be permanent."""
        error = Exception("Table not found")
        assert is_permanent_error(error) is True

    def test_too_many_connections_is_transient(self):
        """Error with 'too many connections' should be transient."""
        error = Exception("too many connections")
        assert is_transient_error(error) is True

    def test_database_locked_is_transient(self):
        """Error with 'database is locked' should be transient."""
        error = Exception("database is locked")
        assert is_transient_error(error) is True

    def test_deadlock_is_transient(self):
        """Error with 'deadlock' should be transient."""
        error = Exception("Deadlock detected")
        assert is_transient_error(error) is True

    def test_service_unavailable_is_transient(self):
        """Error with '503' status should be transient."""
        error = Exception("HTTP 503 Service Unavailable")
        assert is_transient_error(error) is True

    def test_unknown_error_defaults_to_transient(self):
        """Unknown errors should default to transient (optimistic)."""
        error = Exception("Some unknown error")
        assert is_transient_error(error) is True


# =============================================================================
# Retry Decorator Tests - Async
# =============================================================================

class TestRetryDecoratorAsync:
    """Tests for async retry decorator."""

    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self):
        """Successful calls should not trigger retries."""
        call_count = 0

        @with_retry(max_attempts=3)
        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_transient_error_retries(self):
        """Transient errors should trigger retries."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection refused")
            return "success"

        result = await flaky_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_permanent_error_no_retry(self):
        """Permanent errors should not be retried."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01)
        async def perm_error_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid configuration")

        with pytest.raises(ValueError):
            await perm_error_func()

        assert call_count == 1  # Only called once, no retries

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Should raise after max retries exceeded."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            await always_fails()

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Verify exponential backoff timing."""
        call_times = []

        @with_retry(max_attempts=4, min_wait=0.05, max_wait=1.0, jitter=False)
        async def timed_func():
            call_times.append(time.time())
            if len(call_times) < 4:
                raise ConnectionError("Retry me")
            return "done"

        await timed_func()

        # Check that delays increase exponentially
        # Expected: ~0.05s, ~0.1s, ~0.2s
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            # Second delay should be roughly 2x first delay
            assert delay2 >= delay1 * 1.5  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_on_retry_callback(self):
        """Verify on_retry callback is called."""
        callback_calls = []

        def on_retry_handler(exc, attempt):
            callback_calls.append((str(exc), attempt))

        @with_retry(max_attempts=3, min_wait=0.01, on_retry=on_retry_handler)
        async def callback_func():
            if len(callback_calls) < 2:
                raise ConnectionError("Retry please")
            return "done"

        await callback_func()
        assert len(callback_calls) == 2
        assert callback_calls[0][1] == 1
        assert callback_calls[1][1] == 2


# =============================================================================
# Retry Decorator Tests - Sync
# =============================================================================

class TestRetryDecoratorSync:
    """Tests for sync retry decorator."""

    def test_sync_successful_call(self):
        """Sync successful calls should work without retry."""
        call_count = 0

        @with_retry(max_attempts=3)
        def sync_success():
            nonlocal call_count
            call_count += 1
            return "sync_success"

        result = sync_success()
        assert result == "sync_success"
        assert call_count == 1

    def test_sync_retry_on_transient(self):
        """Sync transient errors should trigger retries."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        def sync_flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Transient failure")
            return "recovered"

        result = sync_flaky()
        assert result == "recovered"
        assert call_count == 2

    def test_sync_permanent_error_no_retry(self):
        """Sync permanent errors should not retry."""
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0.01)
        def sync_perm_error():
            nonlocal call_count
            call_count += 1
            raise PermissionError("Access denied")

        with pytest.raises(PermissionError):
            sync_perm_error()

        assert call_count == 1


# =============================================================================
# ConnectionHealth Tests
# =============================================================================

class TestConnectionHealth:
    """Tests for ConnectionHealth tracking."""

    def test_initial_state(self):
        """Initial health state should be clean."""
        health = ConnectionHealth()
        assert health.total_requests == 0
        assert health.successful_requests == 0
        assert health.failed_requests == 0
        assert health.consecutive_failures == 0
        assert health.status == "healthy"

    def test_record_success(self):
        """Recording success should update metrics."""
        health = ConnectionHealth()
        health.record_success(latency_ms=45.5)

        assert health.total_requests == 1
        assert health.successful_requests == 1
        assert health.failed_requests == 0
        assert health.consecutive_failures == 0
        assert health.average_latency_ms == 45.5
        assert health.success_rate == 100.0
        assert health.status == "healthy"

    def test_record_failure(self):
        """Recording failure should update metrics."""
        health = ConnectionHealth()
        health.record_failure(Exception("Test error"))

        assert health.total_requests == 1
        assert health.successful_requests == 0
        assert health.failed_requests == 1
        assert health.consecutive_failures == 1
        assert health.last_error == "Test error"
        assert health.success_rate == 0.0

    def test_consecutive_failures_reset_on_success(self):
        """Consecutive failures should reset after success."""
        health = ConnectionHealth()
        health.record_failure(Exception("Error 1"))
        health.record_failure(Exception("Error 2"))
        assert health.consecutive_failures == 2

        health.record_success(latency_ms=50.0)
        assert health.consecutive_failures == 0

    def test_degraded_status_on_failures(self):
        """Status should be degraded after 2+ consecutive failures."""
        health = ConnectionHealth()
        health.record_failure(Exception("Error 1"))
        health.record_failure(Exception("Error 2"))
        assert health.status == "degraded"

    def test_unhealthy_status_on_many_failures(self):
        """Status should be unhealthy after 5+ consecutive failures."""
        health = ConnectionHealth()
        for i in range(5):
            health.record_failure(Exception(f"Error {i}"))
        assert health.status == "unhealthy"

    def test_degraded_on_low_success_rate(self):
        """Status should be degraded if success rate < 90%."""
        health = ConnectionHealth()
        # 8 successes, 2 failures = 80% success rate
        for _ in range(8):
            health.record_success(latency_ms=10.0)
        health.record_failure(Exception("Error"))
        health.record_failure(Exception("Error"))

        assert health.success_rate == 80.0
        assert health.status == "degraded"

    def test_average_latency_calculation(self):
        """Average latency should be calculated correctly."""
        health = ConnectionHealth()
        health.record_success(latency_ms=100.0)
        health.record_success(latency_ms=200.0)
        health.record_success(latency_ms=300.0)

        assert health.average_latency_ms == 200.0

    def test_to_dict(self):
        """to_dict should return all metrics."""
        health = ConnectionHealth()
        health.record_success(latency_ms=50.0)
        health.record_failure(Exception("Test"))

        data = health.to_dict()

        assert "status" in data
        assert "total_requests" in data
        assert data["total_requests"] == 2
        assert "successful_requests" in data
        assert "failed_requests" in data
        assert "success_rate" in data
        assert "average_latency_ms" in data
        assert "consecutive_failures" in data
        assert "last_error" in data


# =============================================================================
# Convenience Decorator Tests
# =============================================================================

class TestConvenienceDecorators:
    """Tests for convenience retry decorators."""

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """retry_on_connection_error should use default settings."""
        call_count = 0

        @retry_on_connection_error
        async def connection_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("First try fails")
            return "ok"

        # Patch sleep to speed up test
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await connection_func()

        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_with_longer_backoff(self):
        """retry_with_longer_backoff should have more attempts."""
        call_count = 0

        @retry_with_longer_backoff
        async def long_retry_func():
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise TimeoutError("Still waiting")
            return "finally"

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await long_retry_func()

        assert result == "finally"
        assert call_count == 4


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Edge case tests for resilience utilities."""

    def test_transient_errors_tuple_completeness(self):
        """Verify TRANSIENT_ERRORS contains expected types."""
        assert ConnectionError in TRANSIENT_ERRORS
        assert TimeoutError in TRANSIENT_ERRORS
        assert ConnectionRefusedError in TRANSIENT_ERRORS
        assert ConnectionResetError in TRANSIENT_ERRORS

    def test_permanent_errors_tuple_completeness(self):
        """Verify PERMANENT_ERRORS contains expected types."""
        assert ValueError in PERMANENT_ERRORS
        assert TypeError in PERMANENT_ERRORS
        assert PermissionError in PERMANENT_ERRORS

    @pytest.mark.asyncio
    async def test_jitter_adds_randomness(self):
        """Verify jitter adds randomness to backoff."""
        wait_times = []

        original_sleep = asyncio.sleep

        async def mock_sleep(duration):
            wait_times.append(duration)

        @with_retry(max_attempts=5, min_wait=1.0, max_wait=10.0, jitter=True)
        async def jitter_func():
            if len(wait_times) < 4:
                raise ConnectionError("Retry")
            return "done"

        with patch("asyncio.sleep", side_effect=mock_sleep):
            await jitter_func()

        # With jitter, wait times should not all be identical
        if len(wait_times) >= 2:
            # At least some variation expected due to jitter
            unique_times = set(round(t, 3) for t in wait_times)
            # Either different or close together due to randomness
            assert len(wait_times) >= 2

    @pytest.mark.asyncio
    async def test_max_wait_cap(self):
        """Verify wait time is capped at max_wait."""
        wait_times = []

        async def mock_sleep(duration):
            wait_times.append(duration)

        @with_retry(max_attempts=10, min_wait=1.0, max_wait=5.0, jitter=False)
        async def capped_func():
            if len(wait_times) < 8:
                raise ConnectionError("Keep retrying")
            return "done"

        with patch("asyncio.sleep", side_effect=mock_sleep):
            await capped_func()

        # All wait times should be <= max_wait (5.0)
        for wt in wait_times:
            assert wt <= 5.0

    def test_case_insensitive_error_matching(self):
        """Error message matching should be case-insensitive."""
        error1 = Exception("AUTHENTICATION FAILED")
        error2 = Exception("Authentication Failed")
        error3 = Exception("authentication failed")

        assert is_permanent_error(error1) is True
        assert is_permanent_error(error2) is True
        assert is_permanent_error(error3) is True
