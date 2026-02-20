"""
Data-driven scenario scoring for dashboard composition.

Replaces keyword-based scenario selection with intelligent scoring based on
DataShapeProfile properties, entity domain detection, and query context.

All 24 scenarios are first-class citizens. Selection is driven by:
1. Domain detection from entity types + column names (not query keywords)
2. Data shape fitness from DataShapeProfile (variance, cardinality, metric types)
3. Query type + intent affinity (structural, not keyword-based)

No scenario is "niche" — any scenario can appear in any dashboard if the data
properties support it. The system detects, the user doesn't need to specify.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ── Domain detection ─────────────────────────────────────────────────────────
# Infer domain from entity types and column names — NOT from user query text.

_DOMAIN_ENTITY_TYPES: dict[str, set[str]] = {
    "people": {
        "person", "employee", "staff", "worker", "team", "personnel",
        "crew", "operator", "technician", "engineer", "manager",
        "hr", "workforce", "member",
    },
    "supply_chain": {
        "shipment", "route", "warehouse", "supplier", "logistics",
        "delivery", "port", "carrier", "freight", "inventory",
        "distribution", "fleet",
    },
    "iot_device": {
        "device", "gateway", "plc", "rtu", "actuator", "controller",
        "iot", "edge", "node", "module", "firmware",
    },
    "ai_agent": {
        "agent", "bot", "automation", "workflow", "orchestrator",
        "pipeline_agent", "autonomous",
    },
    "compliance": {
        "audit", "compliance", "certificate", "regulation", "policy",
        "vault", "archive", "attestation",
    },
    "diagnostic": {
        "fault", "diagnostic", "failure", "defect", "rootcause",
        "incident", "cooling",
    },
    "prediction": {
        "forecast", "prediction", "model", "projection", "estimate",
    },
    "chat": {
        "chat", "conversation", "message", "dialogue",
    },
}

_DOMAIN_COLUMN_HINTS: dict[str, set[str]] = {
    "people": {
        "name", "role", "department", "hire_date", "headcount",
        "salary", "shift", "badge", "certification",
    },
    "iot_device": {
        "signal_strength", "firmware", "battery", "uptime", "connectivity",
        "rssi", "latency", "packet_loss", "device_id",
    },
    "compliance": {
        "audit_score", "compliance_pct", "violation_count", "expiry_date",
        "certification_status",
    },
    "diagnostic": {
        "fault_code", "error_count", "mtbf", "mttr", "failure_mode",
        "severity",
    },
    "prediction": {
        "confidence_lower", "confidence_upper", "prediction",
        "forecast", "uncertainty", "prediction_interval",
    },
}


def detect_domains(entity_types: set[str], column_names: set[str]) -> set[str]:
    """Detect data domains from entity types and column names.

    Returns set of detected domain strings.
    """
    detected: set[str] = set()
    et_lower = {e.lower() for e in entity_types}
    cn_lower = {c.lower() for c in column_names}

    for domain, keywords in _DOMAIN_ENTITY_TYPES.items():
        if et_lower & keywords:
            detected.add(domain)

    for domain, hints in _DOMAIN_COLUMN_HINTS.items():
        if cn_lower & hints:
            detected.add(domain)

    return detected


def _extract_entity_types_and_columns(catalog, intent=None) -> tuple[set[str], set[str]]:
    """Extract entity types and column names from catalog + intent."""
    entity_types: set[str] = set()
    column_names: set[str] = set()

    if intent and hasattr(intent, "entities"):
        for ent in (intent.entities or []):
            if hasattr(ent, "name") and ent.name:
                entity_types.add(ent.name.lower())

    if catalog and hasattr(catalog, "enriched_tables"):
        for t in catalog.enriched_tables:
            if hasattr(t, "entity_type") and t.entity_type:
                entity_types.add(t.entity_type.lower())
            if hasattr(t, "columns"):
                for c in t.columns:
                    if hasattr(c, "name"):
                        column_names.add(c.name.lower())

    return entity_types, column_names


# ── Scenario data affinity ───────────────────────────────────────────────────
# Each scenario defines what data properties make it a good fit.

@dataclass(frozen=True)
class ScenarioAffinity:
    """Data-driven scoring profile for a scenario."""
    # Required domains — scenario only eligible if ANY of these domains detected
    # Empty means "general purpose" — always eligible
    required_domains: frozenset[str] = frozenset()

    # Query type affinities (0.0 = irrelevant, 1.0 = perfect fit)
    query_type_affinity: dict[str, float] = field(default_factory=dict)

    # Data shape scoring function name (maps to scoring logic below)
    # Higher score = better fit for this data
    prefers_timeseries: float = 0.0
    prefers_alerts: float = 0.0
    prefers_many_entities: float = 0.0
    prefers_few_entities: float = 0.0
    prefers_many_metrics: float = 0.0
    prefers_high_variance: float = 0.0
    prefers_hierarchy: float = 0.0
    prefers_flow: float = 0.0
    prefers_temperature: float = 0.0
    prefers_binary: float = 0.0
    prefers_cumulative: float = 0.0
    prefers_rate: float = 0.0
    prefers_percentage: float = 0.0
    prefers_correlation: float = 0.0
    prefers_dense_timeseries: float = 0.0
    prefers_phase: float = 0.0


# hashable workaround: use tuples for default_factory
def _qa(**kw) -> dict[str, float]:
    return kw


SCENARIO_AFFINITIES: dict[str, ScenarioAffinity] = {
    # ── Core visualization scenarios (always eligible with timeseries) ────
    "kpi": ScenarioAffinity(
        query_type_affinity=_qa(status=0.9, overview=0.8, alert=0.6, trend=0.5,
                                comparison=0.4, analysis=0.5, diagnostic=0.5, forecast=0.6),
        prefers_timeseries=0.3, prefers_few_entities=0.3,
    ),
    "trend": ScenarioAffinity(
        query_type_affinity=_qa(trend=0.9, analysis=0.7, status=0.6, comparison=0.5,
                                diagnostic=0.7, forecast=0.8, overview=0.5, alert=0.4),
        prefers_timeseries=0.9, prefers_temperature=0.2,
    ),
    "trend-multi-line": ScenarioAffinity(
        query_type_affinity=_qa(trend=0.9, comparison=0.7, analysis=0.7, diagnostic=0.5,
                                overview=0.4, status=0.3, forecast=0.6, alert=0.3),
        prefers_timeseries=0.8, prefers_many_entities=0.4, prefers_correlation=0.5,
    ),
    "trends-cumulative": ScenarioAffinity(
        query_type_affinity=_qa(trend=0.8, analysis=0.6, overview=0.5, forecast=0.7,
                                status=0.3, comparison=0.3, diagnostic=0.2, alert=0.2),
        prefers_timeseries=0.7, prefers_cumulative=0.9,
    ),
    "comparison": ScenarioAffinity(
        query_type_affinity=_qa(comparison=0.9, analysis=0.7, overview=0.5, status=0.4,
                                trend=0.4, diagnostic=0.4, forecast=0.3, alert=0.3),
        prefers_many_entities=0.5, prefers_timeseries=0.3, prefers_correlation=0.3,
    ),
    "distribution": ScenarioAffinity(
        query_type_affinity=_qa(analysis=0.8, comparison=0.6, overview=0.6, status=0.3,
                                trend=0.3, diagnostic=0.4, forecast=0.2, alert=0.2),
        prefers_many_metrics=0.4, prefers_high_variance=0.3,
    ),
    "composition": ScenarioAffinity(
        query_type_affinity=_qa(analysis=0.85, overview=0.75, comparison=0.6, trend=0.5,
                                status=0.4, diagnostic=0.3, forecast=0.3, alert=0.2),
        prefers_many_metrics=0.5, prefers_percentage=0.4, prefers_hierarchy=0.4,
        prefers_timeseries=0.3,
    ),
    "category-bar": ScenarioAffinity(
        query_type_affinity=_qa(analysis=0.85, comparison=0.75, overview=0.6, status=0.4,
                                trend=0.3, diagnostic=0.3, forecast=0.2, alert=0.2),
        prefers_many_metrics=0.5, prefers_high_variance=0.3, prefers_timeseries=0.3,
    ),
    "alerts": ScenarioAffinity(
        query_type_affinity=_qa(alert=0.9, status=0.7, diagnostic=0.6, overview=0.4,
                                trend=0.3, comparison=0.2, analysis=0.3, forecast=0.2),
        prefers_alerts=0.9,
    ),
    "timeline": ScenarioAffinity(
        query_type_affinity=_qa(status=0.7, diagnostic=0.7, alert=0.6, analysis=0.5,
                                trend=0.5, overview=0.4, comparison=0.3, forecast=0.3),
        prefers_timeseries=0.6, prefers_alerts=0.3, prefers_binary=0.2,
    ),
    "eventlogstream": ScenarioAffinity(
        query_type_affinity=_qa(status=0.7, alert=0.6, diagnostic=0.6, analysis=0.5,
                                overview=0.5, trend=0.3, comparison=0.2, forecast=0.2),
        prefers_timeseries=0.5,
    ),
    "flow-sankey": ScenarioAffinity(
        query_type_affinity=_qa(analysis=0.85, overview=0.6, comparison=0.5, trend=0.4,
                                diagnostic=0.4, status=0.3, forecast=0.3, alert=0.2),
        prefers_flow=0.8, prefers_rate=0.5, prefers_hierarchy=0.4,
        prefers_many_entities=0.4, prefers_timeseries=0.3,
    ),
    "matrix-heatmap": ScenarioAffinity(
        query_type_affinity=_qa(analysis=0.85, comparison=0.65, diagnostic=0.6, overview=0.55,
                                status=0.55, trend=0.45, forecast=0.3, alert=0.3),
        prefers_many_entities=0.5, prefers_many_metrics=0.5,
        prefers_correlation=0.5, prefers_dense_timeseries=0.4,
        prefers_timeseries=0.3,
    ),
    "narrative": ScenarioAffinity(
        query_type_affinity=_qa(overview=0.9, status=0.5, analysis=0.5, trend=0.3,
                                comparison=0.3, diagnostic=0.4, forecast=0.4, alert=0.3),
    ),

    # ── Domain-specific scenarios (eligible when domain detected in data) ──
    "peopleview": ScenarioAffinity(
        required_domains=frozenset({"people"}),
        query_type_affinity=_qa(overview=0.8, status=0.6, analysis=0.4, comparison=0.3,
                                trend=0.2, diagnostic=0.2, forecast=0.2, alert=0.2),
    ),
    "peoplehexgrid": ScenarioAffinity(
        required_domains=frozenset({"people"}),
        query_type_affinity=_qa(overview=0.7, status=0.5, analysis=0.5, comparison=0.4,
                                trend=0.2, diagnostic=0.2, forecast=0.2, alert=0.2),
        prefers_many_entities=0.4,
    ),
    "peoplenetwork": ScenarioAffinity(
        required_domains=frozenset({"people"}),
        query_type_affinity=_qa(overview=0.7, analysis=0.6, status=0.4, comparison=0.3,
                                trend=0.2, diagnostic=0.2, forecast=0.2, alert=0.2),
        prefers_hierarchy=0.5, prefers_correlation=0.4,
    ),
    "supplychainglobe": ScenarioAffinity(
        required_domains=frozenset({"supply_chain"}),
        query_type_affinity=_qa(overview=0.8, status=0.6, analysis=0.5, comparison=0.3,
                                trend=0.4, diagnostic=0.3, forecast=0.4, alert=0.3),
        prefers_many_entities=0.3,
    ),
    "edgedevicepanel": ScenarioAffinity(
        required_domains=frozenset({"iot_device"}),
        query_type_affinity=_qa(status=0.8, overview=0.6, diagnostic=0.6, alert=0.5,
                                analysis=0.4, trend=0.3, comparison=0.3, forecast=0.2),
    ),
    "chatstream": ScenarioAffinity(
        required_domains=frozenset({"chat"}),
        query_type_affinity=_qa(overview=0.3, status=0.2, analysis=0.2, trend=0.1,
                                comparison=0.1, diagnostic=0.2, forecast=0.1, alert=0.1),
    ),
    "diagnosticpanel": ScenarioAffinity(
        required_domains=frozenset({"diagnostic"}),
        query_type_affinity=_qa(diagnostic=0.9, alert=0.6, status=0.5, analysis=0.5,
                                overview=0.3, trend=0.3, comparison=0.2, forecast=0.2),
        prefers_alerts=0.5,
    ),
    "uncertaintypanel": ScenarioAffinity(
        required_domains=frozenset({"prediction"}),
        query_type_affinity=_qa(forecast=0.9, analysis=0.5, trend=0.5, diagnostic=0.3,
                                overview=0.3, status=0.2, comparison=0.2, alert=0.2),
    ),
    "agentsview": ScenarioAffinity(
        required_domains=frozenset({"ai_agent"}),
        query_type_affinity=_qa(status=0.7, overview=0.7, diagnostic=0.4, analysis=0.3,
                                trend=0.2, comparison=0.2, forecast=0.2, alert=0.3),
    ),
    "vaultview": ScenarioAffinity(
        required_domains=frozenset({"compliance"}),
        query_type_affinity=_qa(overview=0.7, status=0.6, analysis=0.4, diagnostic=0.3,
                                trend=0.2, comparison=0.2, forecast=0.2, alert=0.3),
    ),
}


# ── Scoring ──────────────────────────────────────────────────────────────────

def score_scenario_fitness(
    scenario: str,
    shape,
    query_type: str = "overview",
    domains: set[str] | None = None,
) -> float:
    """Score how well a scenario fits the current data + context.

    Returns 0.0 (poor fit) to 1.0 (excellent fit).
    """
    affinity = SCENARIO_AFFINITIES.get(scenario)
    if not affinity:
        return 0.3  # Unknown scenario gets low neutral score

    # Domain gate: if scenario requires specific domains, check
    if affinity.required_domains and domains is not None:
        if not (affinity.required_domains & domains):
            return 0.0  # Domain mismatch — hard zero

    # Domain bonus: if domain-specific scenario matches detected domain, boost
    domain_bonus = 0.0
    if affinity.required_domains and domains is not None:
        if affinity.required_domains & domains:
            domain_bonus = 0.3  # Strong boost for domain match

    # 1. Query type score
    qt_score = affinity.query_type_affinity.get(query_type, 0.3)

    # 2. Data shape score
    ds_score = 0.0
    ds_weight = 0.0

    def _add(pref: float, match: bool):
        nonlocal ds_score, ds_weight
        if pref > 0:
            ds_weight += pref
            if match:
                ds_score += pref

    if shape:
        _add(affinity.prefers_timeseries, shape.has_timeseries)
        _add(affinity.prefers_alerts, shape.has_alerts)
        _add(affinity.prefers_many_entities, shape.entity_count >= 4)
        _add(affinity.prefers_few_entities, shape.entity_count <= 2)
        _add(affinity.prefers_many_metrics, shape.metric_count >= 4)
        _add(affinity.prefers_high_variance, shape.has_high_variance)
        _add(affinity.prefers_hierarchy, shape.has_hierarchy)
        _add(affinity.prefers_flow, shape.has_flow_metric)
        _add(affinity.prefers_temperature, shape.has_temperature)
        _add(affinity.prefers_binary, shape.has_binary_metric)
        _add(affinity.prefers_cumulative, shape.has_cumulative_metric)
        _add(affinity.prefers_rate, shape.has_rate_metric)
        _add(affinity.prefers_percentage, shape.has_percentage_metric)
        _add(affinity.prefers_correlation,
             shape.multi_numeric_potential and shape.cross_entity_comparable)
        _add(affinity.prefers_dense_timeseries, shape.temporal_density > 100)
        _add(affinity.prefers_phase, shape.has_phase_data)

    raw_fitness = (ds_score / ds_weight) if ds_weight > 0 else 0.5
    # Floor at 0.3: prevents specialized scenarios from scoring near zero
    # just because their unique data preferences don't match generic data.
    # Without this, scenarios like flow-sankey (prefers_flow) get crushed
    # in dashboards with generic power/temperature data.
    shape_fitness = max(0.3, raw_fitness)

    # Additive blend: 55% query type + 35% data shape + domain bonus
    # Higher QT weight ensures scenarios relevant to the query type always
    # compete, even when data shape is generic.
    base = 0.55 * qt_score + 0.35 * shape_fitness

    # Add domain bonus and normalize to [0, 1]
    return round(min(1.0, base + domain_bonus), 4)


def score_all_scenarios(
    shape,
    query_type: str = "overview",
    catalog=None,
    intent=None,
) -> dict[str, float]:
    """Score ALL 24 scenarios based on data properties.

    Returns scenario -> score mapping. Scores of 0.0 mean the scenario
    is not eligible (domain mismatch or missing data requirements).
    """
    # Detect domains from data
    entity_types, column_names = _extract_entity_types_and_columns(catalog, intent)
    domains = detect_domains(entity_types, column_names)

    scores: dict[str, float] = {}
    for scenario in SCENARIO_AFFINITIES:
        scores[scenario] = score_scenario_fitness(
            scenario, shape, query_type, domains,
        )

    return scores
