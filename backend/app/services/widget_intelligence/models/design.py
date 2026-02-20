"""Design models for the widget intelligence pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WidgetSlot:
    id: str = ""
    variant: str = ""
    scenario: str = ""
    size: Any = None
    question: str = ""
    relevance: float = 0.0
    entity_id: str = ""
    table_prefix: str = ""
    entity_confidence: float = 0.0


@dataclass
class GridCell:
    widget_id: str = ""
    col_start: int = 1
    col_end: int = 1
    row_start: int = 1
    row_end: int = 1


@dataclass
class GridLayout:
    cells: list[GridCell] = field(default_factory=list)
    total_cols: int = 12
    total_rows: int = 12
    utilization_pct: float = 0.0


VALID_SCENARIOS: list[str] = [
    "kpi", "alerts", "trend", "trend-multi-line", "trends-cumulative",
    "comparison", "distribution", "composition", "category-bar",
    "flow-sankey", "matrix-heatmap", "timeline", "eventlogstream",
    "narrative", "peopleview", "peoplehexgrid", "peoplenetwork",
    "supplychainglobe", "edgedevicepanel", "chatstream",
    "diagnosticpanel", "uncertaintypanel", "agentsview", "vaultview",
]

# variant -> scenario mapping (built from all widget plugin meta.variants)
VARIANT_TO_SCENARIO: dict[str, str] = {
    # KPI
    "kpi-live": "kpi", "kpi-alert": "kpi", "kpi-accumulated": "kpi",
    "kpi-lifecycle": "kpi", "kpi-status": "kpi",
    # Trend
    "trend-line": "trend", "trend-area": "trend", "trend-step-line": "trend",
    "trend-rgb-phase": "trend", "trend-alert-context": "trend", "trend-heatmap": "trend",
    # Trend Multi-Line
    "trend-multi-line": "trend-multi-line",
    # Trends Cumulative
    "trends-cumulative": "trends-cumulative",
    # Comparison
    "comparison-side-by-side": "comparison", "comparison-delta-bar": "comparison",
    "comparison-grouped-bar": "comparison", "comparison-waterfall": "comparison",
    "comparison-small-multiples": "comparison", "comparison-composition-split": "comparison",
    # Distribution
    "distribution-donut": "distribution", "distribution-100-stacked-bar": "distribution",
    "distribution-horizontal-bar": "distribution", "distribution-pie": "distribution",
    "distribution-grouped-bar": "distribution", "distribution-pareto-bar": "distribution",
    # Composition
    "composition-stacked-bar": "composition", "composition-stacked-area": "composition",
    "composition-donut": "composition", "composition-waterfall": "composition",
    "composition-treemap": "composition",
    # Category Bar
    "category-bar-vertical": "category-bar", "category-bar-horizontal": "category-bar",
    "category-bar-stacked": "category-bar", "category-bar-grouped": "category-bar",
    "category-bar-diverging": "category-bar",
    # Flow Sankey
    "flow-sankey-standard": "flow-sankey", "flow-sankey-energy-balance": "flow-sankey",
    "flow-sankey-multi-source": "flow-sankey", "flow-sankey-layered": "flow-sankey",
    "flow-sankey-time-sliced": "flow-sankey",
    # Matrix Heatmap
    "matrix-heatmap-value": "matrix-heatmap", "matrix-heatmap-correlation": "matrix-heatmap",
    "matrix-heatmap-calendar": "matrix-heatmap", "matrix-heatmap-status": "matrix-heatmap",
    "matrix-heatmap-density": "matrix-heatmap",
    # Timeline
    "timeline-linear": "timeline", "timeline-status": "timeline",
    "timeline-multilane": "timeline", "timeline-forensic": "timeline",
    "timeline-dense": "timeline",
    # Alerts
    "alerts-banner": "alerts", "alerts-toast": "alerts", "alerts-card": "alerts",
    "alerts-badge": "alerts", "alerts-modal": "alerts",
    # Event Log Stream
    "eventlogstream-chronological": "eventlogstream", "eventlogstream-compact-feed": "eventlogstream",
    "eventlogstream-tabular": "eventlogstream", "eventlogstream-correlation": "eventlogstream",
    "eventlogstream-grouped-asset": "eventlogstream",
    # Narrative
    "narrative": "narrative",
    # People View
    "peopleview": "peopleview",
    # People Hex Grid
    "peoplehexgrid": "peoplehexgrid",
    # People Network
    "peoplenetwork": "peoplenetwork",
    # Supply Chain Globe
    "supplychainglobe": "supplychainglobe",
    # Edge Device Panel
    "edgedevicepanel": "edgedevicepanel",
    # Chat Stream
    "chatstream": "chatstream",
    # Diagnostic Panel
    "diagnosticpanel": "diagnosticpanel",
    # Uncertainty Panel
    "uncertaintypanel": "uncertaintypanel",
    # Agents View
    "agentsview": "agentsview",
    # Vault View
    "vaultview": "vaultview",
}
