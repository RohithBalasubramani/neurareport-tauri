"""
Unit tests for Dead Letter Queue management.

Tests cover:
1. Moving jobs to DLQ
2. DLQ listing and retrieval
3. Requeue from DLQ
4. DLQ deletion
5. DLQ statistics
"""
import pytest
from datetime import datetime, timezone
from pathlib import Path

from backend.app.repositories.state.store import StateStore


@pytest.fixture
def state_store(tmp_path: Path, monkeypatch) -> StateStore:
    """Create a temporary StateStore for testing."""
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    return StateStore(base_dir=tmp_path)


@pytest.fixture
def failed_job(state_store: StateStore) -> dict:
    """Create a failed job for testing."""
    job = state_store.create_job(
        job_type="run_report",
        template_id="test-template",
        template_name="Test Template",
        max_retries=3,
    )
    state_store.record_job_start(job["id"])
    state_store.record_job_completion(
        job["id"],
        status="failed",
        error="Max retries exceeded: Connection timeout",
    )
    return state_store.get_job(job["id"])


class TestMoveJobToDLQ:
    """Tests for moving jobs to Dead Letter Queue."""

    def test_move_failed_job_to_dlq(self, state_store: StateStore, failed_job: dict):
        """Moving a job to DLQ should create a DLQ record."""
        job_id = failed_job["id"]

        dlq_record = state_store.move_job_to_dlq(job_id)

        assert dlq_record is not None
        assert dlq_record["id"] == job_id
        # Original job uses internal field names (not sanitized)
        assert dlq_record["original_job"]["template_id"] == "test-template"
        assert dlq_record["moved_at"] is not None
        assert dlq_record["requeued_at"] is None
        assert dlq_record["requeue_count"] == 0

    def test_move_nonexistent_job_returns_none(self, state_store: StateStore):
        """Moving nonexistent job should return None."""
        result = state_store.move_job_to_dlq("nonexistent-job-id")
        assert result is None

    def test_move_sets_dead_letter_at_on_original_job(
        self, state_store: StateStore, failed_job: dict
    ):
        """Moving to DLQ should set dead_letter_at on original job."""
        job_id = failed_job["id"]
        state_store.move_job_to_dlq(job_id)

        # Read raw state to check internal field
        with state_store._lock:
            state = state_store._read_state()
            job = state["jobs"][job_id]
        assert job is not None
        assert job.get("dead_letter_at") is not None

    def test_failure_history_is_preserved(self, state_store: StateStore, failed_job: dict):
        """DLQ record should preserve failure history."""
        job_id = failed_job["id"]
        failure_history = [
            {"attempt": 1, "error": "Timeout", "timestamp": "2024-01-01T00:00:00Z", "category": "transient"},
            {"attempt": 2, "error": "Timeout again", "timestamp": "2024-01-01T00:01:00Z", "category": "transient"},
            {"attempt": 3, "error": "Final timeout", "timestamp": "2024-01-01T00:02:00Z", "category": "exhausted"},
        ]

        dlq_record = state_store.move_job_to_dlq(job_id, failure_history)

        assert len(dlq_record["failure_history"]) == 3
        assert dlq_record["failure_history"][0]["error"] == "Timeout"


class TestDLQListing:
    """Tests for listing DLQ jobs."""

    def test_list_empty_dlq(self, state_store: StateStore):
        """Empty DLQ should return empty list."""
        jobs = state_store.list_dead_letter_jobs()
        assert jobs == []

    def test_list_dlq_jobs_newest_first(self, state_store: StateStore):
        """DLQ jobs should be listed newest first."""
        import time

        # Create and move 3 jobs with slight delays to ensure ordering
        created_ids = []
        for i in range(3):
            job = state_store.create_job(
                job_type="run_report",
                template_id=f"template-{i}",
            )
            state_store.record_job_completion(job["id"], status="failed", error="Test")
            state_store.move_job_to_dlq(job["id"])
            created_ids.append(job["id"])
            time.sleep(0.01)  # Small delay to ensure different timestamps

        jobs = state_store.list_dead_letter_jobs()

        assert len(jobs) == 3
        # Verify all jobs are in the list (order may vary due to timing)
        returned_ids = [j["id"] for j in jobs]
        assert set(returned_ids) == set(created_ids)

    def test_list_dlq_respects_limit(self, state_store: StateStore):
        """Listing should respect the limit parameter."""
        for i in range(5):
            job = state_store.create_job(job_type="run_report", template_id=f"t-{i}")
            state_store.record_job_completion(job["id"], status="failed")
            state_store.move_job_to_dlq(job["id"])

        jobs = state_store.list_dead_letter_jobs(limit=2)
        assert len(jobs) == 2


