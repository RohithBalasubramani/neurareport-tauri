"""
Tests for LLM Response Cache — line 1257 of FORENSIC_AUDIT_REPORT.md.

Covers:
- Memory cache (get, set, TTL expiry, LRU eviction)
- Disk cache (persistence, expiry cleanup)
- Cache key determinism
- Stats tracking
- Thread safety

Run with: pytest backend/tests/services/llm/test_response_cache.py -v
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from backend.app.services.llm.client import ResponseCache


# =============================================================================
# Memory Cache Tests
# =============================================================================


class TestMemoryCache:
    """Test in-memory LRU cache."""

    def test_set_and_get(self):
        cache = ResponseCache(max_memory_items=10)
        messages = [{"role": "user", "content": "Hello"}]
        response = {"choices": [{"message": {"content": "Hi"}}]}

        cache.set(messages, "gpt-4", response)
        result = cache.get(messages, "gpt-4")

        assert result == response

    def test_get_miss_returns_none(self):
        cache = ResponseCache(max_memory_items=10)
        result = cache.get([{"role": "user", "content": "unknown"}], "gpt-4")
        assert result is None

    def test_different_models_different_keys(self):
        cache = ResponseCache(max_memory_items=10)
        messages = [{"role": "user", "content": "Hello"}]
        resp_a = {"model": "a"}
        resp_b = {"model": "b"}

        cache.set(messages, "model-a", resp_a)
        cache.set(messages, "model-b", resp_b)

        assert cache.get(messages, "model-a") == resp_a
        assert cache.get(messages, "model-b") == resp_b

    def test_ttl_expiry(self):
        cache = ResponseCache(max_memory_items=10, default_ttl_seconds=0.1)
        messages = [{"role": "user", "content": "test"}]
        cache.set(messages, "gpt-4", {"data": "value"})

        # Should be available immediately
        assert cache.get(messages, "gpt-4") is not None

        # Should expire after TTL
        time.sleep(0.15)
        assert cache.get(messages, "gpt-4") is None

    def test_lru_eviction(self):
        cache = ResponseCache(max_memory_items=2)

        msg1 = [{"role": "user", "content": "first"}]
        msg2 = [{"role": "user", "content": "second"}]
        msg3 = [{"role": "user", "content": "third"}]

        cache.set(msg1, "gpt-4", {"data": "1"})
        cache.set(msg2, "gpt-4", {"data": "2"})

        # Cache is full. Adding a third should evict the oldest (msg1)
        cache.set(msg3, "gpt-4", {"data": "3"})

        assert cache.get(msg1, "gpt-4") is None  # Evicted
        assert cache.get(msg2, "gpt-4") is not None
        assert cache.get(msg3, "gpt-4") is not None

    def test_stats_tracking(self):
        cache = ResponseCache(max_memory_items=10)
        messages = [{"role": "user", "content": "stats"}]
        cache.set(messages, "gpt-4", {"data": "x"})

        cache.get(messages, "gpt-4")  # Hit
        cache.get([{"role": "user", "content": "miss"}], "gpt-4")  # Miss

        assert cache._stats["hits"] == 1
        assert cache._stats["misses"] == 1


# =============================================================================
# Disk Cache Tests
# =============================================================================


class TestDiskCache:
    """Test disk-based persistence."""

    def test_set_writes_to_disk(self, tmp_path):
        cache = ResponseCache(max_memory_items=10, cache_dir=tmp_path)
        messages = [{"role": "user", "content": "persist"}]
        cache.set(messages, "gpt-4", {"data": "persisted"})

        # Verify at least one .json file was created
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 1

    def test_disk_read_after_memory_eviction(self, tmp_path):
        cache = ResponseCache(max_memory_items=1, cache_dir=tmp_path)
        msg1 = [{"role": "user", "content": "first"}]
        msg2 = [{"role": "user", "content": "second"}]

        cache.set(msg1, "gpt-4", {"data": "1"})
        cache.set(msg2, "gpt-4", {"data": "2"})  # Evicts msg1 from memory

        # msg1 should still be on disk
        result = cache.get(msg1, "gpt-4")
        assert result == {"data": "1"}

    def test_disk_ttl_expiry(self, tmp_path):
        cache = ResponseCache(
            max_memory_items=10,
            cache_dir=tmp_path,
            default_ttl_seconds=0.1,
        )
        messages = [{"role": "user", "content": "expire"}]
        cache.set(messages, "gpt-4", {"data": "temp"})

        # Clear memory to force disk read
        cache._memory_cache.clear()
        cache._access_order.clear()

        time.sleep(0.15)
        result = cache.get(messages, "gpt-4")
        assert result is None  # Expired on disk too

    def test_cache_dir_created_if_missing(self, tmp_path):
        cache_dir = tmp_path / "nested" / "cache"
        cache = ResponseCache(max_memory_items=10, cache_dir=cache_dir)
        assert cache_dir.exists()


# =============================================================================
# Cache Key Determinism Tests
# =============================================================================


class TestCacheKeyDeterminism:
    """Verify cache keys are deterministic and unique."""

    def test_same_request_same_key(self):
        cache = ResponseCache()
        msgs = [{"role": "user", "content": "test"}]
        key1 = cache._compute_key(msgs, "gpt-4")
        key2 = cache._compute_key(msgs, "gpt-4")
        assert key1 == key2

    def test_different_messages_different_keys(self):
        cache = ResponseCache()
        key1 = cache._compute_key([{"role": "user", "content": "a"}], "gpt-4")
        key2 = cache._compute_key([{"role": "user", "content": "b"}], "gpt-4")
        assert key1 != key2

    def test_different_models_different_keys(self):
        cache = ResponseCache()
        msgs = [{"role": "user", "content": "test"}]
        key1 = cache._compute_key(msgs, "gpt-4")
        key2 = cache._compute_key(msgs, "gpt-3.5")
        assert key1 != key2

    def test_key_is_hex_hash(self):
        cache = ResponseCache()
        key = cache._compute_key([{"role": "user", "content": "x"}], "gpt-4")
        # SHA256 truncated to 32 hex chars
        assert len(key) == 32
        int(key, 16)  # Should not raise


# =============================================================================
# Thread Safety Tests
# =============================================================================


class TestCacheConcurrency:
    """Test thread safety of cache operations."""

    def test_concurrent_reads_and_writes(self):
        cache = ResponseCache(max_memory_items=50)
        errors = []

        def write_ops(idx):
            try:
                for i in range(20):
                    msgs = [{"role": "user", "content": f"thread-{idx}-msg-{i}"}]
                    cache.set(msgs, "gpt-4", {"data": f"{idx}-{i}"})
            except Exception as e:
                errors.append(str(e))

        def read_ops(idx):
            try:
                for i in range(20):
                    msgs = [{"role": "user", "content": f"thread-{idx}-msg-{i}"}]
                    cache.get(msgs, "gpt-4")
            except Exception as e:
                errors.append(str(e))

        threads = []
        for i in range(4):
            threads.append(threading.Thread(target=write_ops, args=(i,)))
            threads.append(threading.Thread(target=read_ops, args=(i,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
