"""Tests for Enrichment Cache hit/miss tracking."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta

from backend.app.services.enrichment.cache import EnrichmentCache, _compute_cache_key


class TestCacheHitMissTracking:
    """Test cache hit/miss tracking functionality."""

    @pytest.fixture
    def mock_state_store(self):
        """Create a mock state store."""
        mock_store = MagicMock()
        # Set up transaction() as a context manager that returns state
        mock_transaction = MagicMock()
        mock_transaction.__enter__ = MagicMock(return_value={})
        mock_transaction.__exit__ = MagicMock(return_value=None)
        mock_store.transaction.return_value = mock_transaction
        return mock_store

    def test_cache_miss_on_empty_cache(self, mock_state_store):
        """Test that cache miss is recorded when cache is empty."""
        mock_state_store.transaction.return_value.__enter__.return_value = {"enrichment_cache": {}}

        cache = EnrichmentCache(mock_state_store)
        result = cache.get("source-1", "lookup-value")

        assert result is None
        assert cache._misses == 1
        assert cache._hits == 0

    def test_cache_hit_on_valid_entry(self, mock_state_store):
        """Test that cache hit is recorded on valid entry."""
        cache_key = _compute_cache_key("source-1", "lookup-value")
        now = datetime.now(timezone.utc)

        mock_state_store.transaction.return_value.__enter__.return_value = {
            "enrichment_cache": {
                cache_key: {
                    "source_id": "source-1",
                    "lookup_value": "lookup-value",
                    "data": {"result": "cached"},
                    "ttl_hours": 24,
                    "cached_at": now.isoformat(),
                }
            }
        }

        cache = EnrichmentCache(mock_state_store)
        result = cache.get("source-1", "lookup-value", max_age_hours=24)

        assert result == {"result": "cached"}
        assert cache._hits == 1
        assert cache._misses == 0

    def test_cache_miss_on_expired_entry(self, mock_state_store):
        """Test that cache miss is recorded on expired entry."""
        cache_key = _compute_cache_key("source-1", "lookup-value")
        old_time = datetime.now(timezone.utc) - timedelta(hours=48)

        mock_state_store.transaction.return_value.__enter__.return_value = {
            "enrichment_cache": {
                cache_key: {
                    "source_id": "source-1",
                    "lookup_value": "lookup-value",
                    "data": {"result": "expired"},
                    "ttl_hours": 24,
                    "cached_at": old_time.isoformat(),
                }
            }
        }

        cache = EnrichmentCache(mock_state_store)
        result = cache.get("source-1", "lookup-value", max_age_hours=24)

        assert result is None
        assert cache._misses == 1
        assert cache._hits == 0

    def test_multiple_hits_and_misses(self, mock_state_store):
        """Test tracking multiple hits and misses."""
        cache_key = _compute_cache_key("source-1", "exists")
        now = datetime.now(timezone.utc)

        mock_state_store.transaction.return_value.__enter__.return_value = {
            "enrichment_cache": {
                cache_key: {
                    "source_id": "source-1",
                    "lookup_value": "exists",
                    "data": {"result": "cached"},
                    "ttl_hours": 24,
                    "cached_at": now.isoformat(),
                }
            }
        }

        cache = EnrichmentCache(mock_state_store)

        # Two hits
        cache.get("source-1", "exists")
        cache.get("source-1", "exists")

        # Two misses
        cache.get("source-1", "not-exists")
        cache.get("source-2", "something")

        assert cache._hits == 2
        assert cache._misses == 2

    def test_get_stats_returns_hit_rate(self, mock_state_store):
        """Test that get_stats returns hit_rate."""
        cache_key = _compute_cache_key("source-1", "value")
        now = datetime.now(timezone.utc)

        mock_state_store.transaction.return_value.__enter__.return_value = {
            "enrichment_cache": {
                cache_key: {
                    "source_id": "source-1",
                    "lookup_value": "value",
                    "data": {"result": "cached"},
                    "ttl_hours": 24,
                    "cached_at": now.isoformat(),
                }
            }
        }

        cache = EnrichmentCache(mock_state_store)

        # Generate some hits and misses
        cache.get("source-1", "value")  # Hit
        cache.get("source-1", "value")  # Hit
        cache.get("source-1", "missing")  # Miss

        stats = cache.get_stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(2/3, rel=0.01)

    def test_get_stats_returns_size_bytes(self, mock_state_store):
        """Test that get_stats returns size_bytes."""
        cache_key = _compute_cache_key("source-1", "value")
        now = datetime.now(timezone.utc)

        mock_state_store.transaction.return_value.__enter__.return_value = {
            "enrichment_cache": {
                cache_key: {
                    "source_id": "source-1",
                    "lookup_value": "value",
                    "data": {"result": "some data here"},
                    "ttl_hours": 24,
                    "cached_at": now.isoformat(),
                }
            }
        }

        cache = EnrichmentCache(mock_state_store)
        stats = cache.get_stats()

        assert "size_bytes" in stats
        assert stats["size_bytes"] > 0

    def test_get_stats_with_zero_requests(self, mock_state_store):
        """Test hit_rate with zero requests."""
        mock_state_store.transaction.return_value.__enter__.return_value = {"enrichment_cache": {}}

        cache = EnrichmentCache(mock_state_store)
        stats = cache.get_stats()

        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0.0

    def test_get_stats_includes_all_expected_fields(self, mock_state_store):
        """Test that get_stats returns all expected fields."""
        mock_state_store.transaction.return_value.__enter__.return_value = {"enrichment_cache": {}}

        cache = EnrichmentCache(mock_state_store)
        stats = cache.get_stats()

        expected_fields = [
            "total_entries",
            "expired_entries",
            "entries_by_source",
            "hits",
            "misses",
            "hit_rate",
            "size_bytes",
        ]

        for field in expected_fields:
            assert field in stats, f"Missing field: {field}"


class TestCacheKeyComputation:
    """Test cache key computation."""

    def test_cache_key_consistency(self):
        """Test that same input produces same cache key."""
        key1 = _compute_cache_key("source-1", "value")
        key2 = _compute_cache_key("source-1", "value")
        assert key1 == key2

    def test_cache_key_uniqueness(self):
        """Test that different inputs produce different cache keys."""
        key1 = _compute_cache_key("source-1", "value1")
        key2 = _compute_cache_key("source-1", "value2")
        key3 = _compute_cache_key("source-2", "value1")

        assert key1 != key2
        assert key1 != key3
        assert key2 != key3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
