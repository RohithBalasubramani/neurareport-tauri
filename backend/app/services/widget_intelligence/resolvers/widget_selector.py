"""
Widget selection via data-driven scoring + Thompson Sampling exploration.

Architecture:
1. Data-driven eligibility — DataShapeProfile + domain detection (scenario_scorer.py)
2. Scenario scoring — data shape fitness + query type affinity (no keywords)
3. Thompson Sampling modulation — exploration noise for RL learning
4. Diversity constraint (no more than 2 of same family)
5. 3-layer variant selection pipeline:
   a) LlamaIndex MetadataFilters — hard constraint elimination (variant_metadata.py)
   b) LangGraph constraint graph — data shape + intent scoring (selection_graph.py)
   c) DSPy ChainOfThought — reasoned tie-breaking when ambiguous (dspy_reasoner.py)

All 24 scenarios are first-class citizens. No scenario is "niche" — the system
intelligently detects which scenarios fit the data, not the user's keywords.
"""

from __future__ import annotations

import logging
import random
import re
from dataclasses import dataclass
from typing import Any

from backend.app.services.widget_intelligence.models.intent import ParsedIntent, WidgetSize
from backend.app.services.widget_intelligence.models.data import DataProfile
from backend.app.services.widget_intelligence.models.design import WidgetSlot, VALID_SCENARIOS, VARIANT_TO_SCENARIO
from backend.app.services.widget_intelligence.resolvers.variant_scorer import VARIANT_PROFILES

logger = logging.getLogger(__name__)


@dataclass
class BetaParams:
    """Thompson Sampling Beta distribution parameters per scenario."""
    alpha: float = 1.0  # Success count + 1
    beta: float = 1.0   # Failure count + 1

    def sample(self) -> float:
        """Draw from Beta distribution."""
        return random.betavariate(self.alpha, self.beta)

    def update(self, reward: float):
        """Update parameters based on reward signal."""
        if reward > 0:
            self.alpha += reward
        else:
            self.beta += abs(reward)


# Default variant per scenario
_DEFAULT_VARIANT: dict[str, str] = {
    "kpi": "kpi-live",
    "alerts": "alerts-card",
    "trend": "trend-line",
    "trend-multi-line": "trend-multi-line",
    "trends-cumulative": "trends-cumulative",
    "comparison": "comparison-side-by-side",
    "distribution": "distribution-donut",
    "composition": "composition-stacked-bar",
    "category-bar": "category-bar-vertical",
    "flow-sankey": "flow-sankey-standard",
    "matrix-heatmap": "matrix-heatmap-value",
    "timeline": "timeline-linear",
    "eventlogstream": "eventlogstream-chronological",
    "narrative": "narrative",
    "peopleview": "peopleview",
    "peoplehexgrid": "peoplehexgrid",
    "peoplenetwork": "peoplenetwork",
    "supplychainglobe": "supplychainglobe",
    "edgedevicepanel": "edgedevicepanel",
    "chatstream": "chatstream",
    "diagnosticpanel": "diagnosticpanel",
    "uncertaintypanel": "uncertaintypanel",
    "agentsview": "agentsview",
    "vaultview": "vaultview",
}

# Data requirements per scenario (hard constraints)
_DATA_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "kpi": {"min_tables": 1, "needs_timeseries": True},
    "trend": {"min_tables": 1, "needs_timeseries": True},
    "trend-multi-line": {"min_tables": 1, "needs_timeseries": True},
    "trends-cumulative": {"min_tables": 1, "needs_timeseries": True},
    "comparison": {"min_tables": 1, "needs_timeseries": True},
    "distribution": {"min_tables": 1, "needs_timeseries": True},
    "composition": {"min_tables": 1, "needs_timeseries": True},
    "category-bar": {"min_tables": 1, "needs_timeseries": True},
    "flow-sankey": {"min_tables": 1, "needs_timeseries": True},
    "matrix-heatmap": {"min_tables": 1, "needs_timeseries": True},
    "timeline": {"min_tables": 1, "needs_timeseries": True},
    "alerts": {"min_tables": 1, "needs_timeseries": True},
    "eventlogstream": {"min_tables": 1, "needs_timeseries": True},
    "peopleview": {"min_tables": 1, "needs_timeseries": False},
    "peoplehexgrid": {"min_tables": 1, "needs_timeseries": False},
    "peoplenetwork": {"min_tables": 1, "needs_timeseries": False},
    "supplychainglobe": {"min_tables": 1, "needs_timeseries": False},
    "narrative": {"min_tables": 0, "needs_timeseries": False},
    "edgedevicepanel": {"min_tables": 1, "needs_timeseries": False},
    "chatstream": {"min_tables": 0, "needs_timeseries": False},
    "diagnosticpanel": {"min_tables": 1, "needs_timeseries": False},
    "uncertaintypanel": {"min_tables": 1, "needs_timeseries": False},
    "agentsview": {"min_tables": 0, "needs_timeseries": False},
    "vaultview": {"min_tables": 0, "needs_timeseries": False},
}

