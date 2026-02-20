"""
Concurrency and Race Condition Tests for Job Management.

Tests thread safety and concurrent operation handling:
1. Concurrent idempotency key operations
2. Concurrent DLQ operations
3. Concurrent job state updates
4. Lock contention scenarios
"""
import pytest
import threading
import time
import concurrent.futures
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

from backend.app.repositories.state.store import StateStore


@pytest.fixture
def state_store(tmp_path: Path, monkeypatch) -> StateStore:
    """Create a temporary StateStore for testing."""
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    return StateStore(base_dir=tmp_path)


# =============================================================================
# Concurrent Idempotency Key Tests
# =============================================================================

class TestConcurrentIdempotencyKeys:
    """Tests for concurrent idempotency key operations."""

    def test_concurrent_stores_same_key(self, state_store: StateStore):
        """Multiple threads storing same key should not corrupt state."""
        key = "concurrent-key"
        results: List[Tuple[int, dict]] = []
        errors: List[Exception] = []

        def store_key(thread_id: int):
            try:
                response = {"thread": thread_id, "timestamp": time.time()}
                state_store.store_idempotency_key(key, f"job-{thread_id}", "hash", response)
                exists, cached = state_store.check_idempotency_key(key, "hash")
                if exists and cached:
                    results.append((thread_id, cached))
            except Exception as e:
                errors.append(e)

        # Run 10 threads concurrently
        threads = [threading.Thread(target=store_key, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have no errors
        assert len(errors) == 0, f"Errors: {errors}"

        # Final state should be consistent
        exists, cached = state_store.check_idempotency_key(key, "hash")
        assert exists is True
        assert cached is not None
        assert "thread" in cached

    def test_concurrent_store_different_keys(self, state_store: StateStore):
        """Multiple threads storing different keys should all succeed."""
        results = {}
        errors: List[Exception] = []
        lock = threading.Lock()

        def store_key(thread_id: int):
            try:
                key = f"key-{thread_id}"
                response = {"thread": thread_id}
                state_store.store_idempotency_key(key, f"job-{thread_id}", f"hash-{thread_id}", response)
                exists, cached = state_store.check_idempotency_key(key, f"hash-{thread_id}")
                with lock:
                    results[thread_id] = (exists, cached)
            except Exception as e:
                with lock:
                    errors.append(e)

        # Run 20 threads concurrently
        threads = [threading.Thread(target=store_key, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == 20

        # All should succeed
        for thread_id, (exists, cached) in results.items():
            assert exists is True
            assert cached["thread"] == thread_id

    def test_concurrent_check_while_storing(self, state_store: StateStore):
        """Concurrent reads and writes should not deadlock."""
        key = "read-write-key"
        state_store.store_idempotency_key(key, "job-0", "hash", {"initial": True})

        read_results = []
        write_results = []
        errors = []
        lock = threading.Lock()

        def read_key(n: int):
            try:
                for _ in range(n):
                    exists, cached = state_store.check_idempotency_key(key, "hash")
                    with lock:
                        read_results.append((exists, cached is not None))
            except Exception as e:
                with lock:
                    errors.append(e)

        def write_key(n: int):
            try:
                for i in range(n):
                    response = {"write": i, "time": time.time()}
                    state_store.store_idempotency_key(key, "job", "hash", response)
                    with lock:
                        write_results.append(i)
            except Exception as e:
                with lock:
                    errors.append(e)

        # Start readers and writers
        threads = [
            threading.Thread(target=read_key, args=(50,)),
            threading.Thread(target=read_key, args=(50,)),
            threading.Thread(target=write_key, args=(20,)),
            threading.Thread(target=write_key, args=(20,)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(read_results) == 100
        assert len(write_results) == 40

    def test_concurrent_cleanup(self, state_store: StateStore):
        """Concurrent cleanup operations should be safe."""
        # Create many expired keys
        from datetime import timedelta

        for i in range(50):
            state_store.store_idempotency_key(f"exp-{i}", f"job-{i}", f"hash-{i}", {})

        # Expire all of them
        with state_store._lock:
            state = state_store._read_state()
            past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            for i in range(50):
                if f"exp-{i}" in state.get("idempotency_keys", {}):
                    state["idempotency_keys"][f"exp-{i}"]["expires_at"] = past
            state_store._write_state(state)

        results = []
        errors = []
        lock = threading.Lock()

        def cleanup():
            try:
                removed = state_store.clean_expired_idempotency_keys()
                with lock:
                    results.append(removed)
            except Exception as e:
                with lock:
                    errors.append(e)

        # Run multiple cleanup threads
        threads = [threading.Thread(target=cleanup) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        # Total removed should be <= 50 (some threads might find nothing)
        assert sum(results) <= 50


# =============================================================================
# Concurrent DLQ Tests
# =============================================================================

class TestConcurrentDLQOperations:
    """Tests for concurrent DLQ operations."""

    def test_concurrent_move_to_dlq(self, state_store: StateStore):
        """Multiple jobs moved to DLQ concurrently should all succeed."""
        # Create jobs
        job_ids = []
        for i in range(20):
            job = state_store.create_job(job_type="run_report", template_id=f"t-{i}")
            state_store.record_job_completion(job["id"], status="failed")
            job_ids.append(job["id"])

        results = []
        errors = []
        lock = threading.Lock()

        def move_to_dlq(job_id: str):
            try:
                dlq_record = state_store.move_job_to_dlq(job_id)
                with lock:
                    results.append((job_id, dlq_record is not None))
            except Exception as e:
                with lock:
                    errors.append(e)

        threads = [threading.Thread(target=move_to_dlq, args=(jid,)) for jid in job_ids]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == 20
        assert all(success for _, success in results)

        # Verify all in DLQ
        dlq_jobs = state_store.list_dead_letter_jobs(limit=100)
        assert len(dlq_jobs) == 20

    def test_concurrent_requeue_same_job(self, state_store: StateStore):
        """Multiple threads requeuing same job should all succeed without corruption."""
        job = state_store.create_job(job_type="run_report", template_id="t1")
        state_store.record_job_completion(job["id"], status="failed")
        state_store.move_job_to_dlq(job["id"])

        results = []
        errors = []
        lock = threading.Lock()

        def requeue():
            try:
                new_job = state_store.requeue_from_dlq(job["id"])
                with lock:
                    results.append(new_job)
            except Exception as e:
                with lock:
                    errors.append(e)

        threads = [threading.Thread(target=requeue) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == 10

        # All requeues should create new jobs
        new_job_ids = [j["id"] for j in results if j]
        assert len(new_job_ids) == len(set(new_job_ids))  # All unique

        # Requeue count should be 10
        dlq_record = state_store.get_dead_letter_job(job["id"])
        assert dlq_record["requeue_count"] == 10

    def test_concurrent_dlq_stats(self, state_store: StateStore):
        """Reading DLQ stats while modifying should be safe."""
        # Create some DLQ jobs
        for i in range(10):
            job = state_store.create_job(job_type="run_report", template_id=f"t-{i}")
            state_store.record_job_completion(job["id"], status="failed")
            state_store.move_job_to_dlq(job["id"])

        stats_results = []
        errors = []
        lock = threading.Lock()

        def read_stats():
            for _ in range(20):
                try:
                    stats = state_store.get_dlq_stats()
                    with lock:
                        stats_results.append(stats)
                except Exception as e:
                    with lock:
                        errors.append(e)

        def modify_dlq():
            for i in range(5):
                try:
                    job = state_store.create_job(job_type="run_report", template_id=f"new-{i}")
                    state_store.record_job_completion(job["id"], status="failed")
                    state_store.move_job_to_dlq(job["id"])
                except Exception as e:
                    with lock:
                        errors.append(e)

        threads = [
            threading.Thread(target=read_stats),
            threading.Thread(target=read_stats),
            threading.Thread(target=modify_dlq),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"

        # All stats should be valid
        for stats in stats_results:
            assert "total" in stats
            assert "pending" in stats
            assert "requeued" in stats
            assert stats["total"] >= 0


# =============================================================================
# Concurrent Job State Tests
# =============================================================================

class TestConcurrentJobState:
    """Tests for concurrent job state modifications."""

    def test_concurrent_job_creation(self, state_store: StateStore):
        """Creating many jobs concurrently should all succeed."""
        results = []
        errors = []
        lock = threading.Lock()

        def create_job(i: int):
            try:
                job = state_store.create_job(
                    job_type="run_report",
                    template_id=f"template-{i}",
                )
                with lock:
                    results.append(job)
            except Exception as e:
                with lock:
                    errors.append(e)

        threads = [threading.Thread(target=create_job, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == 50

        # All jobs should have unique IDs
        job_ids = [j["id"] for j in results]
        assert len(job_ids) == len(set(job_ids))

    def test_concurrent_job_updates(self, state_store: StateStore):
        """Concurrent updates to same job should not corrupt state."""
        job = state_store.create_job(job_type="run_report", template_id="t1")
        state_store.record_job_start(job["id"])

        errors = []
        lock = threading.Lock()

        def update_progress(progress: int):
            try:
                state_store.record_job_progress(job["id"], progress)
            except Exception as e:
                with lock:
                    errors.append(e)

        # Multiple threads updating progress
        threads = [
            threading.Thread(target=update_progress, args=(i * 10,))
            for i in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"

        # Final state should be valid
        updated_job = state_store.get_job(job["id"])
        assert 0 <= updated_job["progress"] <= 100


# =============================================================================
# Lock Contention Tests
# =============================================================================

class TestLockContention:
    """Tests for lock contention scenarios."""

    def test_high_contention_mixed_operations(self, state_store: StateStore):
        """High contention from mixed operations should not deadlock."""
        errors = []
        completed = []
        lock = threading.Lock()

        def idempotency_ops():
            for i in range(20):
                try:
                    state_store.store_idempotency_key(f"idem-{i}", f"j-{i}", f"h-{i}", {})
                    state_store.check_idempotency_key(f"idem-{i}", f"h-{i}")
                    with lock:
                        completed.append(("idem", i))
                except Exception as e:
                    with lock:
                        errors.append(("idem", e))

        def dlq_ops():
            for i in range(20):
                try:
                    job = state_store.create_job(job_type="run_report", template_id=f"dlq-{i}")
                    state_store.record_job_completion(job["id"], status="failed")
                    state_store.move_job_to_dlq(job["id"])
                    with lock:
                        completed.append(("dlq", i))
                except Exception as e:
                    with lock:
                        errors.append(("dlq", e))

        def job_ops():
            for i in range(20):
                try:
                    job = state_store.create_job(job_type="run_report", template_id=f"job-{i}")
                    state_store.record_job_start(job["id"])
                    state_store.record_job_progress(job["id"], 50)
                    state_store.record_job_completion(job["id"], status="succeeded")
                    with lock:
                        completed.append(("job", i))
                except Exception as e:
                    with lock:
                        errors.append(("job", e))

        threads = [
            threading.Thread(target=idempotency_ops),
            threading.Thread(target=idempotency_ops),
            threading.Thread(target=dlq_ops),
            threading.Thread(target=job_ops),
            threading.Thread(target=job_ops),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)  # 30 second timeout to detect deadlocks

        # Check for timeouts (deadlocks)
        alive_threads = [t for t in threads if t.is_alive()]
        assert len(alive_threads) == 0, "Deadlock detected - threads still running"

        assert len(errors) == 0, f"Errors: {errors}"

    def test_thread_pool_executor_operations(self, state_store: StateStore):
        """ThreadPoolExecutor should work without issues."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def create_and_process_job(i: int) -> dict:
            job = state_store.create_job(job_type="run_report", template_id=f"tp-{i}")
            state_store.record_job_start(job["id"])
            state_store.record_job_progress(job["id"], 100)
            state_store.record_job_completion(job["id"], status="succeeded")
            return {"id": job["id"], "index": i}

        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_and_process_job, i) for i in range(30)]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    pytest.fail(f"Thread pool operation failed: {e}")

        assert len(results) == 30

        # Verify all jobs exist
        for result in results:
            job = state_store.get_job(result["id"])
            assert job is not None
            assert job["status"] == "succeeded"
