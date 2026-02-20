"""
Property-Based and Fuzz Tests for Job Management.

Uses hypothesis for property-based testing to find edge cases that
manual tests might miss.

Tests cover:
1. Idempotency key invariants
2. DLQ state machine invariants
3. Job state transitions
4. Input fuzzing for edge cases
"""
import pytest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume, HealthCheck

from backend.app.repositories.state.store import StateStore


def make_store():
    """Create a fresh StateStore with a temporary directory."""
    import os
    os.environ.pop("NEURA_STATE_DIR", None)
    tmp = tempfile.mkdtemp()
    return StateStore(base_dir=Path(tmp))


# =============================================================================
# Strategy Definitions
# =============================================================================

# Valid idempotency keys: non-empty strings with reasonable characters
idempotency_key_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P")),
    min_size=1,
    max_size=100,
).filter(lambda x: x.strip())

# Request hash strategy: hexadecimal-like strings
hash_strategy = st.text(
    alphabet="0123456789abcdef",
    min_size=8,
    max_size=64,
)

# Job ID strategy: UUID-like strings
job_id_strategy = st.uuids().map(str)

# Template ID strategy
template_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_"),
    min_size=1,
    max_size=50,
).filter(lambda x: x.strip())


# =============================================================================
# Idempotency Key Property Tests
# =============================================================================

