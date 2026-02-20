"""
LangGraph constraint graph for widget variant selection.

Three-layer pipeline with conditional routing:
  Layer 1: LlamaIndex MetadataFilters — hard elimination
  Layer 2: Data shape + intent scoring — ranked composite
  Layer 2.5: Semantic tie-breaker — embedding-based disambiguation (when ambiguous)
  Layer 3: DSPy ChainOfThought — reasoned tie-breaking (when still ambiguous)
  Layer 3.5: AutoGen validator — deterministic validation fallback

Graph topology:
  START → profile_data → hard_filter ─┬─ sole_survivor → finalize → END
                                       └─ multiple → score_shape → score_intent
                                         → apply_penalties → rank ─┬─ high → finalize → END
                                                                   └─ low → semantic_tiebreak ─┬─ resolved → finalize → END
                                                                                               └─ still_ambiguous → dspy_reason ─┬─ ok → finalize → END
                                                                                                                          └─ fallback → autogen_validate → finalize → END

Scoring weights (Layer 2): data_shape=0.40, intent=0.25, query_type=0.15, penalties=0.15, default=0.05
Layer 2 is fully data-driven (no keyword heuristics). Semantic embeddings are
used only as a low-confidence tie-breaker (Layer 2.5).
"""

from __future__ import annotations

import logging
from typing import Any, TypedDict

logger = logging.getLogger(__name__)

# ── Try to import LangGraph ─────────────────────────────────────────────────

_langgraph_available = False
try:
    from langgraph.graph import StateGraph, START, END
    _langgraph_available = True
    logger.debug("[SelectionGraph] LangGraph available")
except ImportError:
    logger.debug("[SelectionGraph] LangGraph not available, using sequential fallback")


# ── Scoring weights ──────────────────────────────────────────────────────────

W_SHAPE = 0.35
W_INTENT = 0.20
W_QUERY_TYPE = 0.10
W_PENALTIES = 0.30
W_DEFAULT = 0.05


# ── Graph State ─────────────────────────────────────────────────────────────

class SelectionState(TypedDict, total=False):
    # Inputs
    scenario: str
    query_text: str
    question_intent: str
    query_type: str
    entity_count: int
    metric_count: int
    instance_count: int
    has_timeseries: bool
    catalog: Any
    data_profile: Any
    intent: Any
    query_embedding: list[float] | None
    embedding_client: Any

    # Pipeline state — extracted data shape profile
    _data_shape: Any  # DataShapeProfile (must be in TypedDict for LangGraph)

    # Pipeline state — scoring
    all_variants: list[str]
    survivors: list[str]
    elimination_log: dict[str, list[str]]
    shape_scores: dict[str, float]
    intent_scores: dict[str, float]
    qtype_scores: dict[str, float]
    penalty_scores: dict[str, float]
    composite_scores: dict[str, float]
    semantic_scores: dict[str, float]

    dspy_needed: bool
    dspy_selection: str
    dspy_reasoning: str
    autogen_reason: str

    # Output
    selected_variant: str
    confidence: float
    method: str


# ── Pipeline Nodes ──────────────────────────────────────────────────────────

def node_profile_data(state: SelectionState) -> dict:
    """Node 1: Extract DataShapeProfile from catalog."""
    from backend.resolvers.data_shape import extract_data_shape, DataShapeProfile

    catalog = state.get("catalog")
    profile = state.get("data_profile")
    intent = state.get("intent")

    shape = extract_data_shape(catalog, profile, intent)

    return {"_data_shape": shape}


def node_hard_filter(state: SelectionState) -> dict:
    """Node 2: Hard elimination using LlamaIndex MetadataFilters."""
    from backend.resolvers.variant_metadata import filter_variants
    from backend.resolvers.variant_scorer import VARIANT_PROFILES

    scenario = state["scenario"]
    shape = state.get("_data_shape")

    profiles = VARIANT_PROFILES.get(scenario, {})
    all_variants = list(profiles.keys()) if profiles else [scenario]

    if not profiles or shape is None:
        return {
            "all_variants": all_variants,
            "survivors": all_variants,
            "elimination_log": {},
        }

    survivors = filter_variants(scenario, shape)

    # Build elimination log
    eliminated = set(all_variants) - set(survivors)
    elimination_log: dict[str, list[str]] = {}
    for v in eliminated:
        reasons = []
        p = profiles.get(v)
        if p:
            if p.needs_timeseries and not shape.has_timeseries:
                reasons.append("requires_timeseries")
            if p.needs_multiple_entities and shape.entity_count < 2:
                reasons.append("requires_multiple_entities")
            if p.ideal_entity_count and shape.entity_count < p.ideal_entity_count[0]:
                reasons.append(f"min_entity_count={p.ideal_entity_count[0]}")
            if p.ideal_metric_count and shape.metric_count < p.ideal_metric_count[0]:
                reasons.append(f"min_metric_count={p.ideal_metric_count[0]}")
        elimination_log[v] = reasons or ["filtered_by_metadata"]

    logger.debug(
        f"[SelectionGraph] {scenario}: {len(all_variants)} → {len(survivors)} "
        f"(eliminated: {list(eliminated)})"
    )

    result = {
        "all_variants": all_variants,
        "survivors": survivors,
        "elimination_log": elimination_log,
    }

    # When sole survivor, set selected_variant for the finalize node
    # (LangGraph path skips rank node which normally sets this)
    if len(survivors) == 1:
        result["selected_variant"] = survivors[0]
        result["confidence"] = 1.0
        result["method"] = "filter_only"

    return result


