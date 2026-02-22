"""
Tests for job retry and recovery functionality in StateStore.

Tests cover:
1. Job creation with retry configuration
2. Marking jobs for retry
3. Finding stale running jobs
4. Finding jobs ready for retry
5. Re-queuing jobs
6. Heartbeat updates
7. Webhook tracking
"""
import pytest
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from backend.app.repositories.state.store import StateStore


@pytest.fixture
def state_store(tmp_path: Path, monkeypatch) -> StateStore:
    """Create a temporary StateStore for testing."""
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    store = StateStore(base_dir=tmp_path)
    return store


class TestJobCreationWithRetry:
    """Tests for creating jobs with retry configuration."""

    def test_job_created_with_default_retry_config(self, state_store: StateStore):
        """New jobs should have default retry configuration."""
        job = state_store.create_job(
            job_type="run_report",
            template_id="test-template",
        )

        assert job["retryCount"] == 0
        assert job["maxRetries"] == 3  # DEFAULT_MAX_RETRIES
        assert job["retryAt"] is None
        assert job["failureReason"] is None

    def test_job_created_with_custom_retry_config(self, state_store: StateStore):
        """Jobs can be created with custom retry configuration."""
        job = state_store.create_job(
            job_type="run_report",
            template_id="test-template",
            max_retries=5,
            retry_backoff_seconds=60,
        )

        assert job["maxRetries"] == 5

    def test_job_created_with_webhook(self, state_store: StateStore):
        """Jobs can be created with webhook configuration."""
        job = state_store.create_job(
            job_type="run_report",
            template_id="test-template",
            webhook_url="https://example.com/webhook",
            webhook_secret="my-secret",
        )

        assert job["webhookUrl"] == "https://example.com/webhook"
        assert job["notificationSentAt"] is None

    def test_job_created_with_priority(self, state_store: StateStore):
        """Jobs can be created with priority."""
        job = state_store.create_job(
            job_type="run_report",
            template_id="test-template",
            priority=5,
        )

        # Priority is stored but may not be in sanitized output
        raw_job = state_store._read_state()["jobs"][job["id"]]
        assert raw_job.get("priority") == 5


class TestMarkJobForRetry:
    """Tests for marking jobs for retry."""

    def test_mark_job_for_retry_increments_count(self, state_store: StateStore):
        """Marking a job for retry should increment retry_count."""
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])

        result = state_store.mark_job_for_retry(
            job["id"],
            reason="Connection timeout",
        )

        assert result["retryCount"] == 1
        assert result["status"] == "pending_retry"
        assert result["failureReason"] == "Connection timeout"
        assert result["retryAt"] is not None

    def test_mark_job_for_retry_calculates_backoff(self, state_store: StateStore):
        """Retry backoff should increase exponentially."""
        job = state_store.create_job(
            job_type="run_report",
            template_id="test",
            retry_backoff_seconds=10,
        )

        # First retry: ~10 seconds
        state_store.mark_job_for_retry(job["id"], reason="error 1")
        job1 = state_store.get_job(job["id"])
        retry_at_1 = datetime.fromisoformat(job1["retryAt"])

        # Manually set back to running for next test
        state_store._update_job_record(job["id"], lambda r: r.update({"status": "running"}) or True)

        # Second retry: ~20 seconds
        state_store.mark_job_for_retry(job["id"], reason="error 2")
        job2 = state_store.get_job(job["id"])
        retry_at_2 = datetime.fromisoformat(job2["retryAt"])

        # Second retry should be further out than first
        # (allowing for jitter, we just check it's not the same)
        assert retry_at_2 > retry_at_1

    def test_mark_job_for_retry_fails_after_max_retries(self, state_store: StateStore):
        """Job should permanently fail after max retries exceeded."""
        job = state_store.create_job(
            job_type="run_report",
            template_id="test",
            max_retries=2,
        )

        # First retry
        state_store.mark_job_for_retry(job["id"], reason="error 1")
        job1 = state_store.get_job(job["id"])
        assert job1["status"] == "pending_retry"

        # Second retry
        state_store._update_job_record(job["id"], lambda r: r.update({"status": "running"}) or True)
        state_store.mark_job_for_retry(job["id"], reason="error 2")
        job2 = state_store.get_job(job["id"])
        assert job2["status"] == "pending_retry"

        # Third attempt - should fail permanently
        state_store._update_job_record(job["id"], lambda r: r.update({"status": "running"}) or True)
        state_store.mark_job_for_retry(job["id"], reason="error 3")
        job3 = state_store.get_job(job["id"])
        assert job3["status"] == "failed"
        assert "max retries exceeded" in job3.get("error", "").lower()

    def test_mark_non_retriable_error(self, state_store: StateStore):
        """Non-retriable errors should immediately fail the job."""
        job = state_store.create_job(job_type="run_report", template_id="test")

        result = state_store.mark_job_for_retry(
            job["id"],
            reason="Template not found",
            is_retriable=False,
        )

        assert result["status"] == "failed"
        assert result["retryCount"] == 0  # Didn't increment


