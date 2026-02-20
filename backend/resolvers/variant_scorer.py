"""
Variant scorer — multi-signal variant selection (legacy fallback).

Scoring signals:
1. Question intent — anomaly/baseline/comparison/trend/correlation/health
2. Query type — status/analysis/comparison/trend/diagnostic/overview/alert/forecast
3. Data shape — entity count, metric count, instance count
4. Default bonus — slight preference for the scenario default variant

The primary selection pipeline uses LangGraph + LlamaIndex + DSPy
(selection_graph.py). This module provides VariantProfile definitions
and data shape scoring used by both the new pipeline and fallback.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ── Variant Profile ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class VariantProfile:
    """Multi-signal fitness profile for a single variant."""

    # Weighted phrase patterns: [(phrase_or_regex, weight), ...]
    # Weight range: 0.0-1.0. Matched against query+question text.
    text_signals: tuple[tuple[str, float], ...] = ()

    # Which question intents this variant excels at.
    # Values: baseline, trend, anomaly, comparison, correlation, health
    intent_affinity: dict[str, float] = field(default_factory=dict)

    # Which query types boost this variant.
    # Values: status, analysis, comparison, trend, diagnostic, overview, alert, forecast
    query_type_affinity: dict[str, float] = field(default_factory=dict)

    # Data shape preferences. None = don't care.
    ideal_entity_count: tuple[int, int] | None = None  # (min, max) inclusive
    ideal_metric_count: tuple[int, int] | None = None
    ideal_instance_count: tuple[int, int] | None = None
    needs_multiple_entities: bool = False
    needs_timeseries: bool = False

    # Whether this is the scenario default (gets small tiebreaker bonus)
    is_default: bool = False


# ── Scoring Weights ──────────────────────────────────────────────────────────

_W_TEXT = 0.40       # Text phrase matching
_W_INTENT = 0.20     # Question intent alignment
_W_QUERY_TYPE = 0.15 # Query type alignment
_W_DATA_SHAPE = 0.20 # Data shape fitness
_W_DEFAULT = 0.05    # Default variant tiebreaker


# ── Scoring Functions ────────────────────────────────────────────────────────

def _score_text(profile: VariantProfile, text: str) -> float:
    """Score text affinity: check all phrase patterns against the text.

    Returns max matching weight (not sum) to avoid double-counting overlapping
    phrases. E.g., "pareto" and "80/20" both suggest pareto-bar — we want
    the stronger signal, not both added.
    """
    if not profile.text_signals or not text:
        return 0.0

    best = 0.0
    for phrase, weight in profile.text_signals:
        # Support both literal substring and regex
        if phrase.startswith("r:"):
            if re.search(phrase[2:], text, re.IGNORECASE):
                best = max(best, weight)
        elif phrase in text:
            best = max(best, weight)
    return best


def _score_intent(profile: VariantProfile, question_intent: str) -> float:
    """Score question intent alignment."""
    if not profile.intent_affinity or not question_intent:
        return 0.0
    return profile.intent_affinity.get(question_intent, 0.0)


def _score_query_type(profile: VariantProfile, query_type: str) -> float:
    """Score query type alignment."""
    if not profile.query_type_affinity or not query_type:
        return 0.0
    return profile.query_type_affinity.get(query_type, 0.0)


def _score_data_shape(
    profile: VariantProfile,
    entity_count: int,
    metric_count: int,
    instance_count: int,
) -> float:
    """Score data shape fitness.

    Returns 1.0 if data shape is ideal, degrades as it moves away from ideal.
    Returns 0.0 if hard requirements are violated (needs_multiple but only 1).
    """
    if profile.needs_multiple_entities and entity_count < 2:
        return 0.0

    score = 0.5  # Neutral baseline if no shape preferences

    checks = 0
    total = 0.0

    if profile.ideal_entity_count is not None:
        checks += 1
        lo, hi = profile.ideal_entity_count
        if lo <= entity_count <= hi:
            total += 1.0
        elif entity_count < lo:
            total += max(0.0, 1.0 - (lo - entity_count) * 0.3)
        else:
            total += max(0.0, 1.0 - (entity_count - hi) * 0.15)

    if profile.ideal_metric_count is not None:
        checks += 1
        lo, hi = profile.ideal_metric_count
        if lo <= metric_count <= hi:
            total += 1.0
        elif metric_count < lo:
            total += max(0.0, 1.0 - (lo - metric_count) * 0.3)
        else:
            total += max(0.0, 1.0 - (metric_count - hi) * 0.1)

    if profile.ideal_instance_count is not None:
        checks += 1
        lo, hi = profile.ideal_instance_count
        if lo <= instance_count <= hi:
            total += 1.0
        elif instance_count < lo:
            total += max(0.0, 1.0 - (lo - instance_count) * 0.3)
        else:
            total += max(0.0, 1.0 - (instance_count - hi) * 0.1)

    if checks > 0:
        score = total / checks

    return score


def score_variant(
    variant: str,
    profile: VariantProfile,
    text: str,
    question_intent: str,
    query_type: str,
    entity_count: int,
    metric_count: int,
    instance_count: int,
) -> float:
    """Compute weighted composite score for a variant."""
    s_text = _score_text(profile, text)
    s_intent = _score_intent(profile, question_intent)
    s_qtype = _score_query_type(profile, query_type)
    s_data = _score_data_shape(profile, entity_count, metric_count, instance_count)
    s_default = 1.0 if profile.is_default else 0.0

    total = (
        _W_TEXT * s_text
        + _W_INTENT * s_intent
        + _W_QUERY_TYPE * s_qtype
        + _W_DATA_SHAPE * s_data
        + _W_DEFAULT * s_default
    )
    return total


def choose_variant(
    scenario: str,
    text: str,
    question_intent: str = "",
    query_type: str = "overview",
    entity_count: int = 1,
    metric_count: int = 1,
    instance_count: int = 1,
) -> str:
    """Choose the best variant for a scenario using multi-signal scoring.

    Args:
        scenario: Widget scenario (e.g., "comparison")
        text: Combined query + question text (lowercased)
        question_intent: From question_dict (baseline/trend/anomaly/comparison/correlation/health)
        query_type: From ParsedIntent.query_type (status/analysis/comparison/trend/...)
        entity_count: Number of resolved entities
        metric_count: Number of metrics (columns) available
        instance_count: Number of table instances (e.g., TRF-001, TRF-002)

    Returns:
        Best variant key (e.g., "comparison-waterfall")
    """
    profiles = VARIANT_PROFILES.get(scenario)
    if not profiles:
        # Single-variant scenario or unknown — return scenario name
        return scenario

    best_variant = scenario
    best_score = -1.0

    for variant, profile in profiles.items():
        s = score_variant(
            variant, profile, text, question_intent, query_type,
            entity_count, metric_count, instance_count,
        )
        if s > best_score:
            best_score = s
            best_variant = variant

    logger.debug(f"[VariantScorer] {scenario} -> {best_variant} (score={best_score:.3f})")
    return best_variant


# ═════════════════════════════════════════════════════════════════════════════
# VARIANT PROFILES — One per variant, across all multi-variant scenarios
# ═════════════════════════════════════════════════════════════════════════════

VARIANT_PROFILES: dict[str, dict[str, VariantProfile]] = {

    # ── KPI ───────────────────────────────────────────────────────────────────
    "kpi": {
        "kpi-live": VariantProfile(
            intent_affinity={"baseline": 0.9, "health": 0.5, "trend": 0.3},
            query_type_affinity={"status": 0.8, "overview": 0.7, "trend": 0.4},
            ideal_entity_count=(1, 3),
            ideal_metric_count=(1, 2),
            is_default=True,
        ),
        "kpi-alert": VariantProfile(
            intent_affinity={"anomaly": 0.9, "health": 0.6},
            query_type_affinity={"alert": 0.9, "diagnostic": 0.6, "status": 0.5},
            ideal_entity_count=(1, 2),
        ),
        "kpi-accumulated": VariantProfile(
            intent_affinity={"baseline": 0.8, "trend": 0.5},
            query_type_affinity={"overview": 0.7, "status": 0.5, "analysis": 0.5},
            ideal_entity_count=(1, 2),
        ),
        "kpi-lifecycle": VariantProfile(
            intent_affinity={"health": 0.9, "baseline": 0.7},
            query_type_affinity={"diagnostic": 0.8, "status": 0.6, "forecast": 0.7},
            ideal_entity_count=(1, 2),
        ),
        "kpi-status": VariantProfile(
            intent_affinity={"health": 0.8, "baseline": 0.5},
            query_type_affinity={"status": 0.9, "overview": 0.5, "diagnostic": 0.5},
            ideal_entity_count=(1, 5),
        ),
    },

    # ── Trend ─────────────────────────────────────────────────────────────────
    "trend": {
        "trend-line": VariantProfile(
            intent_affinity={"trend": 0.8, "baseline": 0.5, "correlation": 0.4},
            query_type_affinity={"trend": 0.8, "analysis": 0.6, "overview": 0.5},
            ideal_entity_count=(1, 2),
            ideal_metric_count=(1, 1),
            is_default=True,
        ),
        "trend-area": VariantProfile(
            intent_affinity={"trend": 0.8, "baseline": 0.5},
            query_type_affinity={"trend": 0.8, "analysis": 0.6, "overview": 0.5},
            ideal_entity_count=(1, 2),
            ideal_metric_count=(1, 1),
        ),
        "trend-step-line": VariantProfile(
            intent_affinity={"health": 0.6, "baseline": 0.5, "anomaly": 0.5, "trend": 0.6},
            query_type_affinity={"status": 0.7, "diagnostic": 0.6, "trend": 0.6},
            ideal_entity_count=(1, 2),
            ideal_metric_count=(1, 1),
        ),
        "trend-rgb-phase": VariantProfile(
            intent_affinity={"trend": 0.7, "baseline": 0.6, "anomaly": 0.7, "comparison": 0.5},
            query_type_affinity={"trend": 0.7, "analysis": 0.7, "diagnostic": 0.8, "status": 0.5},
            ideal_entity_count=(1, 1),
            ideal_metric_count=(3, 3),
        ),
        "trend-alert-context": VariantProfile(
            intent_affinity={"anomaly": 0.9, "health": 0.6, "trend": 0.5},
            query_type_affinity={"alert": 0.9, "diagnostic": 0.7, "analysis": 0.5},
            ideal_entity_count=(1, 2),
            ideal_metric_count=(1, 2),
        ),
        "trend-heatmap": VariantProfile(
            intent_affinity={"trend": 0.7, "anomaly": 0.6, "correlation": 0.5},
            query_type_affinity={"analysis": 0.8, "trend": 0.6, "overview": 0.5},
            ideal_entity_count=(1, 2),
            ideal_metric_count=(1, 2),
        ),
    },

    # ── Comparison ────────────────────────────────────────────────────────────
    "comparison": {
        "comparison-side-by-side": VariantProfile(
            intent_affinity={"comparison": 0.8, "baseline": 0.5},
            query_type_affinity={"comparison": 0.8, "status": 0.5, "overview": 0.5},
            ideal_entity_count=(2, 2),
            ideal_instance_count=(2, 4),
            is_default=True,
        ),
        "comparison-delta-bar": VariantProfile(
            intent_affinity={"comparison": 0.8, "anomaly": 0.7, "baseline": 0.4},
            query_type_affinity={"comparison": 0.8, "analysis": 0.7, "diagnostic": 0.6},
            ideal_entity_count=(2, 6),
            ideal_instance_count=(2, 8),
        ),
        "comparison-grouped-bar": VariantProfile(
            intent_affinity={"comparison": 0.8, "baseline": 0.4},
            query_type_affinity={"comparison": 0.8, "analysis": 0.7},
            ideal_entity_count=(2, 5),
            ideal_metric_count=(3, 8),
            needs_multiple_entities=True,
        ),
        "comparison-waterfall": VariantProfile(
            intent_affinity={"comparison": 0.7, "anomaly": 0.5, "health": 0.4},
            query_type_affinity={"analysis": 0.8, "diagnostic": 0.6, "comparison": 0.6},
            ideal_entity_count=(1, 3),
            ideal_metric_count=(3, 10),
        ),
        "comparison-small-multiples": VariantProfile(
            intent_affinity={"comparison": 0.7, "baseline": 0.5, "health": 0.5},
            query_type_affinity={"overview": 0.8, "comparison": 0.7, "status": 0.6},
            ideal_entity_count=(4, 20),
            ideal_instance_count=(4, 20),
            needs_multiple_entities=True,
        ),
        "comparison-composition-split": VariantProfile(
            intent_affinity={"comparison": 0.7, "baseline": 0.3},
            query_type_affinity={"comparison": 0.7, "analysis": 0.7},
            ideal_entity_count=(2, 3),
            ideal_metric_count=(3, 8),
            needs_multiple_entities=True,
        ),
    },

    # ── Distribution ──────────────────────────────────────────────────────────
    "distribution": {
        "distribution-donut": VariantProfile(
            intent_affinity={"baseline": 0.7, "comparison": 0.5},
            query_type_affinity={"overview": 0.8, "analysis": 0.7, "status": 0.5},
            ideal_metric_count=(2, 7),
            is_default=True,
        ),
        "distribution-pie": VariantProfile(
            intent_affinity={"baseline": 0.6},
            query_type_affinity={"overview": 0.6, "status": 0.4},
            ideal_metric_count=(2, 5),  # Pie is bad with >5 slices
        ),
        "distribution-horizontal-bar": VariantProfile(
            intent_affinity={"comparison": 0.7, "baseline": 0.5},
            query_type_affinity={"analysis": 0.7, "comparison": 0.6, "overview": 0.5},
            ideal_metric_count=(4, 20),  # Good for many items
        ),
        "distribution-pareto-bar": VariantProfile(
            intent_affinity={"anomaly": 0.7, "comparison": 0.6, "health": 0.5, "baseline": 0.4},
            query_type_affinity={"diagnostic": 0.8, "analysis": 0.8},
            ideal_metric_count=(4, 15),
        ),
        "distribution-grouped-bar": VariantProfile(
            intent_affinity={"comparison": 0.7, "baseline": 0.4},
            query_type_affinity={"comparison": 0.7, "analysis": 0.7},
            ideal_metric_count=(3, 10),
            ideal_entity_count=(2, 6),
            needs_multiple_entities=True,
        ),
        "distribution-100-stacked-bar": VariantProfile(
            intent_affinity={"comparison": 0.7, "baseline": 0.4},
            query_type_affinity={"comparison": 0.7, "analysis": 0.7},
            ideal_metric_count=(3, 10),
        ),
    },

    # ── Composition ───────────────────────────────────────────────────────────
    "composition": {
        "composition-stacked-bar": VariantProfile(
            intent_affinity={"baseline": 0.7, "comparison": 0.5},
            query_type_affinity={"analysis": 0.7, "overview": 0.7, "comparison": 0.5},
            ideal_metric_count=(2, 8),
            is_default=True,
        ),
        "composition-stacked-area": VariantProfile(
            intent_affinity={"trend": 0.8, "comparison": 0.5},
            query_type_affinity={"trend": 0.8, "analysis": 0.7},
            needs_timeseries=True,
            ideal_metric_count=(2, 6),
        ),
        "composition-donut": VariantProfile(
            intent_affinity={"baseline": 0.7, "health": 0.4},
            query_type_affinity={"overview": 0.7, "status": 0.6},
            ideal_metric_count=(2, 6),
        ),
        "composition-waterfall": VariantProfile(
            intent_affinity={"comparison": 0.6, "anomaly": 0.5, "baseline": 0.3},
            query_type_affinity={"analysis": 0.8, "diagnostic": 0.6},
            ideal_metric_count=(3, 10),
        ),
        "composition-treemap": VariantProfile(
            intent_affinity={"baseline": 0.5, "comparison": 0.5},
            query_type_affinity={"analysis": 0.7, "overview": 0.7},
            ideal_metric_count=(2, 30),  # Treemap works with fewer items too
        ),
    },

    # ── Alerts ────────────────────────────────────────────────────────────────
    "alerts": {
        "alerts-card": VariantProfile(
            intent_affinity={"anomaly": 0.7, "health": 0.5},
            query_type_affinity={"alert": 0.6, "status": 0.5, "overview": 0.4},
            is_default=True,
        ),
        "alerts-banner": VariantProfile(
            intent_affinity={"anomaly": 0.7},
            query_type_affinity={"alert": 0.7},
        ),
        "alerts-toast": VariantProfile(
            intent_affinity={"anomaly": 0.6},
            query_type_affinity={"alert": 0.6},
        ),
        "alerts-badge": VariantProfile(
            intent_affinity={"health": 0.6, "baseline": 0.4},
            query_type_affinity={"status": 0.7, "overview": 0.6},
        ),
        "alerts-modal": VariantProfile(
            intent_affinity={"anomaly": 0.8, "health": 0.5},
            query_type_affinity={"diagnostic": 0.8, "alert": 0.7},
        ),
    },

    # ── Timeline ──────────────────────────────────────────────────────────────
    "timeline": {
        "timeline-linear": VariantProfile(
            intent_affinity={"trend": 0.5, "baseline": 0.4, "anomaly": 0.4},
            query_type_affinity={"overview": 0.5, "status": 0.4, "analysis": 0.4},
            is_default=True,
        ),
        "timeline-status": VariantProfile(
            intent_affinity={"health": 0.8, "baseline": 0.5, "trend": 0.5},
            query_type_affinity={"status": 0.9, "diagnostic": 0.6},
        ),
        "timeline-multilane": VariantProfile(
            intent_affinity={"comparison": 0.7, "baseline": 0.4},
            query_type_affinity={"overview": 0.6, "comparison": 0.6},
            ideal_entity_count=(2, 10),
        ),
        "timeline-forensic": VariantProfile(
            intent_affinity={"anomaly": 0.9, "health": 0.6},
            query_type_affinity={"diagnostic": 0.9, "alert": 0.6},
        ),
        "timeline-dense": VariantProfile(
            intent_affinity={"anomaly": 0.7, "trend": 0.5, "baseline": 0.5},
            query_type_affinity={"diagnostic": 0.7, "analysis": 0.6, "overview": 0.5},
        ),
    },

    # ── EventLogStream ────────────────────────────────────────────────────────
    "eventlogstream": {
        "eventlogstream-chronological": VariantProfile(
            intent_affinity={"baseline": 0.5, "anomaly": 0.4},
            query_type_affinity={"overview": 0.5, "status": 0.5},
            is_default=True,
        ),
        "eventlogstream-compact-feed": VariantProfile(
            intent_affinity={"baseline": 0.5},
            query_type_affinity={"overview": 0.6, "status": 0.5},
        ),
        "eventlogstream-tabular": VariantProfile(
            intent_affinity={"baseline": 0.5, "comparison": 0.4},
            query_type_affinity={"analysis": 0.7, "overview": 0.5},
        ),
        "eventlogstream-correlation": VariantProfile(
            intent_affinity={"correlation": 0.9, "anomaly": 0.6},
            query_type_affinity={"diagnostic": 0.8, "analysis": 0.7},
        ),
        "eventlogstream-grouped-asset": VariantProfile(
            intent_affinity={"comparison": 0.6, "baseline": 0.4},
            query_type_affinity={"overview": 0.6, "comparison": 0.6},
            ideal_entity_count=(2, 10),
        ),
    },

    # ── Category-Bar ──────────────────────────────────────────────────────────
    "category-bar": {
        "category-bar-vertical": VariantProfile(
            intent_affinity={"comparison": 0.6, "baseline": 0.5},
            query_type_affinity={"comparison": 0.6, "overview": 0.5},
            ideal_metric_count=(2, 8),
            is_default=True,
        ),
        "category-bar-horizontal": VariantProfile(
            intent_affinity={"comparison": 0.6, "baseline": 0.6},
            query_type_affinity={"comparison": 0.6, "overview": 0.6, "analysis": 0.5},
            ideal_metric_count=(1, 20),
        ),
        "category-bar-stacked": VariantProfile(
            intent_affinity={"comparison": 0.6, "baseline": 0.4},
            query_type_affinity={"analysis": 0.7, "comparison": 0.6},
            ideal_metric_count=(3, 10),
        ),
        "category-bar-grouped": VariantProfile(
            intent_affinity={"comparison": 0.8, "baseline": 0.4},
            query_type_affinity={"comparison": 0.8, "analysis": 0.7},
            ideal_metric_count=(2, 5),
        ),
        "category-bar-diverging": VariantProfile(
            intent_affinity={"anomaly": 0.7, "comparison": 0.7},
            query_type_affinity={"analysis": 0.8, "diagnostic": 0.6, "comparison": 0.6},
        ),
    },

    # ── Flow-Sankey ───────────────────────────────────────────────────────────
    "flow-sankey": {
        "flow-sankey-standard": VariantProfile(
            intent_affinity={"baseline": 0.5, "comparison": 0.4},
            query_type_affinity={"analysis": 0.6, "overview": 0.5},
            is_default=True,
        ),
        "flow-sankey-energy-balance": VariantProfile(
            intent_affinity={"anomaly": 0.6, "health": 0.5, "baseline": 0.4},
            query_type_affinity={"analysis": 0.8, "diagnostic": 0.6},
        ),
        "flow-sankey-multi-source": VariantProfile(
            intent_affinity={"baseline": 0.5, "comparison": 0.5},
            query_type_affinity={"analysis": 0.7},
            ideal_entity_count=(3, 10),
        ),
        "flow-sankey-layered": VariantProfile(
            intent_affinity={"baseline": 0.5},
            query_type_affinity={"analysis": 0.7, "overview": 0.5},
        ),
        "flow-sankey-time-sliced": VariantProfile(
            intent_affinity={"trend": 0.8, "comparison": 0.5},
            query_type_affinity={"trend": 0.7, "analysis": 0.7},
            needs_timeseries=True,
        ),
    },

    # ── Matrix-Heatmap ────────────────────────────────────────────────────────
    "matrix-heatmap": {
        "matrix-heatmap-value": VariantProfile(
            intent_affinity={"baseline": 0.5, "comparison": 0.5},
            query_type_affinity={"overview": 0.6, "analysis": 0.6, "status": 0.5},
            is_default=True,
        ),
        "matrix-heatmap-correlation": VariantProfile(
            intent_affinity={"correlation": 0.95, "comparison": 0.4},
            query_type_affinity={"analysis": 0.9, "diagnostic": 0.5},
            ideal_metric_count=(3, 20),
        ),
        "matrix-heatmap-calendar": VariantProfile(
            intent_affinity={"trend": 0.7, "anomaly": 0.5},
            query_type_affinity={"analysis": 0.7, "trend": 0.7},
        ),
        "matrix-heatmap-status": VariantProfile(
            intent_affinity={"health": 0.9, "baseline": 0.5, "anomaly": 0.5},
            query_type_affinity={"status": 0.9, "diagnostic": 0.7, "overview": 0.6},
            ideal_entity_count=(3, 20),
        ),
        "matrix-heatmap-density": VariantProfile(
            intent_affinity={"anomaly": 0.6, "baseline": 0.4},
            query_type_affinity={"analysis": 0.7, "diagnostic": 0.5},
        ),
    },
}
