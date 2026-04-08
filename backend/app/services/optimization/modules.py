from __future__ import annotations

import hashlib
import json
import logging
from collections import deque
from typing import Any, Dict, Optional

logger = logging.getLogger("neura.optimization.modules")

# ---------------------------------------------------------------------------
# Optional dependency: DSPy
# ---------------------------------------------------------------------------
_dspy_available = False
try:
    import dspy

    _dspy_available = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Import signatures (conditional on DSPy availability)
# ---------------------------------------------------------------------------
if _dspy_available:
    from .signatures import (
        ReportQualityAssessment,
        FieldMappingReasoner,
        QueryClassifier,
        SQLValidator,
        ContentSummarizer,
    )

from .signatures import (
    StubPrediction,
    stub_report_quality,
    stub_field_mapping,
    stub_query_classifier,
    stub_sql_validator,
    stub_content_summarizer,
    is_dspy_available,
)


# =========================================================================== #
#  DSPy Module wrappers (only defined when DSPy is installed)                 #
# =========================================================================== #

if _dspy_available:

    class ReportQualityModule(dspy.Module):
        """ChainOfThought wrapper for report quality assessment."""

        def __init__(self) -> None:
            super().__init__()
            self.assess = dspy.ChainOfThought(ReportQualityAssessment)

        def forward(
            self,
            report_content: str,
            context: str = "",
        ) -> Any:
            return self.assess(report_content=report_content, context=context)

    class FieldMappingModule(dspy.Module):
        """ChainOfThought wrapper for field mapping reasoning."""

        def __init__(self) -> None:
            super().__init__()
            self.reason = dspy.ChainOfThought(FieldMappingReasoner)

        def forward(
            self,
            source_columns: str,
            target_fields: str,
            context: str = "",
        ) -> Any:
            return self.reason(
                source_columns=source_columns,
                target_fields=target_fields,
                context=context,
            )

    class QueryClassifierModule(dspy.Module):
        """ChainOfThought wrapper for query classification."""

        def __init__(self) -> None:
            super().__init__()
            self.classify = dspy.ChainOfThought(QueryClassifier)

        def forward(
            self,
            query: str,
            available_types: str = "",
        ) -> Any:
            return self.classify(query=query, available_types=available_types)

    class SQLValidatorModule(dspy.Module):
        """ChainOfThought wrapper for SQL validation."""

        def __init__(self) -> None:
            super().__init__()
            self.validate = dspy.ChainOfThought(SQLValidator)

        def forward(
            self,
            sql_query: str,
            schema_context: str = "",
        ) -> Any:
            return self.validate(
                sql_query=sql_query,
                schema_context=schema_context,
            )

    class ContentSummarizerModule(dspy.Module):
        """ChainOfThought wrapper for content summarization."""

        def __init__(self) -> None:
            super().__init__()
            self.summarize = dspy.ChainOfThought(ContentSummarizer)

        def forward(
            self,
            content: str,
            max_length: str = "500",
        ) -> Any:
            return self.summarize(content=content, max_length=max_length)


# =========================================================================== #
#  Fallback classes (always defined, used when DSPy is NOT installed)         #
# =========================================================================== #


class FallbackReportQuality:
    """Fallback for ReportQualityModule when DSPy is unavailable."""

    def __call__(
        self,
        report_content: str,
        context: str = "",
    ) -> StubPrediction:
        return stub_report_quality(report_content, context)


class FallbackFieldMapping:
    """Fallback for FieldMappingModule when DSPy is unavailable."""

    def __call__(
        self,
        source_columns: str,
        target_fields: str,
        context: str = "",
    ) -> StubPrediction:
        return stub_field_mapping(source_columns, target_fields, context)


class FallbackQueryClassifier:
    """Fallback for QueryClassifierModule when DSPy is unavailable."""

    def __call__(
        self,
        query: str,
        available_types: str = "",
    ) -> StubPrediction:
        return stub_query_classifier(query, available_types)


class FallbackSQLValidator:
    """Fallback for SQLValidatorModule when DSPy is unavailable."""

    def __call__(
        self,
        sql_query: str,
        schema_context: str = "",
    ) -> StubPrediction:
        return stub_sql_validator(sql_query, schema_context)


