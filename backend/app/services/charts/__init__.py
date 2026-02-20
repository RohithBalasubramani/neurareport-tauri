# mypy: ignore-errors
"""
Chart Generation Module.

Provides server-side chart generation using:
- QuickChart (Chart.js API)
- Matplotlib (local generation)
"""

from .quickchart import (
    QuickChartClient,
    ChartConfig,
    create_bar_chart,
    create_line_chart,
    create_pie_chart,
    create_scatter_chart,
    generate_chart_url,
    save_chart_image,
)

__all__ = [
    "QuickChartClient",
    "ChartConfig",
    "create_bar_chart",
    "create_line_chart",
    "create_pie_chart",
    "create_scatter_chart",
    "generate_chart_url",
    "save_chart_image",
]