# Build scenario → [variants] reverse map for variant-aware selection
_SCENARIO_VARIANTS: dict[str, list[str]] = {}
for _v, _s in VARIANT_TO_SCENARIO.items():
    _SCENARIO_VARIANTS.setdefault(_s, []).append(_v)

# Category caps — maximum scenarios per category in a single dashboard.
# Greedy selection picks the highest-scoring scenario that doesn't exceed
# its category cap. This ensures diversity without rigid slot reservation.
_CATEGORY_MAP: dict[str, str] = {
    "kpi": "anchor",
    "trend": "trend", "trend-multi-line": "trend", "trends-cumulative": "trend",
    "comparison": "analysis", "distribution": "analysis", "composition": "analysis",
    "category-bar": "analysis", "flow-sankey": "analysis", "matrix-heatmap": "analysis",
    "timeline": "context", "eventlogstream": "context",
    "alerts": "alerts", "narrative": "context",
    "peopleview": "domain", "peoplehexgrid": "domain", "peoplenetwork": "domain",
    "supplychainglobe": "domain", "edgedevicepanel": "domain",
    "chatstream": "domain", "diagnosticpanel": "domain",
    "uncertaintypanel": "domain", "agentsview": "domain", "vaultview": "domain",
}
_CATEGORY_CAPS: dict[str, int] = {
    "anchor": 1,    # Always 1 KPI
    "trend": 2,     # Up to 2 trend types
    "analysis": 4,  # Up to 4 different analysis views
    "context": 2,   # Up to 2 contextual widgets (timeline, eventlog, narrative)
    "alerts": 1,    # Up to 1 alert widget
    "domain": 3,    # Up to 3 domain-specific widgets (e.g., 3 people scenarios)
}


