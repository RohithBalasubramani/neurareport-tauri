"""Matrix heatmap widget plugin."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class MatrixHeatmapWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="matrix-heatmap",
        variants=["matrix-heatmap-value", "matrix-heatmap-correlation",
                  "matrix-heatmap-calendar", "matrix-heatmap-status",
                  "matrix-heatmap-density"],
        description="Color-coded 2D matrix showing values across two dimensions",
        good_for=["correlation matrix", "time-of-day patterns", "equipment vs metric"],
        sizes=["expanded", "hero"],
        height_units=4,
        rag_strategy="multi_metric",
        required_fields=["matrix"],
        aggregation="latest_multi",
    )

    def validate_data(self, data: dict) -> list[str]:
        return []

    def format_data(self, raw: dict) -> dict:
        return raw
