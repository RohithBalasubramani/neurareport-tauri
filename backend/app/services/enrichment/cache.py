"""Caching layer for data enrichment."""
from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("neura.domain.enrichment.cache")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _compute_cache_key(source_id: str, lookup_value: Any) -> str:
    """Compute a cache key from source and lookup value."""
    value_str = json.dumps(lookup_value, sort_keys=True, default=str)
    content = f"{source_id}:{value_str}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


class EnrichmentCache:
    """In-memory cache with TTL support for enrichment data."""

    def __init__(self, state_store):
        self._store = state_store
        self._hits = 0
        self._misses = 0

    def get(
        self,
        source_id: str,
        lookup_value: Any,
        max_age_hours: int = 24,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached enrichment result.

        Args:
            source_id: ID of the enrichment source
            lookup_value: The value being looked up
            max_age_hours: Maximum age of cached data in hours

        Returns:
            Cached data if found and not expired, None otherwise
        """
        cache_key = _compute_cache_key(source_id, lookup_value)

        try:
            with self._store.transaction() as state:
                cache = dict(state.get("enrichment_cache", {}) or {})
            entry = cache.get(cache_key)

            if not entry:
                self._misses += 1
                return None

            # Check expiration
            cached_at = entry.get("cached_at")
            if cached_at:
                cache_time = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                age_hours = (now - cache_time).total_seconds() / 3600

                if age_hours > max_age_hours:
                    logger.debug(f"Cache expired for key {cache_key}")
                    self._misses += 1
                    return None

            self._hits += 1
            return entry.get("data")

        except Exception as exc:
            logger.warning(f"Cache read error: {exc}")
            self._misses += 1
            return None

    def set(
        self,
        source_id: str,
        lookup_value: Any,
        data: Dict[str, Any],
        ttl_hours: int = 24,
    ) -> None:
        """
        Cache enrichment result.

        Args:
            source_id: ID of the enrichment source
            lookup_value: The value being looked up
            data: The enrichment data to cache
            ttl_hours: Time-to-live in hours
        """
        cache_key = _compute_cache_key(source_id, lookup_value)

        try:
            with self._store.transaction() as state:
                cache = state.setdefault("enrichment_cache", {})

                cache[cache_key] = {
                    "source_id": source_id,
                    "lookup_value": lookup_value,
                    "data": data,
                    "ttl_hours": ttl_hours,
                    "cached_at": _now_iso(),
                }

                # Trim cache if too large (keep most recent 1000 entries)
                if len(cache) > 1000:
                    sorted_entries = sorted(
                        cache.items(),
                        key=lambda x: x[1].get("cached_at", ""),
                        reverse=True,
                    )
                    state["enrichment_cache"] = dict(sorted_entries[:1000])

        except Exception as exc:
            logger.warning(f"Cache write error: {exc}")

    def invalidate(self, source_id: Optional[str] = None) -> int:
        """
        Invalidate cache entries.

        Args:
            source_id: If provided, only invalidate entries for this source.
                      If None, invalidate all entries.

        Returns:
            Number of entries invalidated
        """
        try:
            with self._store.transaction() as state:
                cache = state.get("enrichment_cache", {})

                if source_id is None:
                    count = len(cache)
                    state["enrichment_cache"] = {}
                else:
                    original_count = len(cache)
                    cache = {k: v for k, v in cache.items() if v.get("source_id") != source_id}
                    count = original_count - len(cache)
                    state["enrichment_cache"] = cache

                return count

        except Exception as exc:
            logger.warning(f"Cache invalidation error: {exc}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            with self._store.transaction() as state:
                cache = dict(state.get("enrichment_cache", {}) or {})

            now = datetime.now(timezone.utc)
            expired_count = 0
            sources = {}
            size_bytes = 0

            for entry in cache.values():
                source_id = entry.get("source_id", "unknown")
                sources[source_id] = sources.get(source_id, 0) + 1

                # Estimate size of entry
                try:
                    size_bytes += len(json.dumps(entry, default=str))
                except Exception:
                    size_bytes += 100  # Estimate if serialization fails

                cached_at = entry.get("cached_at")
                ttl_hours = entry.get("ttl_hours", 24)
                if cached_at:
                    cache_time = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
                    age_hours = (now - cache_time).total_seconds() / 3600
                    if age_hours > ttl_hours:
                        expired_count += 1

            # Calculate hit rate
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return {
                "total_entries": len(cache),
                "expired_entries": expired_count,
                "entries_by_source": sources,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "size_bytes": size_bytes,
            }

        except Exception as exc:
            logger.warning(f"Cache stats error: {exc}")
            return {"error": "Cache stats unavailable", "hits": 0, "misses": 0, "hit_rate": 0.0, "size_bytes": 0}
