from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("neura.optimization.signatures")

# ---------------------------------------------------------------------------
# Optional dependency: DSPy
# ---------------------------------------------------------------------------
_dspy_available = False
try:
    import dspy

    _dspy_available = True
    logger.debug("dspy_available", extra={"event": "dspy_available"})
except ImportError:
    logger.debug(
        "dspy_unavailable",
        extra={"event": "dspy_unavailable", "fallback": "stub"},
    )


# =========================================================================== #
#  DSPy Signature classes (only defined when DSPy is installed)               #
# =========================================================================== #

if _dspy_available:

    class ReportQualityAssessment(dspy.Signature):
        """Assess the quality of a generated report."""

        report_content: str = dspy.InputField(
            desc="The full report content to assess",
        )
        context: str = dspy.InputField(
            desc="Original requirements and data context",
        )

        quality_score: str = dspy.OutputField(
            desc="Quality score from 0.0 to 1.0",
        )
        issues: str = dspy.OutputField(desc="List of issues found")
        suggestions: str = dspy.OutputField(desc="Improvement suggestions")

    class FieldMappingReasoner(dspy.Signature):
        """Reason about the best field mapping between source columns and target template fields."""

        source_columns: str = dspy.InputField(
            desc="Comma-separated source column names",
        )
        target_fields: str = dspy.InputField(
            desc="Comma-separated target template field names",
        )
        context: str = dspy.InputField(
            desc="Additional context about the data domain",
        )

        mappings: str = dspy.OutputField(
            desc="JSON mapping of source columns to target fields",
        )
        confidence: str = dspy.OutputField(
            desc="Confidence score from 0.0 to 1.0",
        )
        reasoning: str = dspy.OutputField(
            desc="Step-by-step reasoning for the chosen mappings",
        )

    class QueryClassifier(dspy.Signature):
        """Classify a natural language query by type and intent."""

        query: str = dspy.InputField(
            desc="The natural language query to classify",
        )
        available_types: str = dspy.InputField(
            desc="Comma-separated list of valid query types",
        )

        query_type: str = dspy.OutputField(
            desc="The classified query type",
        )
        intent: str = dspy.OutputField(
            desc="The underlying intent of the query",
        )
        entities: str = dspy.OutputField(
            desc="Extracted entities as JSON list",
        )

    class SQLValidator(dspy.Signature):
        """Validate and optionally correct a SQL query."""

        sql_query: str = dspy.InputField(
            desc="The SQL query to validate",
        )
        schema_context: str = dspy.InputField(
            desc="Database schema information for validation",
        )

        is_valid: str = dspy.OutputField(
            desc="Whether the SQL is valid (true/false)",
        )
        issues: str = dspy.OutputField(
            desc="List of validation issues found",
        )
        corrected_sql: str = dspy.OutputField(
            desc="Corrected SQL query if issues were found",
        )

    class ContentSummarizer(dspy.Signature):
        """Summarize content to a target length while preserving key information."""

        content: str = dspy.InputField(
            desc="The content to summarize",
        )
        max_length: str = dspy.InputField(
            desc="Target maximum length in characters",
        )

        summary: str = dspy.OutputField(
            desc="The summarized content",
        )
        key_points: str = dspy.OutputField(
            desc="Bullet-point list of key information preserved",
        )


# =========================================================================== #
#  Stub fallbacks (used when DSPy is NOT installed)                           #
# =========================================================================== #


@dataclass
class StubPrediction:
    """Mimics dspy.Prediction when DSPy is not installed."""

    _data: Dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return self._data.get(name, "")

    def __repr__(self) -> str:
        return f"StubPrediction({self._data})"


def stub_report_quality(
    report_content: str,
    context: str = "",
) -> StubPrediction:
    """Stub fallback for ReportQualityAssessment."""
    logger.warning("stub_report_quality called; DSPy unavailable")
    return StubPrediction(
        _data={
            "quality_score": "0.5",
            "issues": "DSPy unavailable",
            "suggestions": "",
        },
    )


def stub_field_mapping(
    source_columns: str,
    target_fields: str,
    context: str = "",
) -> StubPrediction:
    """Stub fallback for FieldMappingReasoner."""
    logger.warning("stub_field_mapping called; DSPy unavailable")
    return StubPrediction(
        _data={
            "mappings": "{}",
            "confidence": "0.0",
            "reasoning": "DSPy unavailable; no reasoning performed",
        },
    )


def stub_query_classifier(
    query: str,
    available_types: str = "",
) -> StubPrediction:
    """Stub fallback for QueryClassifier."""
    logger.warning("stub_query_classifier called; DSPy unavailable")
    return StubPrediction(
        _data={
            "query_type": "unknown",
            "intent": "unknown",
            "entities": "[]",
        },
    )


def stub_sql_validator(
    sql_query: str,
    schema_context: str = "",
) -> StubPrediction:
    """Stub fallback for SQLValidator."""
    logger.warning("stub_sql_validator called; DSPy unavailable")
    return StubPrediction(
        _data={
            "is_valid": "true",
            "issues": "DSPy unavailable; validation skipped",
            "corrected_sql": sql_query,
        },
    )


def stub_content_summarizer(
    content: str,
    max_length: str = "500",
) -> StubPrediction:
    """Stub fallback for ContentSummarizer."""
    logger.warning("stub_content_summarizer called; DSPy unavailable")
    limit = int(max_length) if max_length.isdigit() else 500
    truncated = content[:limit] if len(content) > limit else content
    return StubPrediction(
        _data={
            "summary": truncated,
            "key_points": "DSPy unavailable; content truncated only",
        },
    )


# =========================================================================== #
#  Registry & public API                                                      #
# =========================================================================== #

_SIGNATURE_REGISTRY: Dict[str, Any] = {}

if _dspy_available:
    _SIGNATURE_REGISTRY = {
        "report_quality": ReportQualityAssessment,
        "field_mapping": FieldMappingReasoner,
        "query_classifier": QueryClassifier,
        "sql_validator": SQLValidator,
        "content_summarizer": ContentSummarizer,
    }
else:
    _SIGNATURE_REGISTRY = {
        "report_quality": stub_report_quality,
        "field_mapping": stub_field_mapping,
        "query_classifier": stub_query_classifier,
        "sql_validator": stub_sql_validator,
        "content_summarizer": stub_content_summarizer,
    }


def get_signature(name: str) -> Any:
    """Get a signature class or stub function by name.

    When DSPy is installed the returned value is a ``dspy.Signature``
    subclass suitable for use with ``dspy.Predict``, ``dspy.ChainOfThought``,
    etc.  When DSPy is **not** installed a plain callable stub is returned
    that accepts the same keyword arguments and returns a
    :class:`StubPrediction`.

    Args:
        name: One of ``report_quality``, ``field_mapping``,
              ``query_classifier``, ``sql_validator``,
              ``content_summarizer``.

    Returns:
        A DSPy Signature class **or** a stub callable.

    Raises:
        KeyError: If *name* is not a registered signature.
    """
    if name not in _SIGNATURE_REGISTRY:
        available = ", ".join(sorted(_SIGNATURE_REGISTRY))
        raise KeyError(
            f"Unknown signature '{name}'. Available: {available}"
        )
    return _SIGNATURE_REGISTRY[name]


def available_signatures() -> List[str]:
    """Return the names of all registered signatures."""
    return sorted(_SIGNATURE_REGISTRY)


def is_dspy_available() -> bool:
    """Check whether DSPy is installed and signatures are native."""
    return _dspy_available