def node_score_shape(state: SelectionState) -> dict:
    """Node 3: Score survivors by data shape fitness.

    Uses DataShapeProfile properties to compute how well each
    variant matches the actual data characteristics.
    """
    from backend.resolvers.variant_metadata import score_shape_fitness
    from backend.resolvers.variant_scorer import (
        VARIANT_PROFILES, _score_data_shape,
    )

    scenario = state["scenario"]
    survivors = state.get("survivors", [])
    shape = state.get("_data_shape")
    profiles = VARIANT_PROFILES.get(scenario, {})

    shape_scores: dict[str, float] = {}
    for variant in survivors:
        # Shape preference fitness (from variant_metadata.py)
        pref_score = score_shape_fitness(variant, shape) if shape else 0.5

        # Data count fitness (from variant_scorer.py)
        profile = profiles.get(variant)
        if profile:
            count_score = _score_data_shape(
                profile,
                shape.entity_count if shape else state.get("entity_count", 1),
                shape.metric_count if shape else state.get("metric_count", 1),
                shape.instance_count if shape else state.get("instance_count", 1),
            )
        else:
            count_score = 0.5

        # Blend: 60% preference fitness + 40% count fitness
        shape_scores[variant] = round(0.6 * pref_score + 0.4 * count_score, 4)

    return {"shape_scores": shape_scores}


def node_score_intent(state: SelectionState) -> dict:
    """Node 4: Score intent affinity + query type affinity."""
    from backend.resolvers.variant_metadata import (
        get_variant_intent_score, get_variant_qtype_score,
    )

    survivors = state.get("survivors", [])
    question_intent = state.get("question_intent", "")
    query_type = state.get("query_type", "overview")

    intent_scores: dict[str, float] = {}
    qtype_scores: dict[str, float] = {}

    for variant in survivors:
        intent_scores[variant] = get_variant_intent_score(variant, question_intent)
        qtype_scores[variant] = get_variant_qtype_score(variant, query_type)

    return {
        "intent_scores": intent_scores,
        "qtype_scores": qtype_scores,
    }


