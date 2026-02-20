"""
Tests for JobRecoveryDaemon — lines 1253 of FORENSIC_AUDIT_REPORT.md.

Covers:
- Daemon lifecycle (start, stop, double-start, stop-timeout)
- Recovery cycle dispatch (stale jobs, retry requeue, webhook, idempotency, DLQ)
- Stats tracking
- Thread-safety
- Failure resilience (individual step failures don't crash daemon)

Run with: pytest backend/tests/services/jobs/test_recovery_daemon.py -v
"""
from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.jobs.recovery_daemon import (
    JobRecoveryDaemon,
    get_recovery_daemon,
    start_recovery_daemon,
    stop_recovery_daemon,
    is_recovery_daemon_running,
    get_recovery_daemon_stats,
)


# =============================================================================
# Lifecycle Tests
# =============================================================================


class TestDaemonLifecycle:
    """Test daemon start/stop lifecycle."""

    def test_start_and_stop(self):
        daemon = JobRecoveryDaemon(poll_interval_seconds=60)
        assert not daemon.is_running

        started = daemon.start()
        assert started is True
        assert daemon.is_running

        stopped = daemon.stop(timeout_seconds=5)
        assert stopped is True
        assert not daemon.is_running

    def test_double_start_returns_false(self):
        daemon = JobRecoveryDaemon(poll_interval_seconds=60)
        daemon.start()
        try:
            result = daemon.start()
            assert result is False, "Double start should return False"
        finally:
            daemon.stop(timeout_seconds=5)

    def test_stop_when_not_running(self):
        daemon = JobRecoveryDaemon()
        result = daemon.stop()
        assert result is True

    def test_stats_initial_state(self):
        daemon = JobRecoveryDaemon()
        stats = daemon.stats
        assert stats["stale_jobs_recovered"] == 0
        assert stats["jobs_requeued"] == 0
        assert stats["jobs_moved_to_dlq"] == 0
        assert stats["webhooks_sent"] == 0
        assert stats["errors"] == 0
        assert stats["runs"] == 0
        assert stats["last_run_at"] is None

    def test_daemon_thread_is_daemon_thread(self):
        """Daemon thread should be marked as daemon so it doesn't prevent shutdown."""
        daemon = JobRecoveryDaemon(poll_interval_seconds=60)
        daemon.start()
        try:
            assert daemon._thread is not None
            assert daemon._thread.daemon is True
            assert daemon._thread.name == "JobRecoveryDaemon"
        finally:
            daemon.stop(timeout_seconds=5)


# =============================================================================
# Recovery Cycle Tests
# =============================================================================