class FallbackContentSummarizer:
    """Fallback for ContentSummarizerModule when DSPy is unavailable."""

    def __call__(
        self,
        content: str,
        max_length: str = "500",
    ) -> StubPrediction:
        return stub_content_summarizer(content, max_length)


# =========================================================================== #
#  CachedModule — LRU-style caching wrapper for any callable module           #
# =========================================================================== #


class CachedModule:
    """Wraps a DSPy module (or fallback) with deterministic LRU caching.

    Cache keys are SHA-256 hashes of the JSON-serialized keyword arguments,
    ensuring that identical inputs always produce a cache hit.

    Args:
        module: The callable module to wrap.
        cache_size: Maximum number of cached results to retain.
    """

    def __init__(self, module: Any, cache_size: int = 50) -> None:
        self._module = module
        self._cache: Dict[str, Any] = {}
        self._cache_order: deque[str] = deque(maxlen=cache_size)
        self._cache_size = cache_size
        self._hits = 0
        self._misses = 0

    def __call__(self, **kwargs: Any) -> Any:
        key = hashlib.sha256(
            json.dumps(kwargs, sort_keys=True, default=str).encode(),
        ).hexdigest()

        if key in self._cache:
            self._hits += 1
            logger.debug(
                "cache_hit",
                extra={"event": "cache_hit", "key": key[:12], "hits": self._hits},
            )
            return self._cache[key]

        self._misses += 1
        result = self._module(**kwargs)

        if len(self._cache) >= self._cache_size:
            oldest = self._cache_order.popleft()
            self._cache.pop(oldest, None)

        self._cache[key] = result
        self._cache_order.append(key)

        logger.debug(
            "cache_miss",
            extra={
                "event": "cache_miss",
                "key": key[:12],
                "misses": self._misses,
                "cache_size": len(self._cache),
            },
        )
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Return cache hit/miss statistics."""
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total else 0.0,
            "cache_size": len(self._cache),
            "max_cache_size": self._cache_size,
        }

    def clear(self) -> None:
        """Clear the cache and reset statistics."""
        self._cache.clear()
        self._cache_order.clear()
        self._hits = 0
        self._misses = 0
        logger.info("cache_cleared", extra={"event": "cache_cleared"})


# =========================================================================== #
#  Module registry & accessor                                                 #
# =========================================================================== #

_MODULE_REGISTRY: Dict[str, type] = {
    "report_quality": (
        ReportQualityModule if _dspy_available else FallbackReportQuality
    ),
    "field_mapping": (
        FieldMappingModule if _dspy_available else FallbackFieldMapping
    ),
    "query_classifier": (
        QueryClassifierModule if _dspy_available else FallbackQueryClassifier
    ),
    "sql_validator": (
        SQLValidatorModule if _dspy_available else FallbackSQLValidator
    ),
    "content_summarizer": (
        ContentSummarizerModule if _dspy_available else FallbackContentSummarizer
    ),
}

_module_cache: Dict[str, Any] = {}


def get_module(name: str, cached: bool = True) -> Any:
    """Retrieve a module instance by name, optionally wrapped with caching.

    Args:
        name: One of ``report_quality``, ``field_mapping``,
              ``query_classifier``, ``sql_validator``,
              ``content_summarizer``.
        cached: If ``True`` (default), wrap the module in a
                :class:`CachedModule` for LRU caching.

    Returns:
        A callable module (DSPy Module or fallback), optionally cached.

    Raises:
        KeyError: If *name* is not a registered module.
    """
    if name not in _MODULE_REGISTRY:
        raise KeyError(
            f"Unknown module: {name!r}. Available: {sorted(_MODULE_REGISTRY)}"
        )

    if name in _module_cache:
        return _module_cache[name]

    module_cls = _MODULE_REGISTRY[name]
    module = module_cls()

    if cached:
        module = CachedModule(module)

    _module_cache[name] = module
    logger.info(
        "module_loaded",
        extra={
            "event": "module_loaded",
            "module": name,
            "dspy": _dspy_available,
            "cached": cached,
        },
    )
    return module


def available_modules() -> list[str]:
    """Return the names of all registered modules."""
    return sorted(_MODULE_REGISTRY)


def reset_module_cache() -> None:
    """Clear the module instance cache, forcing re-creation on next access."""
    _module_cache.clear()
    logger.info("module_cache_reset", extra={"event": "module_cache_reset"})