def node_apply_penalties(state: SelectionState) -> dict:
    """Node 5: Apply data-driven penalties.

    Bidirectional: boosts specialized variants AND penalizes generic/default
    variants when specific data signals are detected. This is the primary
    mechanism for reaching non-default variants.

    Uses both DataShapeProfile (primary) and intent/query_type context (secondary)
    for context-aware differentiation.
    """
    survivors = state.get("survivors", [])
    shape = state.get("_data_shape")
    question_intent = state.get("question_intent", "")
    query_type = state.get("query_type", "")

    penalty_scores: dict[str, float] = {}
    for variant in survivors:
        penalty = 0.0

        if shape:
            # ─── KPI differentiation ────────────────────────────
            if variant == "kpi-accumulated" and shape.has_cumulative_metric:
                penalty += 0.5
            if variant == "kpi-live" and shape.has_cumulative_metric:
                penalty -= 0.35
            if variant == "kpi-status" and shape.has_binary_metric:
                penalty += 0.45
            if variant == "kpi-live" and shape.has_binary_metric:
                penalty -= 0.3
            if variant == "kpi-lifecycle" and shape.has_percentage_metric:
                penalty += 0.4
            if variant == "kpi-live" and shape.has_percentage_metric and not shape.has_cumulative_metric:
                penalty -= 0.25
            if variant == "kpi-alert" and shape.has_alerts:
                penalty += 0.4
            if variant == "kpi-live" and shape.has_alerts:
                penalty -= 0.2

            # ─── Trend differentiation ──────────────────────────
            if variant == "trend-step-line" and shape.has_binary_metric:
                penalty += 0.5
            if variant == "trend-line" and shape.has_binary_metric:
                penalty -= 0.5
            if variant == "trend-rgb-phase" and shape.has_phase_data:
                penalty += 0.5
            if variant == "trend-line" and shape.has_phase_data:
                penalty -= 0.35
            if variant == "trend-rgb-phase" and not shape.has_phase_data:
                penalty -= 0.5
            if variant == "trend-step-line" and not shape.has_binary_metric:
                penalty -= 0.4
            if variant == "trend-heatmap" and shape.temporal_density > 100:
                penalty += 0.45
            if variant == "trend-line" and shape.temporal_density > 100 and shape.metric_count <= 2:
                penalty -= 0.25
            if variant == "trend-alert-context" and shape.has_alerts:
                penalty += 0.4
            if variant == "trend-line" and shape.has_alerts:
                penalty -= 0.2
            if variant == "trend-area" and shape.has_flow_metric:
                penalty += 0.35
            if variant == "trend-area" and shape.has_rate_metric:
                penalty += 0.3
            if variant == "trend-line" and (shape.has_flow_metric or shape.has_rate_metric):
                penalty -= 0.15

            # ─── Comparison differentiation ─────────────────────
            if variant == "comparison-side-by-side" and shape.entity_count <= 2 and shape.metric_count <= 3 and not shape.has_high_variance:
                penalty += 0.35  # Side-by-side for simple A-vs-B
            if variant == "comparison-side-by-side" and shape.has_high_variance and shape.metric_count >= 3:
                penalty -= 0.2  # Yield to waterfall when high variance + many metrics
            if variant == "comparison-side-by-side" and shape.entity_count > 3:
                penalty -= 0.3
            if variant == "comparison-grouped-bar" and shape.metric_count >= 4 and shape.entity_count >= 3:
                penalty += 0.45  # Strong: grouped-bar is ideal for many metrics + entities
            if variant == "comparison-grouped-bar" and shape.cross_entity_comparable:
                penalty += 0.1  # Extra boost for cross-entity
            if variant == "comparison-grouped-bar" and shape.metric_count < 3:
                penalty -= 0.2
            if variant == "comparison-delta-bar" and shape.entity_count >= 3 and shape.metric_count <= 2:
                penalty += 0.35
            if variant == "comparison-delta-bar" and shape.metric_count >= 4:
                penalty -= 0.25
            if variant == "comparison-waterfall" and shape.has_high_variance and shape.metric_count >= 3:
                penalty += 0.45  # Strong: waterfall for high variance breakdown
            if variant == "comparison-waterfall" and not shape.has_high_variance and shape.metric_count >= 3:
                penalty += 0.15
            if variant == "comparison-delta-bar" and shape.has_high_variance and shape.metric_count >= 3:
                penalty -= 0.15
            if variant == "comparison-small-multiples" and shape.entity_count >= 5:
                penalty += 0.45
            if variant == "comparison-small-multiples" and shape.entity_count >= 4:
                penalty += 0.3
            if variant == "comparison-small-multiples" and shape.entity_count < 3:
                penalty -= 0.4
            if variant == "comparison-delta-bar" and shape.entity_count >= 5:
                penalty -= 0.15
            if variant == "comparison-composition-split" and shape.entity_count <= 3 and shape.metric_count >= 3 and not shape.has_high_variance:
                penalty += 0.35  # Composition-split: compare makeup between few entities
            if variant == "comparison-composition-split" and shape.entity_count >= 3 and shape.metric_count >= 4:
                penalty -= 0.2  # Yield to grouped-bar when many entities + many metrics
            if variant == "comparison-composition-split" and shape.has_high_variance:
                penalty -= 0.15
            if variant == "comparison-composition-split" and shape.metric_count <= 2:
                penalty -= 0.2

            # ─── Distribution differentiation ───────────────────
            if variant == "distribution-pie" and shape.metric_count <= 3 and shape.entity_count <= 3:
                penalty += 0.3
            if variant == "distribution-donut" and shape.metric_count >= 4 and shape.metric_count <= 7 and not shape.has_high_variance:
                penalty += 0.3  # Donut for moderate metrics, no high variance
            if variant == "distribution-donut" and shape.metric_count <= 3 and shape.entity_count <= 3:
                penalty -= 0.05  # Slight yield to pie for very few categories
            if variant == "distribution-horizontal-bar" and shape.metric_count >= 4 and not shape.has_high_variance:
                penalty += 0.35  # Horizontal bar for many metrics, moderate variance
            if variant == "distribution-horizontal-bar" and shape.has_high_variance:
                penalty -= 0.15  # Yield to pareto when high variance
            if variant == "distribution-pareto-bar" and shape.has_high_variance and shape.metric_count >= 4:
                penalty += 0.35
            if variant == "distribution-pareto-bar" and not shape.has_high_variance:
                penalty -= 0.2  # Pareto needs high variance
            if variant == "distribution-100-stacked-bar" and shape.has_percentage_metric:
                penalty += 0.45  # Strong percentage signal
            if variant == "distribution-donut" and shape.has_percentage_metric:
                penalty -= 0.15  # Yield to 100-stacked when percentage
            if variant == "distribution-grouped-bar" and shape.entity_count >= 3 and shape.cross_entity_comparable:
                penalty += 0.3
            if variant == "distribution-grouped-bar" and shape.has_percentage_metric:
                penalty -= 0.15
            if variant in ("distribution-donut", "distribution-pie") and shape.metric_count > 7:
                penalty -= 0.3

            # ─── Composition differentiation ────────────────────
            if variant == "composition-donut" and shape.metric_count <= 4 and shape.entity_count <= 3:
                penalty += 0.35
            if variant == "composition-stacked-bar" and shape.metric_count <= 4 and shape.entity_count <= 3:
                penalty -= 0.2
            if variant == "composition-stacked-bar" and shape.entity_count >= 4 and not shape.has_hierarchy:
                penalty += 0.25
            if variant == "composition-waterfall" and shape.has_high_variance and shape.metric_count >= 3:
                penalty += 0.4
            if variant == "composition-stacked-bar" and shape.has_high_variance and shape.metric_count >= 3 and not shape.has_hierarchy:
                penalty -= 0.2
            if variant == "composition-treemap" and shape.has_high_variance and not shape.has_hierarchy:
                penalty -= 0.3
            if variant == "composition-treemap" and shape.has_hierarchy:
                penalty += 0.4
            if variant == "composition-stacked-area" and shape.temporal_density > 5:
                penalty += 0.3

            # ─── Alerts differentiation ─────────────────────────
            if variant == "alerts-card" and shape.entity_count >= 3:
                penalty += 0.25
            if variant == "alerts-banner" and shape.entity_count == 2:
                penalty += 0.4  # Banner for 2-entity site-wide
            if variant == "alerts-banner" and shape.entity_count == 1:
                penalty -= 0.1  # Banner less appropriate for single entity
            if variant == "alerts-card" and shape.entity_count <= 2:
                penalty -= 0.2
            if variant == "alerts-toast" and shape.entity_count == 1:
                penalty += 0.4  # Toast for single entity notifications
            if variant == "alerts-badge" and shape.entity_count >= 5:
                penalty += 0.35
            if variant == "alerts-card" and shape.entity_count >= 5:
                penalty -= 0.15
            # alerts-modal: investigation-focused — boost when diagnostic context
            if variant == "alerts-modal" and shape.entity_count <= 2 and shape.metric_count >= 2:
                penalty += 0.35
            if variant == "alerts-modal" and query_type == "diagnostic":
                penalty += 0.15
            if variant == "alerts-toast" and shape.metric_count >= 2:
                penalty -= 0.1

            # ─── Timeline differentiation ───────────────────────
            if variant == "timeline-linear" and not shape.has_binary_metric:
                penalty += 0.2
            if variant == "timeline-status" and shape.has_binary_metric:
                penalty += 0.4
            if variant == "timeline-linear" and shape.has_binary_metric:
                penalty -= 0.25
            if variant == "timeline-dense" and shape.temporal_density > 100:
                penalty += 0.4
            if variant == "timeline-forensic" and shape.temporal_density > 100 and not shape.has_alerts:
                penalty -= 0.2
            if variant == "timeline-multilane" and shape.entity_count >= 3:
                penalty += 0.3

            # ─── EventLogStream differentiation ─────────────────
            if variant == "eventlogstream-chronological" and shape.entity_count <= 2 and shape.metric_count <= 1:
                penalty += 0.3  # Chronological for truly simple data
            if variant == "eventlogstream-compact-feed" and shape.entity_count <= 2 and shape.metric_count >= 2:
                penalty += 0.35  # Compact for multi-metric small entity
            if variant == "eventlogstream-chronological" and shape.entity_count <= 2 and shape.metric_count >= 2:
                penalty -= 0.15  # Yield to compact when multi-metric
            if variant == "eventlogstream-compact-feed" and shape.metric_count <= 1:
                penalty -= 0.15
            if variant == "eventlogstream-grouped-asset" and shape.entity_count >= 3:
                penalty += 0.35
            if variant == "eventlogstream-chronological" and shape.entity_count >= 3:
                penalty -= 0.15
            if variant == "eventlogstream-correlation" and shape.multi_numeric_potential and shape.cross_entity_comparable:
                penalty += 0.4
            if variant == "eventlogstream-tabular" and shape.metric_count >= 4:
                penalty += 0.3

            # ─── Category-Bar differentiation ───────────────────
            if variant == "category-bar-vertical" and shape.metric_count <= 5 and not shape.has_high_variance and shape.entity_count <= 2:
                penalty += 0.25  # Default for basic categorical, low variance, few entities
            if variant == "category-bar-vertical" and shape.entity_count >= 3:
                penalty -= 0.15  # Vertical is too basic for multi-entity comparison
            if variant == "category-bar-horizontal" and shape.metric_count >= 6 and not shape.has_high_variance:
                penalty += 0.4
            if variant == "category-bar-horizontal" and shape.has_high_variance:
                penalty -= 0.2
            if variant == "category-bar-stacked" and shape.metric_count >= 4 and shape.entity_count >= 3:
                penalty += 0.45  # Strong: stacked for sub-component breakdown across entities
            if variant == "category-bar-stacked" and shape.entity_count < 3:
                penalty -= 0.15
            if variant == "category-bar-grouped" and shape.cross_entity_comparable and shape.entity_count >= 3:
                penalty += 0.4  # Grouped for cross-entity comparison
            if variant == "category-bar-grouped" and shape.entity_count < 3:
                penalty -= 0.15
            if variant == "category-bar-diverging" and shape.has_high_variance and shape.entity_count < 3:
                penalty += 0.35
            if variant == "category-bar-diverging" and shape.has_high_variance and shape.entity_count >= 3:
                penalty += 0.2
            if variant == "category-bar-diverging" and not shape.has_high_variance:
                penalty -= 0.2

            # ─── Flow-Sankey differentiation ────────────────────
            if variant == "flow-sankey-standard" and shape.entity_count <= 3:
                penalty += 0.25
            if variant == "flow-sankey-multi-source" and shape.entity_count >= 3 and not shape.has_hierarchy:
                penalty += 0.35
            if variant == "flow-sankey-multi-source" and shape.entity_count <= 3:
                penalty -= 0.2
            if variant == "flow-sankey-energy-balance" and shape.has_rate_metric:
                penalty += 0.4
            if variant == "flow-sankey-standard" and shape.has_rate_metric:
                penalty -= 0.2
            if variant == "flow-sankey-layered" and shape.has_hierarchy:
                penalty += 0.4
            if variant == "flow-sankey-multi-source" and shape.has_hierarchy:
                penalty -= 0.2
            if variant == "flow-sankey-time-sliced" and shape.temporal_density > 5:
                penalty += 0.3

            # ─── Matrix-Heatmap differentiation ─────────────────
            if variant == "matrix-heatmap-correlation" and shape.multi_numeric_potential and shape.cross_entity_comparable:
                penalty += 0.4
            if variant == "matrix-heatmap-density" and shape.temporal_density > 100:
                penalty += 0.35
            if variant == "matrix-heatmap-value" and shape.temporal_density > 100 and not shape.cross_entity_comparable:
                penalty -= 0.2
            if variant == "matrix-heatmap-status" and shape.entity_count >= 3:
                penalty += 0.3
            if variant == "matrix-heatmap-status" and shape.entity_count < 3:
                penalty -= 0.1  # Status needs fleet-level view
            if variant == "matrix-heatmap-value" and shape.entity_count >= 2 and shape.metric_count >= 2 and not shape.has_high_variance:
                penalty += 0.2  # Value for moderate multi-entity, multi-metric
            if variant == "matrix-heatmap-calendar" and shape.temporal_density > 5:
                penalty += 0.3

        # Clamp to [-0.5, 0.5] range, then shift to [0.0, 1.0]
        penalty_scores[variant] = max(0.0, min(1.0, 0.5 + penalty))

    return {"penalty_scores": penalty_scores}


