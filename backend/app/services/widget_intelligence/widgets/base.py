"""
Widget plugin base class and auto-discovery registry.

To add a new widget: drop a file in pipeline_v7/widgets/ with a class
that extends WidgetPlugin. It auto-registers — no other files to change.
"""

from __future__ import annotations

import importlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class WidgetMeta:
    """Metadata describing a widget type — replaces entries in widget_catalog.py and widget_schemas.py."""
    scenario: str
    variants: list[str]
    description: str
    good_for: list[str]
    sizes: list[str]
    height_units: int = 2
    rag_strategy: str = "single_metric"
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    aggregation: str = "latest"


class WidgetPlugin(ABC):
    """
    Base class for widget plugins.

    Each widget type is a single file in pipeline_v7/widgets/.
    Implements: meta, validate_data, format_data.
    """

    meta: WidgetMeta

    @abstractmethod
    def validate_data(self, data: dict) -> list[str]:
        """Validate data shape for this widget. Returns list of error messages."""
        ...

    @abstractmethod
    def format_data(self, raw: dict) -> dict:
        """Transform raw query result into frontend-ready data shape."""
        ...



class WidgetRegistry:
    """
    Auto-discovery registry for widget plugins.

    Scans pipeline_v7/widgets/ directory and registers all WidgetPlugin subclasses.
    """

    def __init__(self):
        self._plugins: dict[str, WidgetPlugin] = {}
        self._variant_to_scenario: dict[str, str] = {}
        self._discover_plugins()

    def _discover_plugins(self):
        """Scan widgets directory and import all plugins."""
        widgets_dir = Path(__file__).parent
        for path in widgets_dir.glob("*.py"):
            if path.name.startswith("_") or path.name == "base.py":
                continue
            try:
                module = importlib.import_module(f"backend.app.services.widget_intelligence.widgets.{path.stem}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and issubclass(attr, WidgetPlugin)
                            and attr is not WidgetPlugin and hasattr(attr, "meta")):
                        plugin = attr()
                        self._plugins[plugin.meta.scenario] = plugin
                        for variant in plugin.meta.variants:
                            self._variant_to_scenario[variant] = plugin.meta.scenario
                        logger.debug(f"[WidgetRegistry] Registered: {plugin.meta.scenario}")
            except Exception as e:
                logger.warning(f"[WidgetRegistry] Failed to load {path.name}: {e}")

        logger.info(f"[WidgetRegistry] {len(self._plugins)} widgets registered")

    def get(self, scenario: str) -> WidgetPlugin | None:
        """Get plugin by scenario name."""
        return self._plugins.get(scenario)

    def get_by_variant(self, variant: str) -> WidgetPlugin | None:
        """Get plugin by variant key."""
        scenario = self._variant_to_scenario.get(variant)
        if scenario:
            return self._plugins.get(scenario)
        return None

    @property
    def scenarios(self) -> list[str]:
        """List all registered scenarios."""
        return list(self._plugins.keys())

    @property
    def variants(self) -> list[str]:
        """List all registered variants."""
        return list(self._variant_to_scenario.keys())

    def get_catalog_prompt(self) -> str:
        """Format all widgets as text for LLM prompts."""
        lines = []
        for scenario, plugin in sorted(self._plugins.items()):
            m = plugin.meta
            lines.append(
                f"  {scenario}: {m.description} "
                f"(sizes: {', '.join(m.sizes)}, "
                f"variants: {', '.join(m.variants[:3])}...)"
            )
        return "\n".join(lines)
