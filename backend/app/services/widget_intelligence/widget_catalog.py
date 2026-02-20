"""Widget catalog auto-generated from widget plugins for semantic_embedder.py."""
from __future__ import annotations

from typing import Any

WIDGET_CATALOG: list[dict[str, Any]] = []


def get_widget_catalog() -> list[dict[str, Any]]:
    """Build and cache WIDGET_CATALOG from WidgetRegistry."""
    global WIDGET_CATALOG
    if not WIDGET_CATALOG:
        try:
            from backend.app.services.widget_intelligence.widgets.base import WidgetRegistry
            registry = WidgetRegistry()
            for scenario in registry.scenarios:
                plugin = registry.get(scenario)
                if plugin:
                    m = plugin.meta
                    WIDGET_CATALOG.append({
                        "scenario": m.scenario,
                        "description": m.description,
                        "good_for": m.good_for,
                        "variants": {v: m.description for v in m.variants},
                    })
        except Exception:
            pass
    return WIDGET_CATALOG