def node_rank(state: SelectionState) -> dict:
    """Node 6: Compute composite scores and determine confidence."""
    from backend.resolvers.variant_metadata import is_variant_default

    survivors = state.get("survivors", [])
    shape_scores = state.get("shape_scores", {})
    intent_scores = state.get("intent_scores", {})
    qtype_scores = state.get("qtype_scores", {})
    penalty_scores = state.get("penalty_scores", {})

    composite: dict[str, float] = {}
    for variant in survivors:
        s_shape = shape_scores.get(variant, 0.5)
        s_intent = intent_scores.get(variant, 0.0)
        s_qtype = qtype_scores.get(variant, 0.0)
        s_penalty = penalty_scores.get(variant, 0.5)
        s_default = 1.0 if is_variant_default(variant) else 0.0

        score = (
            W_SHAPE * s_shape
            + W_INTENT * s_intent
            + W_QUERY_TYPE * s_qtype
            + W_PENALTIES * s_penalty
            + W_DEFAULT * s_default
        )
        composite[variant] = round(score, 4)

    if not composite:
        return {
            "composite_scores": {},
            "dspy_needed": False,
            "selected_variant": state.get("scenario", ""),
            "confidence": 0.0,
        }

    # Sort by composite score
    sorted_variants = sorted(composite, key=lambda v: composite[v], reverse=True)
    top_score = composite[sorted_variants[0]]
    second_score = composite[sorted_variants[1]] if len(sorted_variants) > 1 else 0.0
    gap = top_score - second_score

    # Confidence based on gap and absolute score
    confidence = min(1.0, top_score * 1.5 + gap)

    # DSPy needed if ambiguous
    dspy_needed = gap < 0.10 or top_score < 0.45

    return {
        "composite_scores": composite,
        "dspy_needed": dspy_needed,
        "selected_variant": sorted_variants[0],
        "confidence": round(confidence, 3),
    }