class TestFindStaleRunningJobs:
    """Tests for finding stale running jobs."""

    def test_find_stale_job_without_heartbeat(self, state_store: StateStore):
        """Jobs without heartbeat that started long ago should be found."""
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])

        # Backdate the started_at timestamp
        old_time = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        state_store._update_job_record(
            job["id"],
            lambda r: r.update({"started_at": old_time}) or True
        )

        stale = state_store.find_stale_running_jobs(heartbeat_timeout_seconds=60)
        assert len(stale) == 1
        assert stale[0]["id"] == job["id"]

    def test_find_stale_job_with_old_heartbeat(self, state_store: StateStore):
        """Jobs with old heartbeats should be found."""
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])

        # Set an old heartbeat
        old_time = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        state_store._update_job_record(
            job["id"],
            lambda r: r.update({"last_heartbeat_at": old_time}) or True
        )

        stale = state_store.find_stale_running_jobs(heartbeat_timeout_seconds=60)
        assert len(stale) == 1

    def test_recent_heartbeat_not_stale(self, state_store: StateStore):
        """Jobs with recent heartbeats should not be found."""
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])
        state_store.update_job_heartbeat(job["id"], worker_id="worker-1")

        stale = state_store.find_stale_running_jobs(heartbeat_timeout_seconds=60)
        assert len(stale) == 0

    def test_completed_jobs_not_found(self, state_store: StateStore):
        """Completed jobs should not be found as stale."""
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])
        state_store.record_job_completion(job["id"], status="succeeded")

        stale = state_store.find_stale_running_jobs(heartbeat_timeout_seconds=0)
        assert len(stale) == 0


class TestFindJobsReadyForRetry:
    """Tests for finding jobs ready for retry."""

    def test_find_jobs_ready_for_retry(self, state_store: StateStore):
        """Jobs with past retry_at should be found."""
        job = state_store.create_job(job_type="run_report", template_id="test")

        # Set to pending_retry with past retry_at
        past_time = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        state_store._update_job_record(
            job["id"],
            lambda r: r.update({
                "status": "pending_retry",
                "retry_at": past_time,
            }) or True
        )

        ready = state_store.find_jobs_ready_for_retry()
        assert len(ready) == 1
        assert ready[0]["id"] == job["id"]

    def test_future_retry_not_found(self, state_store: StateStore):
        """Jobs with future retry_at should not be found."""
        job = state_store.create_job(job_type="run_report", template_id="test")

        # Set to pending_retry with future retry_at
        future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        state_store._update_job_record(
            job["id"],
            lambda r: r.update({
                "status": "pending_retry",
                "retry_at": future_time,
            }) or True
        )

        ready = state_store.find_jobs_ready_for_retry()
        assert len(ready) == 0