class TestIdempotencyKeyProperties:
    """Property-based tests for idempotency key invariants."""

    @given(
        key=idempotency_key_strategy,
        job_id=job_id_strategy,
        request_hash=hash_strategy,
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_store_then_check_returns_same_response(
        self, key: str, job_id: str, request_hash: str
    ):
        """Stored idempotency key should return exact same response on check."""
        store = make_store()
        response = {"job_id": job_id, "status": "queued"}

        store.store_idempotency_key(key, job_id, request_hash, response)
        exists, cached = store.check_idempotency_key(key, request_hash)

        assert exists is True
        assert cached == response

    @given(
        key=idempotency_key_strategy,
        job_id=job_id_strategy,
        hash1=hash_strategy,
        hash2=hash_strategy,
    )
    @settings(max_examples=50)
    def test_different_hash_returns_none_response(
        self, key: str, job_id: str, hash1: str, hash2: str
    ):
        """Different hash for same key should return (True, None)."""
        assume(hash1 != hash2)  # Ensure hashes are different
        store = make_store()

        store.store_idempotency_key(key, job_id, hash1, {"job_id": job_id})
        exists, cached = store.check_idempotency_key(key, hash2)

        assert exists is True
        assert cached is None  # Hash mismatch

    @given(key=idempotency_key_strategy, request_hash=hash_strategy)
    @settings(max_examples=30)
    def test_nonexistent_key_always_returns_false(self, key: str, request_hash: str):
        """Checking nonexistent key should always return (False, None)."""
        store = make_store()

        exists, cached = store.check_idempotency_key(key, request_hash)

        assert exists is False
        assert cached is None

    @given(
        key=idempotency_key_strategy,
        job_id=job_id_strategy,
        request_hash=hash_strategy,
    )
    @settings(max_examples=30)
    def test_idempotent_store_operations(self, key: str, job_id: str, request_hash: str):
        """Multiple stores with same key should overwrite, not duplicate."""
        store = make_store()
        response1 = {"job_id": job_id, "version": 1}
        response2 = {"job_id": job_id, "version": 2}

        store.store_idempotency_key(key, job_id, request_hash, response1)
        store.store_idempotency_key(key, job_id, request_hash, response2)

        exists, cached = store.check_idempotency_key(key, request_hash)
        assert exists is True
        # Latest store should win
        assert cached["version"] == 2


# =============================================================================
# Dead Letter Queue Property Tests
# =============================================================================

class TestDLQProperties:
    """Property-based tests for DLQ invariants."""

    @given(template_id=template_id_strategy)
    @settings(max_examples=30, deadline=None)
    def test_dlq_preserves_original_job_data(self, template_id: str):
        """Moving to DLQ should preserve all original job data."""
        store = make_store()

        # Create and fail a job
        job = store.create_job(
            job_type="run_report",
            template_id=template_id,
            template_name=f"Template for {template_id}",
        )
        store.record_job_completion(job["id"], status="failed", error="Test error")

        # Move to DLQ
        dlq_record = store.move_job_to_dlq(job["id"])

        assert dlq_record is not None
        assert dlq_record["original_job"]["template_id"] == template_id
        assert "moved_at" in dlq_record

    @given(template_id=template_id_strategy)
    @settings(max_examples=30, deadline=None)
    def test_requeue_creates_new_job_with_reset_state(self, template_id: str):
        """Requeuing from DLQ should create job with reset retry count."""
        store = make_store()

        # Create, fail, and move to DLQ
        job = store.create_job(
            job_type="run_report",
            template_id=template_id,
        )
        store.record_job_completion(job["id"], status="failed")
        store.move_job_to_dlq(job["id"])

        # Requeue
        new_job = store.requeue_from_dlq(job["id"])

        assert new_job is not None
        assert new_job["id"] != job["id"]  # New ID
        assert new_job["status"] == "queued"
        assert new_job["progress"] == 0

    @given(n=st.integers(min_value=1, max_value=10))
    @settings(max_examples=20, deadline=None)
    def test_requeue_count_increments_correctly(self, n: int):
        """Multiple requeues should increment count by exactly n."""
        store = make_store()

        job = store.create_job(job_type="run_report", template_id="t1")
        store.record_job_completion(job["id"], status="failed")
        store.move_job_to_dlq(job["id"])

        for _ in range(n):
            store.requeue_from_dlq(job["id"])

        dlq_record = store.get_dead_letter_job(job["id"])
        assert dlq_record["requeue_count"] == n

    @given(n=st.integers(min_value=0, max_value=20))
    @settings(max_examples=15, deadline=None)
    def test_dlq_stats_are_accurate(self, n: int):
        """DLQ stats should accurately reflect queue state."""
        store = make_store()

        # Create n jobs and move to DLQ
        for i in range(n):
            job = store.create_job(job_type="run_report", template_id=f"t-{i}")
            store.record_job_completion(job["id"], status="failed")
            store.move_job_to_dlq(job["id"])

        stats = store.get_dlq_stats()
        assert stats["total"] == n
        assert stats["pending"] == n
        assert stats["requeued"] == 0


# =============================================================================
# Job State Transition Property Tests
# =============================================================================

class TestJobStateProperties:
    """Property-based tests for job state transitions."""

    @given(template_id=template_id_strategy)
    @settings(max_examples=30)
    def test_job_creation_always_queued(self, template_id: str):
        """Newly created jobs should always be in queued state."""
        store = make_store()

        job = store.create_job(
            job_type="run_report",
            template_id=template_id,
        )

        assert job["status"] == "queued"
        assert job["progress"] == 0

    @given(
        template_id=template_id_strategy,
        progress=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=30)
    def test_progress_updates_are_bounded(self, template_id: str, progress: int):
        """Progress should always be between 0 and 100."""
        store = make_store()

        job = store.create_job(job_type="run_report", template_id=template_id)
        store.record_job_start(job["id"])
        store.record_job_progress(job["id"], progress)

        updated = store.get_job(job["id"])
        assert 0 <= updated["progress"] <= 100


# =============================================================================
# Input Fuzzing Tests
# =============================================================================

class TestInputFuzzing:
    """Fuzz tests for edge case inputs."""

    @given(key=st.text(max_size=1000))
    @settings(max_examples=50)
    def test_idempotency_handles_any_string_key(self, key: str):
        """Idempotency check should handle any string input without crashing."""
        store = make_store()

        # Should not raise
        exists, cached = store.check_idempotency_key(key, "hash")
        assert isinstance(exists, bool)

    @given(job_id=st.text(max_size=500))
    @settings(max_examples=50)
    def test_dlq_handles_any_job_id(self, job_id: str):
        """DLQ operations should handle any job_id without crashing."""
        store = make_store()

        # Should not raise, just return None/False for invalid IDs
        result = store.get_dead_letter_job(job_id)
        assert result is None

        result = store.move_job_to_dlq(job_id)
        assert result is None

        result = store.requeue_from_dlq(job_id)
        assert result is None

        result = store.delete_from_dlq(job_id)
        assert result is False

    @given(limit=st.integers())
    @settings(max_examples=30)
    def test_dlq_list_handles_any_limit(self, limit: int):
        """list_dead_letter_jobs should handle any limit value."""
        store = make_store()

        # Create some jobs
        for i in range(3):
            job = store.create_job(job_type="run_report", template_id=f"t-{i}")
            store.record_job_completion(job["id"], status="failed")
            store.move_job_to_dlq(job["id"])

        # Should not raise for any limit
        try:
            jobs = store.list_dead_letter_jobs(limit=limit)
            assert isinstance(jobs, list)
        except (ValueError, TypeError):
            # It's acceptable to raise for invalid limits
            pass

    @given(
        response=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=False),
                st.text(max_size=100),
            ),
            max_size=20,
        )
    )
    @settings(max_examples=30)
    def test_idempotency_stores_any_json_serializable_response(self, response: dict):
        """Idempotency should store any JSON-serializable response."""
        store = make_store()

        store.store_idempotency_key("key", "job-1", "hash", response)
        exists, cached = store.check_idempotency_key("key", "hash")

        assert exists is True
        assert cached == response