def node_semantic_tiebreak(state: SelectionState) -> dict:
    """Node 6.5: Semantic tie-breaker for low-confidence cases.

    Uses the SemanticEmbedder to compute semantic similarity between the query
    and variant descriptions, then blends that score into the composite ranking.
    This runs only when the rank node marks the result as ambiguous.
    """
    from backend.resolvers.semantic_embedder import score_variants_semantic

    scenario = state.get("scenario", "")
    survivors = state.get("survivors", [])
    composite = state.get("composite_scores", {})
    query_text = state.get("query_text", "")

    if not scenario or not survivors or not composite or not query_text:
        return {}

    embedding_client = state.get("embedding_client")
    query_embedding = state.get("query_embedding")

    # Latency-sensitive: never cold-start heavy models here. If we have the
    # pipeline EmbeddingClient, reuse it; otherwise use TF-IDF fallback.
    strat = "embedding_client" if embedding_client is not None else "tfidf"
    semantic = score_variants_semantic(
        query=query_text,
        scenario=scenario,
        candidates=survivors,
        embedding_client=embedding_client,
        query_embedding=query_embedding,
        strategy=strat,
    )
    if not semantic:
        return {}

    blend = 0.25  # semantic weight
    blended: dict[str, float] = {}
    for v in survivors:
        c = float(composite.get(v, 0.0))
        s = float(semantic.get(v, 0.0))
        blended[v] = round((1.0 - blend) * c + blend * s, 4)

    sorted_variants = sorted(blended, key=lambda v: blended[v], reverse=True)
    top_score = blended[sorted_variants[0]]
    second_score = blended[sorted_variants[1]] if len(sorted_variants) > 1 else 0.0
    gap = top_score - second_score

    confidence = min(1.0, top_score * 1.5 + gap)
    dspy_needed = gap < 0.10 or top_score < 0.45

    prior_method = state.get("method") or "graph"
    method = prior_method if "semantic" in prior_method else "graph+semantic"

    return {
        "semantic_scores": semantic,
        "composite_scores": blended,
        "selected_variant": sorted_variants[0],
        "confidence": round(confidence, 3),
        "dspy_needed": dspy_needed,
        "method": method,
    }