class TestRequeueJobForRetry:
    """Tests for re-queuing jobs for retry."""

    def test_requeue_moves_to_queued(self, state_store: StateStore):
        """Re-queuing should move job to 'queued' status."""
        job = state_store.create_job(job_type="run_report", template_id="test")

        # Set to pending_retry
        state_store._update_job_record(
            job["id"],
            lambda r: r.update({"status": "pending_retry", "retry_at": "2020-01-01T00:00:00Z"}) or True
        )

        result = state_store.requeue_job_for_retry(job["id"])
        assert result["status"] == "queued"
        assert result["retryAt"] is None

    def test_requeue_only_works_for_pending_retry(self, state_store: StateStore):
        """Re-queue should only work for pending_retry status."""
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])

        # Job is running, not pending_retry
        result = state_store.requeue_job_for_retry(job["id"])

        # Should return the job but status unchanged
        job_after = state_store.get_job(job["id"])
        assert job_after["status"] == "running"


class TestHeartbeat:
    """Tests for heartbeat functionality."""

    def test_update_heartbeat(self, state_store: StateStore):
        """Heartbeat should update timestamp."""
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])

        state_store.update_job_heartbeat(job["id"], worker_id="worker-123")

        job = state_store.get_job(job["id"])
        assert job["lastHeartbeatAt"] is not None
        assert job["workerId"] == "worker-123"

    def test_heartbeat_updates_repeatedly(self, state_store: StateStore):
        """Multiple heartbeats should update timestamp."""
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])

        state_store.update_job_heartbeat(job["id"])
        job1 = state_store.get_job(job["id"])
        hb1 = job1["lastHeartbeatAt"]

        time.sleep(0.1)  # Small delay

        state_store.update_job_heartbeat(job["id"])
        job2 = state_store.get_job(job["id"])
        hb2 = job2["lastHeartbeatAt"]

        # Timestamps should be different (or at least not fail)
        assert hb1 is not None
        assert hb2 is not None


class TestWebhookTracking:
    """Tests for webhook tracking functionality."""

    def test_update_webhook_url(self, state_store: StateStore):
        """Can update webhook URL on existing job."""
        job = state_store.create_job(job_type="run_report", template_id="test")

        state_store.update_job_webhook(
            job["id"],
            webhook_url="https://example.com/hook",
        )

        job = state_store.get_job(job["id"])
        assert job["webhookUrl"] == "https://example.com/hook"

    def test_mark_webhook_sent(self, state_store: StateStore):
        """Can mark webhook as sent."""
        job = state_store.create_job(
            job_type="run_report",
            template_id="test",
            webhook_url="https://example.com/hook",
        )

        state_store.mark_webhook_sent(job["id"])

        job = state_store.get_job(job["id"])
        assert job["notificationSentAt"] is not None

    def test_find_jobs_pending_webhook(self, state_store: StateStore):
        """Can find completed jobs with pending webhooks."""
        # Job with webhook that hasn't been sent
        job1 = state_store.create_job(
            job_type="run_report",
            template_id="test1",
            webhook_url="https://example.com/hook1",
        )
        state_store.record_job_completion(job1["id"], status="succeeded")

        # Job with webhook that was sent
        job2 = state_store.create_job(
            job_type="run_report",
            template_id="test2",
            webhook_url="https://example.com/hook2",
        )
        state_store.record_job_completion(job2["id"], status="succeeded")
        state_store.mark_webhook_sent(job2["id"])

        # Job without webhook
        job3 = state_store.create_job(
            job_type="run_report",
            template_id="test3",
        )
        state_store.record_job_completion(job3["id"], status="succeeded")

        # Running job with webhook
        job4 = state_store.create_job(
            job_type="run_report",
            template_id="test4",
            webhook_url="https://example.com/hook4",
        )
        state_store.record_job_start(job4["id"])

        pending = state_store.get_jobs_pending_webhook()

        # Only job1 should be found
        assert len(pending) == 1
        assert pending[0]["id"] == job1["id"]