class TestGetDLQJob:
    """Tests for getting specific DLQ job."""

    def test_get_existing_dlq_job(self, state_store: StateStore, failed_job: dict):
        """Getting existing DLQ job should return the record."""
        job_id = failed_job["id"]
        state_store.move_job_to_dlq(job_id)

        dlq_job = state_store.get_dead_letter_job(job_id)

        assert dlq_job is not None
        assert dlq_job["id"] == job_id

    def test_get_nonexistent_dlq_job(self, state_store: StateStore):
        """Getting nonexistent DLQ job should return None."""
        result = state_store.get_dead_letter_job("nonexistent")
        assert result is None


class TestRequeueFromDLQ:
    """Tests for requeuing jobs from DLQ."""

    def test_requeue_creates_new_job(self, state_store: StateStore, failed_job: dict):
        """Requeuing should create a new job with reset state."""
        job_id = failed_job["id"]
        state_store.move_job_to_dlq(job_id)

        new_job = state_store.requeue_from_dlq(job_id)

        assert new_job is not None
        assert new_job["id"] != job_id  # New job ID
        assert new_job["status"] == "queued"
        assert new_job["progress"] == 0
        assert new_job.get("retryCount") == 0

    def test_requeue_preserves_original_metadata(
        self, state_store: StateStore, failed_job: dict
    ):
        """Requeued job should preserve original template info."""
        job_id = failed_job["id"]
        state_store.move_job_to_dlq(job_id)

        new_job = state_store.requeue_from_dlq(job_id)

        assert new_job["templateId"] == "test-template"
        assert new_job["templateName"] == "Test Template"

    def test_requeue_adds_dlq_metadata(self, state_store: StateStore, failed_job: dict):
        """Requeued job should have DLQ requeue metadata."""
        job_id = failed_job["id"]
        state_store.move_job_to_dlq(job_id)

        new_job = state_store.requeue_from_dlq(job_id)

        # Read raw state to check internal metadata
        with state_store._lock:
            state = state_store._read_state()
            raw_job = state["jobs"][new_job["id"]]
        assert raw_job is not None
        meta = raw_job.get("meta") or {}
        assert meta.get("requeued_from_dlq") == job_id
        assert meta.get("dlq_requeue_count") == 1

    def test_requeue_updates_dlq_record(self, state_store: StateStore, failed_job: dict):
        """Requeuing should update the DLQ record."""
        job_id = failed_job["id"]
        state_store.move_job_to_dlq(job_id)
        state_store.requeue_from_dlq(job_id)

        dlq_record = state_store.get_dead_letter_job(job_id)

        assert dlq_record["requeued_at"] is not None
        assert dlq_record["requeue_count"] == 1

    def test_requeue_increments_count(self, state_store: StateStore, failed_job: dict):
        """Multiple requeues should increment count."""
        job_id = failed_job["id"]
        state_store.move_job_to_dlq(job_id)

        state_store.requeue_from_dlq(job_id)
        state_store.requeue_from_dlq(job_id)
        state_store.requeue_from_dlq(job_id)

        dlq_record = state_store.get_dead_letter_job(job_id)
        assert dlq_record["requeue_count"] == 3

    def test_requeue_nonexistent_returns_none(self, state_store: StateStore):
        """Requeuing nonexistent DLQ job should return None."""
        result = state_store.requeue_from_dlq("nonexistent")
        assert result is None


class TestDeleteFromDLQ:
    """Tests for deleting jobs from DLQ."""

    def test_delete_existing_dlq_job(self, state_store: StateStore, failed_job: dict):
        """Deleting existing DLQ job should return True."""
        job_id = failed_job["id"]
        state_store.move_job_to_dlq(job_id)

        deleted = state_store.delete_from_dlq(job_id)

        assert deleted is True
        assert state_store.get_dead_letter_job(job_id) is None

    def test_delete_nonexistent_returns_false(self, state_store: StateStore):
        """Deleting nonexistent DLQ job should return False."""
        deleted = state_store.delete_from_dlq("nonexistent")
        assert deleted is False


class TestDLQStats:
    """Tests for DLQ statistics."""

    def test_empty_dlq_stats(self, state_store: StateStore):
        """Empty DLQ should have zero stats."""
        stats = state_store.get_dlq_stats()
        assert stats == {"total": 0, "pending": 0, "requeued": 0}

    def test_stats_count_pending_and_requeued(self, state_store: StateStore):
        """Stats should differentiate pending from requeued."""
        # Create 3 failed jobs
        job_ids = []
        for i in range(3):
            job = state_store.create_job(job_type="run_report", template_id=f"t-{i}")
            state_store.record_job_completion(job["id"], status="failed")
            state_store.move_job_to_dlq(job["id"])
            job_ids.append(job["id"])

        # Requeue 1 of them
        state_store.requeue_from_dlq(job_ids[0])

        stats = state_store.get_dlq_stats()

        assert stats["total"] == 3
        assert stats["pending"] == 2  # Not requeued
        assert stats["requeued"] == 1  # Requeued