def node_dspy_reason(state: SelectionState) -> dict:
    """Node 7: DSPy ChainOfThought reasoning for ambiguous cases."""
    from backend.resolvers.dspy_reasoner import (
        reason_variant_selection, is_dspy_available,
    )
    from backend.resolvers.data_shape import shape_to_text
    from backend.resolvers.variant_metadata import VARIANT_DESCRIPTIONS

    survivors = state.get("survivors", [])
    composite = state.get("composite_scores", {})
    shape = state.get("_data_shape")

    if not is_dspy_available() or not survivors:
        # Preserve upstream method (e.g., semantic tie-breaker) when DSPy is unavailable.
        return {"method": state.get("method") or "graph"}

    data_shape_text = shape_to_text(shape) if shape else ""

    selected, reasoning = reason_variant_selection(
        query=state.get("query_text", ""),
        candidates=survivors,
        composite_scores=composite,
        data_shape_text=data_shape_text,
        query_type=state.get("query_type", "overview"),
        question_intent=state.get("question_intent", ""),
        candidate_descriptions={v: VARIANT_DESCRIPTIONS.get(v, "") for v in survivors},
    )

    if selected and selected in survivors:
        return {
            "selected_variant": selected,
            "dspy_selection": selected,
            "dspy_reasoning": reasoning,
            "method": "graph+dspy",
            "confidence": min(1.0, state.get("confidence", 0.5) + 0.15),
        }

    # DSPy ran but did not produce a usable selection; keep upstream method.
    return {"method": state.get("method") or "graph"}


