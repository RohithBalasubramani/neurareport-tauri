"""
Tests for LLM Circuit Breaker — line 1256 of FORENSIC_AUDIT_REPORT.md.

Covers:
- State transitions: CLOSED → OPEN → HALF_OPEN → CLOSED
- Failure threshold enforcement
- Timeout-based recovery to HALF_OPEN
- Success threshold to close circuit
- Failure window cleanup
- Thread-safety
- Stats reporting

Run with: pytest backend/tests/services/llm/test_circuit_breaker.py -v
"""
from __future__ import annotations

import threading
import time
from unittest.mock import patch

import pytest

from backend.app.services.llm.client import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
)


# =============================================================================
# State Transition Tests
# =============================================================================


class TestCircuitBreakerStates:
    """Test circuit breaker state transitions."""

    def test_initial_state_is_closed(self):
        cb = CircuitBreaker("test")
        assert cb.state == CircuitState.CLOSED

    def test_allows_requests_when_closed(self):
        cb = CircuitBreaker("test")
        assert cb.allow_request() is True

    def test_transitions_to_open_after_threshold(self):
        config = CircuitBreakerConfig(failure_threshold=3, failure_window_seconds=60)
        cb = CircuitBreaker("test", config)

        for _ in range(3):
            cb.record_failure()

        assert cb.state == CircuitState.OPEN

    def test_rejects_requests_when_open(self):
        config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=60)
        cb = CircuitBreaker("test", config)

        cb.record_failure()
        cb.record_failure()

        assert cb.allow_request() is False

    def test_transitions_to_half_open_after_timeout(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=0.05,  # 50ms for fast test
        )
        cb = CircuitBreaker("test", config)

        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        time.sleep(0.1)  # Wait for timeout
        assert cb.state == CircuitState.HALF_OPEN

    def test_allows_requests_when_half_open(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=0.05,
        )
        cb = CircuitBreaker("test", config)

        cb.record_failure()
        cb.record_failure()
        time.sleep(0.1)

        assert cb.allow_request() is True

    def test_closes_after_success_threshold_in_half_open(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=0.05,
        )
        cb = CircuitBreaker("test", config)

        # Open the circuit
        cb.record_failure()
        cb.record_failure()

        # Wait for half-open
        time.sleep(0.1)
        _ = cb.state  # Trigger transition

        # Record enough successes
        cb.record_success()
        cb.record_success()

        assert cb.state == CircuitState.CLOSED

    def test_reopens_on_failure_in_half_open(self):
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=0.05,
        )
        cb = CircuitBreaker("test", config)

        # Open
        cb.record_failure()
        cb.record_failure()

        # Wait for half-open
        time.sleep(0.1)
        _ = cb.state

        # Fail again
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_success_in_closed_state_cleans_old_failures(self):
        config = CircuitBreakerConfig(
            failure_threshold=3,
            failure_window_seconds=0.1,
        )
        cb = CircuitBreaker("test", config)

        # Record 2 failures
        cb.record_failure()
        cb.record_failure()

        # Wait for them to expire
        time.sleep(0.15)

        # Record success (should clean old failures)
        cb.record_success()

        # Record 2 more failures — should NOT trigger open because old ones expired
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED


# =============================================================================
# Failure Window Tests
# =============================================================================


class TestFailureWindow:
    """Test failure window-based counting."""

    def test_failures_outside_window_are_ignored(self):
        config = CircuitBreakerConfig(
            failure_threshold=3,
            failure_window_seconds=0.1,
        )
        cb = CircuitBreaker("test", config)

        # Record 2 failures
        cb.record_failure()
        cb.record_failure()

        # Wait for them to expire
        time.sleep(0.15)

        # Record 1 more — total within window is only 1
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED

    def test_rapid_failures_within_window_trigger_open(self):
        config = CircuitBreakerConfig(
            failure_threshold=3,
            failure_window_seconds=10,
        )
        cb = CircuitBreaker("test", config)

        cb.record_failure()
        cb.record_failure()
        cb.record_failure()

        assert cb.state == CircuitState.OPEN


# =============================================================================
# Stats Tests
# =============================================================================


class TestCircuitBreakerStats:
    """Test stats reporting."""

    def test_stats_report_name_and_state(self):
        cb = CircuitBreaker("llm-provider")
        stats = cb.get_stats()

        assert stats["name"] == "llm-provider"
        assert stats["state"] == "closed"
        assert stats["failure_count"] == 0
        assert stats["success_count"] == 0

    def test_stats_reflect_failures(self):
        config = CircuitBreakerConfig(failure_threshold=10)
        cb = CircuitBreaker("test", config)

        cb.record_failure()
        cb.record_failure()

        stats = cb.get_stats()
        assert stats["failure_count"] == 2
        assert stats["last_failure"] is not None


# =============================================================================
# Thread Safety Tests
# =============================================================================


class TestCircuitBreakerConcurrency:
    """Test thread safety of circuit breaker operations."""

    def test_concurrent_failure_recording(self):
        config = CircuitBreakerConfig(
            failure_threshold=100,
            failure_window_seconds=60,
        )
        cb = CircuitBreaker("test", config)
        errors = []

        def record_failures():
            try:
                for _ in range(50):
                    cb.record_failure()
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=record_failures) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        stats = cb.get_stats()
        # Should have recorded close to 200 failures (some may have expired)
        assert stats["failure_count"] > 0

    def test_concurrent_mixed_operations(self):
        config = CircuitBreakerConfig(
            failure_threshold=50,
            success_threshold=5,
            failure_window_seconds=60,
        )
        cb = CircuitBreaker("test", config)
        errors = []

        def mixed_ops():
            try:
                for i in range(100):
                    if i % 3 == 0:
                        cb.record_failure()
                    else:
                        cb.record_success()
                    cb.allow_request()
                    cb.get_stats()
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=mixed_ops) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
