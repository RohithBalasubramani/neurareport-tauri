"""
LlamaIndex-based variant metadata store with MetadataFilters.

Layer 1 of the 3-layer variant selection pipeline:
- Stores all 58 multi-variant profiles as LlamaIndex TextNode objects
- Uses MetadataFilters for hard constraint elimination
- Provides shape fitness scoring for Layer 2

Hard filters eliminate impossible variants (e.g., phase chart with no phase data).
Shape fitness scores rank surviving variants by data-property match.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ── Try LlamaIndex imports ────────────────────────────────────────────────────

_llamaindex_available = False
try:
    from llama_index.core.schema import TextNode
    from llama_index.core.vector_stores import (
        MetadataFilter,
        MetadataFilters,
        FilterOperator,
    )
    _llamaindex_available = True
    logger.debug("[VariantMetadata] LlamaIndex available")
except ImportError:
    logger.debug("[VariantMetadata] LlamaIndex not available, using dict fallback")


# ── Variant descriptions (data-property focused) ─────────────────────────────

VARIANT_DESCRIPTIONS: dict[str, str] = {
    # KPI
    "kpi-live": "Real-time current value display for continuous metrics — single entity, 1-2 metrics, any variance",
    "kpi-alert": "Alert-severity KPI with threshold status — needs alert context, anomaly-focused",
    "kpi-accumulated": "Running total / cumulative metric display — needs cumulative data (kWh, count, production total)",
    "kpi-lifecycle": "Asset lifecycle health indicator — remaining useful life, wear, age, depreciation metrics",
    "kpi-status": "Operational state indicator — binary/discrete states (online/offline/standby), multi-entity capable",
    # Trend
    "trend-line": "Standard continuous time series — single metric, 1-2 entities, moderate-to-high variance",
    "trend-area": "Filled area time series — emphasizes magnitude/volume, good for consumption and load metrics",
    "trend-step-line": "Discrete state change chart — binary/on-off data, zero-or-one variance, state transitions",
    "trend-rgb-phase": "Three-phase electrical overlay — requires exactly 3 phase columns (R/Y/B or L1/L2/L3)",
    "trend-alert-context": "Trend with threshold bands — needs threshold/limit context, alert-relevant metrics",
    "trend-heatmap": "Temporal pattern heatmap — discovers time-of-day and day-of-week patterns, needs dense timeseries",
    # Comparison
    "comparison-side-by-side": "Paired comparison — exactly 2 entities, same metric, direct A-vs-B",
    "comparison-delta-bar": "Deviation/delta bars — shows gap from target/baseline, multiple entities",
    "comparison-grouped-bar": "Multi-parameter grouped bars — multiple metrics across multiple entities",
    "comparison-waterfall": "Stepwise contribution breakdown — shows gains and losses, 3+ metrics",
    "comparison-small-multiples": "Grid of mini charts — 4+ entities, same metric, fleet/overview comparison",
    "comparison-composition-split": "Split composition comparison — 2-3 entities, shows makeup difference",
    # Distribution
    "distribution-donut": "Proportional share donut — 2-7 categories, part-of-whole snapshot",
    "distribution-pie": "Simple pie chart — 2-5 categories, basic proportion display",
    "distribution-horizontal-bar": "Ranked horizontal bars — sorted by value, 4+ items, ranking focus",
    "distribution-pareto-bar": "Pareto (80/20) chart — high variance data, 4+ items, top-contributor analysis",
    "distribution-grouped-bar": "Grouped distribution bars — multi-entity cross-group comparison, needs 2+ entities",
    "distribution-100-stacked-bar": "Normalized 100% stacked bars — proportional comparison across categories",
    # Composition
    "composition-stacked-bar": "Stacked bar breakdown — part-to-whole by category, 2-8 metrics",
    "composition-stacked-area": "Stacked area over time — composition evolution, needs timeseries, 2-6 metrics",
    "composition-donut": "Composition snapshot donut — current mix/makeup, 2-6 categories",
    "composition-waterfall": "Composition waterfall — incremental gains and losses, bridge chart",
    "composition-treemap": "Hierarchical treemap — nested proportional areas, works with hierarchy data",
    # Alerts
    "alerts-card": "Standard alert cards — general alert display, any alert data",
    "alerts-banner": "Full-width alert banner — site-wide critical notifications",
    "alerts-toast": "Floating toast notifications — recent/latest alerts, compact",
    "alerts-badge": "Alert count badge — compact indicator showing number of active alerts",
    "alerts-modal": "Alert investigation modal — detailed alert drill-down, forensic context",
    # Timeline
    "timeline-linear": "Linear event timeline — chronological event sequence, general purpose",
    "timeline-status": "Status/uptime timeline — continuous state history, operational availability",
    "timeline-multilane": "Multi-lane parallel timeline — 2+ entity schedules, concurrent event streams",
    "timeline-forensic": "Forensic investigation timeline — root cause analysis, annotated event chain",
    "timeline-dense": "Dense event cluster view — high-frequency bursts, many events in short time",
    # EventLogStream
    "eventlogstream-chronological": "Chronological event log — general event feed, time-ordered",
    "eventlogstream-compact-feed": "Compact card feed — social-media-style event summaries",
    "eventlogstream-tabular": "Tabular event log — sortable/filterable table format, many columns",
    "eventlogstream-correlation": "Correlated event view — linked/cascading events, cause-effect chains",
    "eventlogstream-grouped-asset": "Asset-grouped events — events organized by equipment, 2+ entities",
    # Category-Bar
    "category-bar-vertical": "Vertical category bars — standard categorical comparison, 2-8 categories",
    "category-bar-horizontal": "Horizontal category bars — long labels, ranking, many items",
    "category-bar-stacked": "Stacked category bars — sub-component breakdown per category",
    "category-bar-grouped": "Grouped category bars — multiple metrics side-by-side per category",
    "category-bar-diverging": "Diverging category bars — positive/negative deviations from baseline",
    # Flow-Sankey
    "flow-sankey-standard": "Standard Sankey flow — source-to-destination flow visualization",
    "flow-sankey-energy-balance": "Energy balance Sankey — input/output/loss flows, efficiency analysis",
    "flow-sankey-multi-source": "Multi-source Sankey — converging flows from 3+ sources",
    "flow-sankey-layered": "Layered/hierarchical Sankey — multi-stage process flows",
    "flow-sankey-time-sliced": "Temporal Sankey — flow changes over time, needs timeseries",
    # Matrix-Heatmap
    "matrix-heatmap-value": "Value heatmap — cross-tabulation of entities and metrics",
    "matrix-heatmap-correlation": "Correlation matrix — metric-to-metric relationships, 3+ metrics",
    "matrix-heatmap-calendar": "Calendar heatmap — daily/weekly/monthly patterns over time",
    "matrix-heatmap-status": "Status grid heatmap — fleet health overview, 3+ entities",
    "matrix-heatmap-density": "Density/hotspot heatmap — spatial concentration patterns",
}


# ── Per-variant shape preferences (soft scoring signals) ─────────────────────

@dataclass(frozen=True)
class ShapePreference:
    """Soft scoring preferences for how well a variant matches data shape."""
    prefers_phase_data: float = 0.0
    prefers_binary_data: float = 0.0
    prefers_cumulative: float = 0.0
    prefers_high_variance: float = 0.0
    prefers_low_variance: float = 0.0
    prefers_many_entities: float = 0.0
    prefers_few_entities: float = 0.0
    prefers_many_metrics: float = 0.0
    prefers_few_metrics: float = 0.0
    prefers_hierarchy: float = 0.0
    prefers_correlation: float = 0.0
    prefers_ranking: float = 0.0
    prefers_temperature: float = 0.0
    prefers_flow: float = 0.0
    prefers_rate: float = 0.0
    prefers_percentage: float = 0.0
    prefers_alerts: float = 0.0
    prefers_dense_timeseries: float = 0.0
    prefers_cross_entity: float = 0.0


VARIANT_SHAPE_PREFS: dict[str, ShapePreference] = {
    # KPI — differentiate by metric type
    "kpi-live": ShapePreference(prefers_few_entities=0.5, prefers_temperature=0.3, prefers_rate=0.3),
    "kpi-alert": ShapePreference(prefers_alerts=0.95, prefers_few_entities=0.3),
    "kpi-accumulated": ShapePreference(prefers_cumulative=0.99, prefers_few_entities=0.4),
    "kpi-lifecycle": ShapePreference(prefers_percentage=0.8, prefers_few_entities=0.5),
    "kpi-status": ShapePreference(prefers_binary_data=0.9, prefers_few_entities=0.3),
    # Trend — differentiate by data type and density
    "trend-line": ShapePreference(prefers_few_entities=0.3, prefers_few_metrics=0.2),
    "trend-area": ShapePreference(prefers_flow=0.7, prefers_rate=0.6, prefers_few_entities=0.3),
    "trend-step-line": ShapePreference(prefers_binary_data=0.99, prefers_low_variance=0.8, prefers_few_entities=0.3),
    "trend-rgb-phase": ShapePreference(prefers_phase_data=0.99, prefers_few_entities=0.3),
    "trend-alert-context": ShapePreference(prefers_alerts=0.9, prefers_few_entities=0.3),
    "trend-heatmap": ShapePreference(prefers_dense_timeseries=0.95, prefers_few_entities=0.3),
    # Comparison — differentiate by entity/metric count
    "comparison-side-by-side": ShapePreference(prefers_few_entities=0.6, prefers_cross_entity=0.5, prefers_few_metrics=0.5),
    "comparison-delta-bar": ShapePreference(prefers_many_entities=0.5, prefers_cross_entity=0.6),
    "comparison-grouped-bar": ShapePreference(prefers_many_metrics=0.85, prefers_cross_entity=0.6, prefers_many_entities=0.4),
    "comparison-waterfall": ShapePreference(prefers_high_variance=0.7, prefers_many_metrics=0.6),
    "comparison-small-multiples": ShapePreference(prefers_many_entities=0.95, prefers_cross_entity=0.7),
    "comparison-composition-split": ShapePreference(prefers_few_entities=0.5, prefers_many_metrics=0.6, prefers_percentage=0.4),
    # Distribution — differentiate by count and variance
    "distribution-donut": ShapePreference(prefers_few_metrics=0.6, prefers_percentage=0.4),
    "distribution-pie": ShapePreference(prefers_few_metrics=0.8, prefers_few_entities=0.5, prefers_percentage=0.3),
    "distribution-horizontal-bar": ShapePreference(prefers_ranking=0.8, prefers_many_metrics=0.5),
    "distribution-pareto-bar": ShapePreference(prefers_ranking=0.7, prefers_high_variance=0.9, prefers_many_metrics=0.6),
    "distribution-grouped-bar": ShapePreference(prefers_many_entities=0.5, prefers_cross_entity=0.7, prefers_many_metrics=0.4),
    "distribution-100-stacked-bar": ShapePreference(prefers_percentage=0.8, prefers_many_metrics=0.5, prefers_cross_entity=0.4),
    # Composition — differentiate by richness and hierarchy
    "composition-stacked-bar": ShapePreference(prefers_many_metrics=0.5, prefers_many_entities=0.4),
    "composition-stacked-area": ShapePreference(prefers_dense_timeseries=0.7, prefers_many_metrics=0.4),
    "composition-donut": ShapePreference(prefers_few_metrics=0.7, prefers_few_entities=0.5, prefers_percentage=0.5),
    "composition-waterfall": ShapePreference(prefers_high_variance=0.7, prefers_many_metrics=0.5),
    "composition-treemap": ShapePreference(prefers_hierarchy=0.9, prefers_many_metrics=0.5, prefers_many_entities=0.4),
    # Alerts — differentiate by scope
    "alerts-card": ShapePreference(prefers_alerts=0.5, prefers_many_entities=0.3),
    "alerts-banner": ShapePreference(prefers_alerts=0.7, prefers_few_entities=0.5),
    "alerts-toast": ShapePreference(prefers_alerts=0.6, prefers_few_entities=0.6),
    "alerts-badge": ShapePreference(prefers_alerts=0.5, prefers_many_entities=0.5),
    "alerts-modal": ShapePreference(prefers_alerts=0.8),
    # Timeline — differentiate by data type and density
    "timeline-linear": ShapePreference(prefers_few_entities=0.3),
    "timeline-status": ShapePreference(prefers_binary_data=0.8, prefers_few_entities=0.4),
    "timeline-multilane": ShapePreference(prefers_many_entities=0.8, prefers_cross_entity=0.5),
    "timeline-forensic": ShapePreference(prefers_alerts=0.7, prefers_dense_timeseries=0.3),
    "timeline-dense": ShapePreference(prefers_dense_timeseries=0.95),
    # EventLogStream — differentiate by entity count and correlation
    "eventlogstream-chronological": ShapePreference(prefers_few_entities=0.3),
    "eventlogstream-compact-feed": ShapePreference(prefers_few_entities=0.6, prefers_few_metrics=0.4),
    "eventlogstream-tabular": ShapePreference(prefers_many_metrics=0.6, prefers_many_entities=0.3),
    "eventlogstream-correlation": ShapePreference(prefers_correlation=0.95, prefers_many_metrics=0.5),
    "eventlogstream-grouped-asset": ShapePreference(prefers_many_entities=0.8, prefers_cross_entity=0.5),
    # Category-Bar — differentiate by structure
    "category-bar-vertical": ShapePreference(prefers_few_metrics=0.5, prefers_few_entities=0.3),
    "category-bar-horizontal": ShapePreference(prefers_ranking=0.8, prefers_many_metrics=0.4),
    "category-bar-stacked": ShapePreference(prefers_many_metrics=0.7, prefers_many_entities=0.4),
    "category-bar-grouped": ShapePreference(prefers_cross_entity=0.7, prefers_many_entities=0.5, prefers_many_metrics=0.5),
    "category-bar-diverging": ShapePreference(prefers_high_variance=0.8),
    # Flow-Sankey — differentiate by structure and type
    "flow-sankey-standard": ShapePreference(prefers_flow=0.5, prefers_few_entities=0.3),
    "flow-sankey-energy-balance": ShapePreference(prefers_rate=0.7, prefers_flow=0.6),
    "flow-sankey-multi-source": ShapePreference(prefers_many_entities=0.8, prefers_flow=0.4),
    "flow-sankey-layered": ShapePreference(prefers_hierarchy=0.9, prefers_flow=0.3),
    "flow-sankey-time-sliced": ShapePreference(prefers_dense_timeseries=0.7, prefers_flow=0.3),
    # Matrix-Heatmap — differentiate by correlation and density
    "matrix-heatmap-value": ShapePreference(prefers_many_entities=0.5, prefers_many_metrics=0.4),
    "matrix-heatmap-correlation": ShapePreference(prefers_correlation=0.95, prefers_many_metrics=0.8),
    "matrix-heatmap-calendar": ShapePreference(prefers_dense_timeseries=0.85),
    "matrix-heatmap-status": ShapePreference(prefers_many_entities=0.8, prefers_binary_data=0.4),
    "matrix-heatmap-density": ShapePreference(prefers_dense_timeseries=0.7, prefers_few_entities=0.3),
}


# ── TextNode construction ─────────────────────────────────────────────────────

_variant_nodes_cache: dict[str, list] = {}


def _build_variant_nodes() -> dict[str, list]:
    """Auto-build TextNode objects from VARIANT_PROFILES + metadata.

    Returns scenario -> [TextNode, ...] mapping.
    """
    global _variant_nodes_cache
    if _variant_nodes_cache:
        return _variant_nodes_cache

    from backend.resolvers.variant_scorer import VARIANT_PROFILES

    nodes: dict[str, list] = {}

    for scenario, profiles in VARIANT_PROFILES.items():
        scenario_nodes = []
        for variant, profile in profiles.items():
            desc = VARIANT_DESCRIPTIONS.get(variant, f"{variant} visualization")

            metadata = {
                "variant": variant,
                "scenario": scenario,
                "requires_timeseries": profile.needs_timeseries,
                "requires_multiple_entities": profile.needs_multiple_entities,
                "min_entity_count": profile.ideal_entity_count[0] if profile.ideal_entity_count else 1,
                "min_metric_count": profile.ideal_metric_count[0] if profile.ideal_metric_count else 1,
                "max_entity_count": profile.ideal_entity_count[1] if profile.ideal_entity_count else 100,
                "max_metric_count": profile.ideal_metric_count[1] if profile.ideal_metric_count else 100,
                "is_default": profile.is_default,
            }

            # Flatten intent affinity into metadata
            for intent_key, score in profile.intent_affinity.items():
                metadata[f"intent_{intent_key}"] = score

            # Flatten query type affinity into metadata
            for qtype_key, score in profile.query_type_affinity.items():
                metadata[f"qtype_{qtype_key}"] = score

            if _llamaindex_available:
                node = TextNode(text=desc, metadata=metadata)
                node.id_ = variant
                scenario_nodes.append(node)
            else:
                scenario_nodes.append({"text": desc, "metadata": metadata, "id": variant})

        nodes[scenario] = scenario_nodes

    _variant_nodes_cache = nodes
    return nodes


# ── Hard filter using LlamaIndex MetadataFilters ─────────────────────────────

def _apply_filters_manual(nodes: list, filters: list[dict]) -> list:
    """Apply metadata filters to a list of nodes (dict or TextNode)."""
    survivors = []
    for node in nodes:
        meta = node.metadata if hasattr(node, "metadata") else node.get("metadata", {})
        passes = True
        for f in filters:
            key, op, val = f["key"], f["op"], f["value"]
            node_val = meta.get(key)
            if node_val is None:
                continue
            if op == "==" and node_val != val:
                passes = False
                break
            if op == "<=" and node_val > val:
                passes = False
                break
            if op == ">=" and node_val < val:
                passes = False
                break
        if passes:
            survivors.append(node)
    return survivors


def filter_variants(scenario: str, shape) -> list[str]:
    """Layer 1: Eliminate impossible variants using metadata hard filters.

    Args:
        scenario: Widget scenario name.
        shape: DataShapeProfile with measured data properties.

    Returns:
        List of surviving variant names after hard elimination.
    """
    nodes = _build_variant_nodes()
    scenario_nodes = nodes.get(scenario, [])
    if not scenario_nodes:
        return []

    # Build filter conditions
    filters: list[dict] = []

    # If no timeseries, exclude variants that require it
    if not shape.has_timeseries:
        filters.append({"key": "requires_timeseries", "op": "==", "value": False})

    # If single entity, exclude variants that need multiple
    if shape.entity_count < 2:
        filters.append({"key": "requires_multiple_entities", "op": "==", "value": False})

    # Entity count must meet variant minimum
    filters.append({"key": "min_entity_count", "op": "<=", "value": shape.entity_count})

    # Metric count must meet variant minimum
    filters.append({"key": "min_metric_count", "op": "<=", "value": shape.metric_count})

    if _llamaindex_available:
        try:
            li_filters = []
            for f in filters:
                op_map = {"==": FilterOperator.EQ, "<=": FilterOperator.LTE, ">=": FilterOperator.GTE}
                li_filters.append(MetadataFilter(
                    key=f["key"],
                    operator=op_map[f["op"]],
                    value=f["value"],
                ))
            metadata_filters = MetadataFilters(filters=li_filters)
            survivors = _apply_llamaindex_filters(scenario_nodes, metadata_filters)
            result = [
                (n.metadata["variant"] if hasattr(n, "metadata") else n["metadata"]["variant"])
                for n in survivors
            ]
            if result:
                return result
        except Exception as e:
            logger.debug(f"[VariantMetadata] LlamaIndex filter failed, using manual: {e}")

    # Manual fallback
    survivors = _apply_filters_manual(scenario_nodes, filters)
    result = [
        (n.metadata["variant"] if hasattr(n, "metadata") else n["metadata"]["variant"])
        for n in survivors
    ]

    # Ensure at least one variant survives (scenario default)
    if not result:
        from backend.resolvers.variant_scorer import VARIANT_PROFILES
        profiles = VARIANT_PROFILES.get(scenario, {})
        for v, p in profiles.items():
            if p.is_default:
                return [v]
        return list(profiles.keys())[:1] if profiles else []

    return result


def _apply_llamaindex_filters(nodes: list, metadata_filters) -> list:
    """Apply LlamaIndex MetadataFilters to TextNode list."""
    survivors = []
    for node in nodes:
        passes = True
        for f in metadata_filters.filters:
            val = node.metadata.get(f.key)
            if val is None:
                continue
            if f.operator == FilterOperator.EQ and val != f.value:
                passes = False
                break
            if f.operator == FilterOperator.LTE and val > f.value:
                passes = False
                break
            if f.operator == FilterOperator.GTE and val < f.value:
                passes = False
                break
            if f.operator == FilterOperator.LT and val >= f.value:
                passes = False
                break
            if f.operator == FilterOperator.GT and val <= f.value:
                passes = False
                break
        if passes:
            survivors.append(node)
    return survivors


# ── Shape fitness scoring ─────────────────────────────────────────────────────

def score_shape_fitness(variant: str, shape) -> float:
    """Score how well a variant matches the data shape.

    Returns 0.0-1.0 based on how many data properties match the
    variant's ideal shape preferences.
    """
    prefs = VARIANT_SHAPE_PREFS.get(variant)
    if not prefs:
        return 0.5  # Neutral for unknown variants

    score = 0.0
    weight_sum = 0.0

    def _add(pref_val: float, match: bool, boost: float = 1.0):
        nonlocal score, weight_sum
        if pref_val > 0:
            weight_sum += pref_val
            if match:
                score += pref_val * boost

    _add(prefs.prefers_phase_data, shape.has_phase_data)
    _add(prefs.prefers_binary_data, shape.has_binary_metric)
    _add(prefs.prefers_cumulative, shape.has_cumulative_metric)
    _add(prefs.prefers_high_variance, shape.has_high_variance)
    _add(prefs.prefers_low_variance, shape.has_near_zero_variance)
    _add(prefs.prefers_many_entities, shape.entity_count >= 4)
    _add(prefs.prefers_few_entities, shape.entity_count <= 3)
    _add(prefs.prefers_many_metrics, shape.metric_count >= 4)
    _add(prefs.prefers_few_metrics, shape.metric_count <= 3)
    _add(prefs.prefers_hierarchy, shape.has_hierarchy)
    _add(prefs.prefers_correlation, shape.multi_numeric_potential and shape.cross_entity_comparable)
    _add(prefs.prefers_ranking, shape.has_high_variance and shape.metric_count >= 3)
    _add(prefs.prefers_temperature, shape.has_temperature)
    _add(prefs.prefers_flow, shape.has_flow_metric)
    _add(prefs.prefers_rate, shape.has_rate_metric)
    _add(prefs.prefers_percentage, shape.has_percentage_metric)
    _add(prefs.prefers_alerts, shape.has_alerts)
    _add(prefs.prefers_dense_timeseries, shape.temporal_density > 100)
    _add(prefs.prefers_cross_entity, shape.cross_entity_comparable)

    if weight_sum <= 0:
        return 0.5  # No preferences defined

    return min(1.0, score / weight_sum)


def get_variant_intent_score(variant: str, question_intent: str) -> float:
    """Get intent affinity score for a variant from metadata."""
    nodes = _build_variant_nodes()
    for scenario_nodes in nodes.values():
        for node in scenario_nodes:
            meta = node.metadata if hasattr(node, "metadata") else node.get("metadata", {})
            if meta.get("variant") == variant:
                return meta.get(f"intent_{question_intent}", 0.0)
    return 0.0


def get_variant_qtype_score(variant: str, query_type: str) -> float:
    """Get query type affinity score for a variant from metadata."""
    nodes = _build_variant_nodes()
    for scenario_nodes in nodes.values():
        for node in scenario_nodes:
            meta = node.metadata if hasattr(node, "metadata") else node.get("metadata", {})
            if meta.get("variant") == variant:
                return meta.get(f"qtype_{query_type}", 0.0)
    return 0.0


def is_variant_default(variant: str) -> bool:
    """Check if variant is the scenario default."""
    nodes = _build_variant_nodes()
    for scenario_nodes in nodes.values():
        for node in scenario_nodes:
            meta = node.metadata if hasattr(node, "metadata") else node.get("metadata", {})
            if meta.get("variant") == variant:
                return bool(meta.get("is_default", False))
    return False


def is_llamaindex_available() -> bool:
    """Check if LlamaIndex is installed."""
    return _llamaindex_available