def node_autogen_validate(state: SelectionState) -> dict:
    """Node 7.5: AutoGen validation fallback.

    Runs a deterministic multi-agent-style validator over the current composite
    scores. This provides a robust fallback when DSPy is unavailable or fails.
    """
    from backend.resolvers.autogen_validator import validate_selection

    composite = state.get("composite_scores", {})
    survivors = set(state.get("survivors", []) or [])
    if not composite or not survivors:
        return {}

    result = validate_selection(
        composite_scores=composite,
        entity_count=int(state.get("entity_count", 1) or 1),
        metric_count=int(state.get("metric_count", 1) or 1),
        instance_count=int(state.get("instance_count", 1) or 1),
        has_timeseries=bool(state.get("has_timeseries", True)),
        query=str(state.get("query_text", "") or ""),
        prefer_autogen=False,
    )

    selected = (result.get("validated_variant") or "").strip()
    if not selected or selected not in survivors:
        return {"method": state.get("method") or "graph"}

    prior_method = state.get("method") or "graph"
    if "semantic" in prior_method:
        method = "graph+semantic+autogen"
    else:
        method = "graph+autogen"

    conf = result.get("confidence", state.get("confidence", 0.5))
    try:
        conf_f = float(conf)
    except Exception:
        conf_f = float(state.get("confidence", 0.5) or 0.5)

    return {
        "selected_variant": selected,
        "confidence": max(0.0, min(1.0, conf_f)),
        "autogen_reason": str(result.get("reason", "") or ""),
        "method": method,
    }


def node_finalize(state: SelectionState) -> dict:
    """Node 8: Finalize output."""
    method = state.get("method", "graph")
    if not method:
        method = "graph"

    selected = state.get("selected_variant", state.get("scenario", ""))
    confidence = state.get("confidence", 0.5)

    logger.debug(
        f"[SelectionGraph] Finalized: {state.get('scenario')} → {selected} "
        f"(confidence={confidence:.3f}, method={method})"
    )

    return {
        "selected_variant": selected,
        "confidence": confidence,
        "method": method,
    }


# ── Routing functions ────────────────────────────────────────────────────────

def route_after_filter(state: SelectionState) -> str:
    """Route after hard filter: 0-1 survivors → finalize, 2+ → score."""
    survivors = state.get("survivors", [])
    if len(survivors) <= 1:
        return "sole_survivor"
    return "multiple"


def route_confidence(state: SelectionState) -> str:
    """Route after ranking: high confidence → finalize, low → semantic tie-breaker."""
    if state.get("dspy_needed", False):
        return "low"
    return "high"


def route_after_semantic(state: SelectionState) -> str:
    """Route after semantic tie-breaker: resolved → finalize, still ambiguous → DSPy."""
    if state.get("dspy_needed", False):
        return "still_ambiguous"
    return "resolved"


def route_after_dspy(state: SelectionState) -> str:
    """Route after DSPy: if DSPy succeeded → finalize, otherwise → AutoGen validation."""
    if state.get("method") == "graph+dspy":
        return "ok"
    return "fallback"


# ── Graph Construction ──────────────────────────────────────────────────────

_compiled_graph = None


def _build_graph():
    """Build and compile the LangGraph selection graph."""
    global _compiled_graph
    if _compiled_graph is not None:
        return _compiled_graph

    if not _langgraph_available:
        return None

    builder = StateGraph(SelectionState)

    # Nodes
    builder.add_node("profile_data", node_profile_data)
    builder.add_node("hard_filter", node_hard_filter)
    builder.add_node("score_shape", node_score_shape)
    builder.add_node("score_intent", node_score_intent)
    builder.add_node("apply_penalties", node_apply_penalties)
    builder.add_node("rank", node_rank)
    builder.add_node("semantic_tiebreak", node_semantic_tiebreak)
    builder.add_node("dspy_reason", node_dspy_reason)
    builder.add_node("autogen_validate", node_autogen_validate)
    builder.add_node("finalize", node_finalize)

    # Edges
    builder.add_edge(START, "profile_data")
    builder.add_edge("profile_data", "hard_filter")
    builder.add_conditional_edges("hard_filter", route_after_filter, {
        "sole_survivor": "finalize",
        "multiple": "score_shape",
    })
    builder.add_edge("score_shape", "score_intent")
    builder.add_edge("score_intent", "apply_penalties")
    builder.add_edge("apply_penalties", "rank")
    builder.add_conditional_edges("rank", route_confidence, {
        "high": "finalize",
        "low": "semantic_tiebreak",
    })
    builder.add_conditional_edges("semantic_tiebreak", route_after_semantic, {
        "resolved": "finalize",
        "still_ambiguous": "dspy_reason",
    })
    builder.add_conditional_edges("dspy_reason", route_after_dspy, {
        "ok": "finalize",
        "fallback": "autogen_validate",
    })
    builder.add_edge("autogen_validate", "finalize")
    builder.add_edge("finalize", END)

    _compiled_graph = builder.compile()
    logger.info("[SelectionGraph] LangGraph constraint graph compiled")
    return _compiled_graph