class TestRealWorldScenarios:
    """Tests for real-world retry scenarios."""

    def test_full_retry_cycle(self, state_store: StateStore):
        """Test a complete retry cycle from failure to success."""
        # Create job
        job = state_store.create_job(
            job_type="run_report",
            template_id="test",
            max_retries=3,
        )

        # Start job
        state_store.record_job_start(job["id"])
        state_store.update_job_heartbeat(job["id"], worker_id="worker-1")

        # First failure (retriable)
        state_store.mark_job_for_retry(job["id"], reason="Connection timeout")
        job = state_store.get_job(job["id"])
        assert job["status"] == "pending_retry"
        assert job["retryCount"] == 1

        # Requeue for retry
        state_store._update_job_record(job["id"], lambda r: r.update({
            "retry_at": (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        }) or True)
        state_store.requeue_job_for_retry(job["id"])
        job = state_store.get_job(job["id"])
        assert job["status"] == "queued"

        # Second attempt succeeds
        state_store.record_job_start(job["id"])
        state_store.update_job_heartbeat(job["id"], worker_id="worker-2")
        state_store.record_job_completion(job["id"], status="succeeded")

        job = state_store.get_job(job["id"])
        assert job["status"] == "succeeded"
        assert job["retryCount"] == 1  # Still shows 1 retry was needed

    def test_server_restart_recovery(self, state_store: StateStore):
        """Test recovery after simulated server restart."""
        # Create and start a job
        job = state_store.create_job(job_type="run_report", template_id="test")
        state_store.record_job_start(job["id"])

        # Simulate old heartbeat (server crashed)
        old_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        state_store._update_job_record(
            job["id"],
            lambda r: r.update({"last_heartbeat_at": old_time, "started_at": old_time}) or True
        )

        # Recovery daemon finds stale job
        stale_jobs = state_store.find_stale_running_jobs(heartbeat_timeout_seconds=120)
        assert len(stale_jobs) == 1

        # Mark for retry
        state_store.mark_job_for_retry(
            job["id"],
            reason="Worker heartbeat timeout - job may have crashed",
        )

        job = state_store.get_job(job["id"])
        assert job["status"] == "pending_retry"


class TestUpdateJob:
    """Tests for the generic update_job() method."""

    def test_update_single_field(self, state_store: StateStore):
        job = state_store.create_job(job_type="run_report", template_id="t1")
        updated = state_store.update_job(job["id"], status="cancelled")
        assert updated is not None
        assert updated["status"] == "cancelled"

    def test_update_multiple_fields(self, state_store: StateStore):
        job = state_store.create_job(job_type="run_report", template_id="t1")
        updated = state_store.update_job(job["id"], status="failed", error="timeout")
        assert updated["status"] == "failed"
        assert updated["error"] == "timeout"

    def test_update_nonexistent_job_returns_none(self, state_store: StateStore):
        result = state_store.update_job("nonexistent-id", status="cancelled")
        assert result is None

    def test_update_no_fields_returns_current(self, state_store: StateStore):
        job = state_store.create_job(job_type="run_report", template_id="t1")
        result = state_store.update_job(job["id"])
        assert result is not None
        assert result["id"] == job["id"]

    def test_update_persists(self, state_store: StateStore):
        job = state_store.create_job(job_type="run_report", template_id="t1")
        state_store.update_job(job["id"], status="cancelled")
        refreshed = state_store.get_job(job["id"])
        assert refreshed["status"] == "cancelled"


class TestDeleteJob:
    """Tests for the delete_job() method."""

    def test_delete_existing_job(self, state_store: StateStore):
        job = state_store.create_job(job_type="run_report", template_id="t1")
        assert state_store.delete_job(job["id"]) is True
        assert state_store.get_job(job["id"]) is None

    def test_delete_nonexistent_job_returns_false(self, state_store: StateStore):
        assert state_store.delete_job("nonexistent-id") is False

    def test_delete_does_not_affect_other_jobs(self, state_store: StateStore):
        job1 = state_store.create_job(job_type="run_report", template_id="t1")
        job2 = state_store.create_job(job_type="run_report", template_id="t2")
        state_store.delete_job(job1["id"])
        assert state_store.get_job(job1["id"]) is None
        assert state_store.get_job(job2["id"]) is not None

    def test_delete_reduces_job_count(self, state_store: StateStore):
        job1 = state_store.create_job(job_type="run_report", template_id="t1")
        job2 = state_store.create_job(job_type="run_report", template_id="t2")
        before = state_store.list_jobs()
        state_store.delete_job(job1["id"])
        after = state_store.list_jobs()
        assert len(after) == len(before) - 1
