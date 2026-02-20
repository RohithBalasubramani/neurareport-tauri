"""
Widget Intelligence Service — facade over widget selection + grid packing.

Provides a clean API for:
- Widget catalog browsing
- AI-powered widget selection for dashboard composition
- Deterministic CSS grid packing
- Widget data validation and formatting
- Thompson Sampling feedback
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from backend.app.services.widget_intelligence.models.intent import (
    ParsedIntent, QueryType, WidgetSize,
)
from backend.app.services.widget_intelligence.models.data import DataProfile
from backend.app.services.widget_intelligence.models.design import WidgetSlot
from backend.app.services.widget_intelligence.widgets.base import WidgetRegistry

logger = logging.getLogger("neura.widget_intelligence")


class WidgetIntelligenceService:
    """Facade over the widget selection + grid packing pipeline."""

    def __init__(self):
        self._registry = WidgetRegistry()
        self._selector = None  # Lazy-loaded to avoid heavy imports at startup

    def _get_selector(self):
        if self._selector is None:
            try:
                from backend.app.services.widget_intelligence.resolvers.widget_selector import WidgetSelector
                self._selector = WidgetSelector()
            except Exception as e:
                logger.warning(f"WidgetSelector unavailable: {e}")
        return self._selector

    # ── Catalog ──────────────────────────────────────────────────────────

    def get_catalog(self) -> list[dict[str, Any]]:
        """Return all registered widget scenarios with their metadata."""
        result = []
        for scenario in self._registry.scenarios:
            plugin = self._registry.get(scenario)
            if plugin:
                m = plugin.meta
                result.append({
                    "scenario": m.scenario,
                    "variants": m.variants,
                    "description": m.description,
                    "good_for": m.good_for,
                    "sizes": m.sizes,
                    "height_units": m.height_units,
                    "rag_strategy": m.rag_strategy,
                    "required_fields": m.required_fields,
                    "optional_fields": m.optional_fields,
                    "aggregation": m.aggregation,
                })
        return result

    # ── Selection ────────────────────────────────────────────────────────

    def select_widgets(
        self,
        query: str,
        query_type: str = "overview",
        data_profile: Optional[dict] = None,
        max_widgets: int = 10,
    ) -> list[dict[str, Any]]:
        """Select optimal widgets for a query using data-driven scoring."""
        selector = self._get_selector()
        if selector is None:
            # Fallback: return a simple default set
            return self._fallback_selection(max_widgets)

        try:
            qt = QueryType(query_type) if query_type in QueryType.__members__ else QueryType.overview
        except ValueError:
            qt = QueryType.overview

        intent = ParsedIntent(original_query=query, query_type=qt)
        profile = DataProfile(**(data_profile or {}))

        try:
            slots = selector.select(
                intent=intent,
                data_profile=profile,
                max_widgets=max_widgets,
            )
        except Exception as e:
            logger.warning(f"Widget selection failed: {e}")
            return self._fallback_selection(max_widgets)

        return [
            {
                "id": s.id,
                "scenario": s.scenario,
                "variant": s.variant,
                "size": s.size.value if hasattr(s.size, "value") else str(s.size),
                "question": s.question,
                "relevance": s.relevance,
            }
            for s in slots
        ]

    def _fallback_selection(self, max_widgets: int) -> list[dict[str, Any]]:
        """Return a sensible default widget set when selector is unavailable."""
        defaults = [
            ("kpi", "kpi-live", "compact"),
            ("trend", "trend-line", "normal"),
            ("comparison", "comparison-side-by-side", "normal"),
            ("distribution", "distribution-donut", "normal"),
            ("alerts", "alerts-card", "compact"),
            ("narrative", "narrative", "normal"),
            ("timeline", "timeline-linear", "expanded"),
            ("category-bar", "category-bar-vertical", "normal"),
        ]
        return [
            {
                "id": f"w{i+1}",
                "scenario": scenario,
                "variant": variant,
                "size": size,
                "question": f"Widget {i+1}",
                "relevance": round(1.0 - i * 0.1, 2),
            }
            for i, (scenario, variant, size) in enumerate(defaults[:max_widgets])
        ]

    # ── Grid Packing ────────────────────────────────────────────────────

    def pack_grid(self, widgets: list[dict[str, Any]]) -> dict[str, Any]:
        """Pack widget slots into a CSS grid layout."""
        from backend.app.services.widget_intelligence.resolvers.grid_packer import pack_grid

        slots = []
        for i, w in enumerate(widgets):
            try:
                size = WidgetSize(w.get("size", "normal"))
            except ValueError:
                size = WidgetSize.normal
            slots.append(WidgetSlot(
                id=w.get("id", f"w{i}"),
                scenario=w.get("scenario", ""),
                variant=w.get("variant", ""),
                size=size,
            ))

        layout = pack_grid(slots)
        return {
            "cells": [
                {
                    "widget_id": c.widget_id,
                    "col_start": c.col_start,
                    "col_end": c.col_end,
                    "row_start": c.row_start,
                    "row_end": c.row_end,
                }
                for c in layout.cells
            ],
            "total_cols": layout.total_cols,
            "total_rows": layout.total_rows,
            "utilization_pct": layout.utilization_pct,
        }

    # ── Validation ───────────────────────────────────────────────────────

    def validate_data(self, scenario: str, data: dict) -> list[str]:
        """Validate data shape for a widget scenario."""
        plugin = self._registry.get(scenario)
        if not plugin:
            return [f"Unknown scenario: {scenario}"]
        return plugin.validate_data(data)

    # ── Format ───────────────────────────────────────────────────────────

    def format_data(self, scenario: str, raw: dict) -> dict[str, Any]:
        """Format raw data into frontend-ready shape for a widget scenario."""
        plugin = self._registry.get(scenario)
        if not plugin:
            return raw
        return plugin.format_data(raw)

    # ── Feedback ─────────────────────────────────────────────────────────

    def update_feedback(self, scenario: str, reward: float):
        """Update Thompson Sampling posterior for a scenario."""
        selector = self._get_selector()
        if selector:
            selector.update(scenario, reward)