# ── Sequential fallback ──────────────────────────────────────────────────────

def _run_sequential(state: SelectionState) -> dict:
    """Run the same pipeline as sequential function calls (no LangGraph)."""
    result = dict(state)

    # 1. Profile data
    result.update(node_profile_data(result))  # type: ignore

    # 2. Hard filter
    result.update(node_hard_filter(result))  # type: ignore

    # Route: sole survivor?
    survivors = result.get("survivors", [])
    if len(survivors) <= 1:
        if survivors:
            result["selected_variant"] = survivors[0]
            result["confidence"] = 1.0
            result["method"] = "filter_only"
        result.update(node_finalize(result))  # type: ignore
        return result

    # 3-6. Score and rank
    result.update(node_score_shape(result))  # type: ignore
    result.update(node_score_intent(result))  # type: ignore
    result.update(node_apply_penalties(result))  # type: ignore
    result.update(node_rank(result))  # type: ignore

    # Route: ambiguous?
    if result.get("dspy_needed", False):
        # 6.5 Semantic tie-breaker
        result.update(node_semantic_tiebreak(result))  # type: ignore

        # Still ambiguous: DSPy (then AutoGen fallback)
        if result.get("dspy_needed", False):
            result.update(node_dspy_reason(result))  # type: ignore
            if result.get("method") != "graph+dspy":
                result.update(node_autogen_validate(result))  # type: ignore

    # Finalize
    result.update(node_finalize(result))  # type: ignore
    return result


# ── Public API ──────────────────────────────────────────────────────────────

def run_selection_graph(
    scenario: str,
    query_text: str,
    question_intent: str = "",
    query_type: str = "overview",
    entity_count: int = 1,
    metric_count: int = 1,
    instance_count: int = 1,
    has_timeseries: bool = True,
    catalog: Any = None,
    data_profile: Any = None,
    intent: Any = None,
    query_embedding: list[float] | None = None,
    embedding_client: Any = None,
) -> tuple[str, float, str]:
    """Run the 3-layer selection graph.

    Returns:
        (variant_name, confidence_score, method) tuple.
        method is one of: "filter_only", "graph", "graph+dspy"
    """
    from backend.resolvers.variant_scorer import VARIANT_PROFILES

    profiles = VARIANT_PROFILES.get(scenario, {})
    if not profiles:
        return scenario, 1.0, "single_variant"

    initial_state: SelectionState = {
        "scenario": scenario,
        "query_text": query_text,
        "question_intent": question_intent,
        "query_type": query_type,
        "entity_count": entity_count,
        "metric_count": metric_count,
        "instance_count": instance_count,
        "has_timeseries": has_timeseries,
        "catalog": catalog,
        "data_profile": data_profile,
        "intent": intent,
        "query_embedding": query_embedding,
        "embedding_client": embedding_client,
        "all_variants": list(profiles.keys()),
        "survivors": list(profiles.keys()),
        "elimination_log": {},
        "shape_scores": {},
        "intent_scores": {},
        "qtype_scores": {},
        "penalty_scores": {},
        "composite_scores": {},
        "semantic_scores": {},
        "dspy_needed": False,
        "dspy_selection": "",
        "dspy_reasoning": "",
        "autogen_reason": "",
        "selected_variant": scenario,
        "confidence": 0.5,
        "method": "",
    }

    # Try LangGraph first
    graph = _build_graph()
    if graph is not None:
        try:
            result = graph.invoke(initial_state)
            variant = result.get("selected_variant", scenario)
            confidence = result.get("confidence", 0.5)
            method = result.get("method", "graph")
            logger.debug(
                f"[SelectionGraph] LangGraph: {scenario} → {variant} "
                f"(confidence={confidence:.2f}, method={method})"
            )
            return variant, confidence, method
        except Exception as e:
            logger.warning(f"[SelectionGraph] LangGraph failed, using sequential: {e}")

    # Fallback: sequential pipeline
    result = _run_sequential(initial_state)
    variant = result.get("selected_variant", scenario)
    confidence = result.get("confidence", 0.5)
    method = result.get("method", "graph")
    logger.debug(
        f"[SelectionGraph] Sequential: {scenario} → {variant} "
        f"(confidence={confidence:.2f}, method={method})"
    )
    return variant, confidence, method


def is_langgraph_available() -> bool:
    """Check if LangGraph is installed and usable."""
    return _langgraph_available