class WidgetSelector:
    """
    Select widgets using data-driven scoring + Thompson Sampling exploration.

    All 24 scenarios compete on equal footing. Domain-specific scenarios are
    gated by data domain detection (entity types + column names), not keywords.
    Core scenarios are scored by DataShapeProfile fitness.
    """

    def __init__(self):
        # Thompson Sampling parameters per scenario
        self._posteriors: dict[str, BetaParams] = {
            s: BetaParams() for s in VALID_SCENARIOS
        }

    def select(
        self,
        intent: ParsedIntent,
        data_profile: DataProfile,
        max_widgets: int = 10,
        questions: list[str] | None = None,
        question_dicts: list[dict] | None = None,
        catalog: Any = None,
        embedding_client: Any = None,
        query_embedding: list[float] | None = None,
    ) -> list[WidgetSlot]:
        """
        Select widgets for a dashboard.

        1. Extract DataShapeProfile from catalog
        2. Score all scenarios using data-driven fitness (scenario_scorer)
        3. Filter by hard data requirements
        4. Modulate with Thompson Sampling for exploration
        5. Pick top-K with diversity constraint
        6. Assign questions with entity diversity maximization
        7. Select variant per scenario via LangGraph pipeline
        """
        from backend.app.services.widget_intelligence.resolvers.data_shape import extract_data_shape
        from backend.app.services.widget_intelligence.resolvers.scenario_scorer import score_all_scenarios

        # Step 1: Extract data shape profile
        shape = extract_data_shape(catalog, data_profile, intent)

        # Step 2: Score all scenarios using data-driven fitness
        scenario_scores = score_all_scenarios(
            shape=shape,
            query_type=intent.query_type.value,
            catalog=catalog,
            intent=intent,
        )

        # Step 3: Hard data requirements filter
        eligible = self._filter_eligible(data_profile)

        # Always include KPI
        if "kpi" not in eligible:
            eligible.add("kpi")

        # Step 4: Combine data-driven scores with Thompson Sampling
        scores: list[tuple[str, float]] = []
        for scenario in eligible:
            data_score = scenario_scores.get(scenario, 0.0)
            if data_score <= 0.0:
                continue  # Domain mismatch — skip entirely
            ts_score = self._posteriors[scenario].sample()
            # Blend: 85% data-driven + 15% Thompson Sampling (exploration)
            # High data weight ensures the right scenarios are selected;
            # low TS weight provides enough noise for RL exploration.
            combined = 0.85 * data_score + 0.15 * ts_score
            scores.append((scenario, combined))

        scores.sort(key=lambda x: x[1], reverse=True)

        # Step 5: Greedy selection with category caps
        # Pick highest-scoring scenarios while respecting per-category limits.
        # This ensures diverse dashboards without rigid slot reservation —
        # high-scoring domain scenarios naturally compete with core scenarios.
        selected: list[str] = []
        cat_counts: dict[str, int] = {}
        for scenario, score in scores:
            if len(selected) >= max_widgets:
                break
            cat = _CATEGORY_MAP.get(scenario, "analysis")
            cap = _CATEGORY_CAPS.get(cat, 2)
            if cat_counts.get(cat, 0) < cap:
                selected.append(scenario)
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

        # Guarantee KPI in final layout
        if "kpi" in eligible and "kpi" not in selected:
            if len(selected) < max_widgets:
                selected.append("kpi")
            elif selected:
                selected[-1] = "kpi"

        # Step 6: Assign questions with entity diversity maximization
        q_dicts = question_dicts or []
        widget_questions = questions or intent.sub_questions or []
        available_qs = list(range(len(q_dicts)))

        assignments: list[tuple[str, dict, str]] = []
        used_prefixes: set[str] = set()
        used_instances: set[str] = set()

        for scenario in selected:
            best_idx = None
            best_score = -1

            for qi in available_qs:
                qd = q_dicts[qi] if qi < len(q_dicts) else {}
                prefix = qd.get("table_prefix", "")
                text_lower = qd.get("text", "").lower()

                inst_match = re.search(r'([a-z_]{2,})-(\d{2,3})', text_lower)
                inst_id = f"{inst_match.group(1)}_{inst_match.group(2)}" if inst_match else ""

                score = 0
                if prefix and prefix not in used_prefixes:
                    score += 2
                if inst_id and inst_id not in used_instances:
                    score += 1

                if score > best_score:
                    best_score = score
                    best_idx = qi

            if best_idx is None and available_qs:
                best_idx = available_qs[0]

            if best_idx is not None:
                available_qs.remove(best_idx)
                qd = q_dicts[best_idx] if best_idx < len(q_dicts) else {}
                text = qd.get("text", "") or (widget_questions[best_idx] if best_idx < len(widget_questions) else "")
                prefix = qd.get("table_prefix", "")
                if prefix:
                    used_prefixes.add(prefix)
                inst_match = re.search(r'([a-z_]{2,})-(\d{2,3})', (text or "").lower())
                if inst_match:
                    used_instances.add(f"{inst_match.group(1)}_{inst_match.group(2)}")
                assignments.append((scenario, qd, text or f"Widget {len(assignments)+1}"))
            else:
                assignments.append((scenario, {}, f"Widget {len(assignments)+1}"))

        # Step 7: Build WidgetSlot list with variant selection
        widgets: list[WidgetSlot] = []
        for i, (scenario, qd, question) in enumerate(assignments):
            variant = self._choose_variant(
                scenario, intent, question, qd, data_profile, catalog,
                embedding_client=embedding_client,
                query_embedding=query_embedding,
            )
            widgets.append(WidgetSlot(
                id=f"w{i+1}",
                variant=variant,
                scenario=scenario,
                size=WidgetSize.normal,
                question=question,
                relevance=round(0.6 + 0.4 * (1 - i / max(len(selected), 1)), 2),
                entity_id=qd.get("entity_id", ""),
                table_prefix=qd.get("table_prefix", ""),
                entity_confidence=float(qd.get("entity_confidence", 0.0)),
            ))

        return widgets

    def update(self, scenario: str, reward: float):
        """Update Thompson Sampling posterior for a scenario after feedback."""
        if scenario in self._posteriors:
            self._posteriors[scenario].update(reward)

    def _filter_eligible(self, profile: DataProfile) -> set[str]:
        """Filter scenarios based on hard data requirements only.

        Domain-based eligibility is handled by scenario_scorer.py which
        returns 0.0 for domain mismatches. This method only checks
        timeseries availability and minimum table counts.
        """
        eligible: set[str] = set()
        for scenario, reqs in _DATA_REQUIREMENTS.items():
            min_tables = reqs.get("min_tables", 0)
            needs_ts = reqs.get("needs_timeseries", False)

            if needs_ts and not profile.has_timeseries:
                continue
            if profile.table_count < min_tables:
                continue
            eligible.add(scenario)

        # Ensure minimum viable set
        minimum = {"kpi", "trend"}
        if profile.has_timeseries:
            eligible |= minimum

        return eligible

    def _choose_variant(
        self,
        scenario: str,
        intent: ParsedIntent,
        question: str,
        question_dict: dict | None = None,
        data_profile: DataProfile | None = None,
        catalog: Any = None,
        embedding_client: Any = None,
        query_embedding: list[float] | None = None,
    ) -> str:
        """Choose the best variant using the 3-layer selection pipeline.

        Pipeline (all layers integrated in LangGraph constraint graph):
        1. LlamaIndex MetadataFilters — hard constraint elimination
        2. Data shape + intent scoring — ranked composite
        3. DSPy ChainOfThought — reasoned tie-breaking (when ambiguous)

        Selection based on measurable data properties (variance, cardinality,
        metric type, hierarchy, temporal density), not keywords.
        """
        # Single-variant scenarios → no selection needed
        if scenario not in VARIANT_PROFILES:
            return _DEFAULT_VARIANT.get(scenario, scenario)

        text = (intent.original_query + " " + question).lower()
        qd = question_dict or {}

        # Extract context signals
        question_intent = qd.get("intent", "")
        entity_count = len(intent.entities) if intent.entities else 1
        metric_count = len(intent.metrics) if intent.metrics else 1
        instance_count = sum(
            len(e.instances) for e in intent.entities
        ) if intent.entities else (
            data_profile.table_count if data_profile else 1
        )
        if data_profile:
            metric_count = max(metric_count, data_profile.numeric_column_count)
        has_timeseries = data_profile.has_timeseries if data_profile else True

        try:
            from backend.app.services.widget_intelligence.resolvers.selection_graph import run_selection_graph

            variant, confidence, method = run_selection_graph(
                scenario=scenario,
                query_text=text,
                question_intent=question_intent,
                query_type=intent.query_type.value,
                entity_count=entity_count,
                metric_count=metric_count,
                instance_count=instance_count,
                has_timeseries=has_timeseries,
                catalog=catalog,
                data_profile=data_profile,
                intent=intent,
                query_embedding=query_embedding,
                embedding_client=embedding_client,
            )

            # Guard: ensure variant belongs to this scenario
            valid_variants = set(VARIANT_PROFILES.get(scenario, {}).keys())
            if valid_variants and variant not in valid_variants:
                logger.warning(
                    f"[WidgetSelector] Cross-scenario leak: {scenario} got {variant}, "
                    f"using default"
                )
                return _DEFAULT_VARIANT.get(scenario, scenario)

            return variant

        except Exception as e:
            logger.debug(f"[WidgetSelector] Selection graph failed: {e}")

        # Fallback: scenario default
        return _DEFAULT_VARIANT.get(scenario, scenario)
