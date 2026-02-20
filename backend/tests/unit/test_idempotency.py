"""
Unit tests for idempotency key management.

Tests cover:
1. Idempotency key storage and retrieval
2. Hash mismatch detection
3. Key expiration
4. Cleanup of expired keys
"""
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.app.repositories.state.store import StateStore


@pytest.fixture
def state_store(tmp_path: Path, monkeypatch) -> StateStore:
    """Create a temporary StateStore for testing."""
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    return StateStore(base_dir=tmp_path)


class TestIdempotencyKeyStorage:
    """Tests for storing and retrieving idempotency keys."""

    def test_store_and_retrieve_idempotency_key(self, state_store: StateStore):
        """Storing a key should allow retrieval with same hash."""
        key = "test-key-123"
        job_id = "job-abc"
        request_hash = "hash-xyz"
        response = {"job_id": job_id, "status": "queued"}

        state_store.store_idempotency_key(key, job_id, request_hash, response)

        exists, cached = state_store.check_idempotency_key(key, request_hash)
        assert exists is True
        assert cached == response

    def test_nonexistent_key_returns_false(self, state_store: StateStore):
        """Checking nonexistent key should return (False, None)."""
        exists, cached = state_store.check_idempotency_key("nonexistent", "hash")
        assert exists is False
        assert cached is None

    def test_empty_key_returns_false(self, state_store: StateStore):
        """Empty key should return (False, None)."""
        exists, cached = state_store.check_idempotency_key("", "hash")
        assert exists is False
        assert cached is None


class TestIdempotencyHashMismatch:
    """Tests for hash mismatch detection."""

    def test_wrong_hash_returns_none_response(self, state_store: StateStore):
        """Same key with different hash should return (True, None)."""
        key = "test-key"
        state_store.store_idempotency_key(
            key, "job-1", "original-hash", {"job_id": "job-1"}
        )

        exists, cached = state_store.check_idempotency_key(key, "different-hash")
        assert exists is True
        assert cached is None  # None indicates hash mismatch

    def test_hash_mismatch_can_be_detected_for_error_response(self, state_store: StateStore):
        """API should return error when hash doesn't match."""
        key = "reused-key"
        state_store.store_idempotency_key(
            key, "job-1", "hash-for-template-A", {"job_id": "job-1"}
        )

        # Simulating reuse of same key for different request
        exists, cached = state_store.check_idempotency_key(key, "hash-for-template-B")

        # exists=True but cached=None means "key exists but payload mismatch"
        # This should trigger a 400 error in the API
        assert exists is True
        assert cached is None


class TestIdempotencyKeyExpiration:
    """Tests for key expiration behavior."""

    def test_expired_key_is_removed_on_check(self, state_store: StateStore):
        """Expired keys should be removed when checked."""
        key = "expiring-key"
        state_store.store_idempotency_key(
            key, "job-1", "hash", {"job_id": "job-1"}
        )

        # Manually backdate the expiration
        with state_store._lock:
            state = state_store._read_state()
            keys = state.get("idempotency_keys", {})
            keys[key]["expires_at"] = (
                datetime.now(timezone.utc) - timedelta(hours=1)
            ).isoformat()
            state["idempotency_keys"] = keys
            state_store._write_state(state)

        # Check should remove expired key
        exists, cached = state_store.check_idempotency_key(key, "hash")
        assert exists is False
        assert cached is None

    def test_key_has_24h_ttl_by_default(self, state_store: StateStore):
        """Keys should have 24-hour TTL."""
        key = "ttl-test"
        state_store.store_idempotency_key(key, "job-1", "hash", {"job_id": "job-1"})

        with state_store._lock:
            state = state_store._read_state()
            record = state["idempotency_keys"][key]
            expires_at = datetime.fromisoformat(record["expires_at"])
            created_at = datetime.fromisoformat(record["created_at"])

            # Should expire ~24 hours after creation
            delta = expires_at - created_at
            assert 23.9 < delta.total_seconds() / 3600 < 24.1


class TestIdempotencyKeyCleanup:
    """Tests for expired key cleanup."""

    def test_cleanup_removes_expired_keys(self, state_store: StateStore):
        """clean_expired_idempotency_keys should remove old keys."""
        # Create 3 keys
        for i in range(3):
            state_store.store_idempotency_key(
                f"key-{i}", f"job-{i}", f"hash-{i}", {"job_id": f"job-{i}"}
            )

        # Expire 2 of them
        with state_store._lock:
            state = state_store._read_state()
            keys = state.get("idempotency_keys", {})
            past = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            keys["key-0"]["expires_at"] = past
            keys["key-1"]["expires_at"] = past
            state["idempotency_keys"] = keys
            state_store._write_state(state)

        # Cleanup
        removed = state_store.clean_expired_idempotency_keys()
        assert removed == 2

        # Only key-2 should remain
        with state_store._lock:
            state = state_store._read_state()
            keys = state.get("idempotency_keys", {})
            assert len(keys) == 1
            assert "key-2" in keys

    def test_cleanup_with_no_expired_keys(self, state_store: StateStore):
        """Cleanup should return 0 when no keys are expired."""
        state_store.store_idempotency_key("fresh-key", "job-1", "hash", {})
        removed = state_store.clean_expired_idempotency_keys()
        assert removed == 0


class TestIdempotencyRecordFields:
    """Tests for idempotency record structure."""

    def test_record_contains_required_fields(self, state_store: StateStore):
        """Stored record should have all required fields."""
        key = "field-test"
        state_store.store_idempotency_key(
            key, "job-123", "hash-abc", {"status": "queued"}
        )

        with state_store._lock:
            state = state_store._read_state()
            record = state["idempotency_keys"][key]

        assert record["key"] == key
        assert record["job_id"] == "job-123"
        assert record["request_hash"] == "hash-abc"
        assert record["response"] == {"status": "queued"}
        assert "created_at" in record
        assert "expires_at" in record