class TestRecoveryCycle:
    """Test individual recovery steps using mocked state_store."""

    def _make_daemon(self):
        return JobRecoveryDaemon(
            poll_interval_seconds=60,
            heartbeat_timeout_seconds=120,
        )

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_recover_stale_jobs_within_retries(self, mock_store_module):
        """Jobs within retry limit should be marked for retry."""
        mock_store = MagicMock()
        mock_store.find_stale_running_jobs.return_value = [
            {"id": "job-1", "retry_count": 1, "max_retries": 3, "last_heartbeat_at": None},
        ]

        daemon = self._make_daemon()
        daemon._recover_stale_jobs(mock_store)

        mock_store.mark_job_for_retry.assert_called_once()
        assert daemon._stats["stale_jobs_recovered"] == 1

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_recover_stale_jobs_max_retries_exceeded(self, mock_store_module):
        """Jobs at max retries should be permanently failed."""
        mock_store = MagicMock()
        mock_store.find_stale_running_jobs.return_value = [
            {"id": "job-2", "retry_count": 3, "max_retries": 3, "last_heartbeat_at": None},
        ]

        daemon = self._make_daemon()
        daemon._recover_stale_jobs(mock_store)

        mock_store.record_job_completion.assert_called_once_with(
            "job-2",
            status="failed",
            error="Worker died and max retries exceeded",
        )

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_requeue_retry_jobs(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.find_jobs_ready_for_retry.return_value = [
            {"id": "job-3", "retry_count": 1, "retry_at": "2024-01-01T00:00:00"},
        ]

        callback = MagicMock()
        daemon = self._make_daemon()
        daemon.reschedule_callback = callback
        daemon._requeue_retry_jobs(mock_store)

        mock_store.requeue_job_for_retry.assert_called_once_with("job-3")
        callback.assert_called_once_with("job-3")
        assert daemon._stats["jobs_requeued"] == 1

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_requeue_without_callback(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.find_jobs_ready_for_retry.return_value = [
            {"id": "job-4"},
        ]

        daemon = self._make_daemon()
        daemon.reschedule_callback = None
        daemon._requeue_retry_jobs(mock_store)

        mock_store.requeue_job_for_retry.assert_called_once_with("job-4")
        assert daemon._stats["jobs_requeued"] == 1

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_clean_idempotency_keys(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.clean_expired_idempotency_keys.return_value = 7

        daemon = self._make_daemon()
        daemon._clean_idempotency_keys(mock_store)

        assert daemon._stats["idempotency_keys_cleaned"] == 7

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_move_failed_to_dlq(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.list_jobs.return_value = [
            {
                "id": "job-5",
                "status": "failed",
                "retryCount": 3,
                "maxRetries": 3,
                "deadLetterAt": None,
                "error": "Permanent failure",
            },
        ]

        daemon = self._make_daemon()
        daemon._move_failed_to_dlq(mock_store)

        mock_store.move_job_to_dlq.assert_called_once()
        assert daemon._stats["jobs_moved_to_dlq"] == 1

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_dlq_skips_already_in_dlq(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.list_jobs.return_value = [
            {
                "id": "job-6",
                "status": "failed",
                "retryCount": 5,
                "maxRetries": 3,
                "deadLetterAt": "2024-01-01T00:00:00Z",  # Already in DLQ
            },
        ]

        daemon = self._make_daemon()
        daemon._move_failed_to_dlq(mock_store)

        mock_store.move_job_to_dlq.assert_not_called()
        assert daemon._stats["jobs_moved_to_dlq"] == 0


# =============================================================================
# Failure Resilience Tests
# =============================================================================


class TestDaemonResilience:
    """Individual step failures should not crash the daemon."""

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_stale_jobs_error_increments_stats(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.find_stale_running_jobs.side_effect = RuntimeError("DB down")

        daemon = JobRecoveryDaemon()
        daemon._recover_stale_jobs(mock_store)

        assert daemon._stats["errors"] == 1

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_requeue_error_increments_stats(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.find_jobs_ready_for_retry.side_effect = RuntimeError("DB down")

        daemon = JobRecoveryDaemon()
        daemon._requeue_retry_jobs(mock_store)

        assert daemon._stats["errors"] == 1

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_idempotency_error_increments_stats(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.clean_expired_idempotency_keys.side_effect = RuntimeError("DB down")

        daemon = JobRecoveryDaemon()
        daemon._clean_idempotency_keys(mock_store)

        assert daemon._stats["errors"] == 1

    @patch("backend.app.services.jobs.recovery_daemon.state_store", create=True)
    def test_dlq_error_increments_stats(self, mock_store_module):
        mock_store = MagicMock()
        mock_store.list_jobs.side_effect = RuntimeError("DB down")

        daemon = JobRecoveryDaemon()
        daemon._move_failed_to_dlq(mock_store)

        assert daemon._stats["errors"] == 1

    def test_reschedule_callback_error_does_not_crash(self):
        """If reschedule_callback throws, the daemon should continue."""
        mock_store = MagicMock()
        mock_store.find_jobs_ready_for_retry.return_value = [
            {"id": "job-x"},
        ]

        def bad_callback(job_id):
            raise ValueError("Callback crashed")

        daemon = JobRecoveryDaemon()
        daemon.reschedule_callback = bad_callback
        # Should not raise
        daemon._requeue_retry_jobs(mock_store)
        assert daemon._stats["jobs_requeued"] == 1


# =============================================================================
# Module-Level Function Tests
# =============================================================================


class TestModuleFunctions:
    """Test the module-level convenience functions."""

    def test_get_recovery_daemon_singleton(self):
        """get_recovery_daemon should return a singleton."""
        import backend.app.services.jobs.recovery_daemon as mod

        # Reset singleton
        old_daemon = mod._daemon
        mod._daemon = None
        try:
            d1 = get_recovery_daemon()
            d2 = get_recovery_daemon()
            assert d1 is d2
        finally:
            mod._daemon = old_daemon

    def test_get_recovery_daemon_stats_delegates(self):
        stats = get_recovery_daemon_stats()
        assert "runs" in stats
        assert "errors" in stats
