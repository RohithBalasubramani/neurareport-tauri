"""Trend widget plugin — time-series line/area chart."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class TrendWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="trend",
        variants=["trend-line", "trend-area", "trend-step-line",
                  "trend-rgb-phase", "trend-alert-context", "trend-heatmap"],
        description="Time-series line/area chart for metric over time",
        good_for=["temporal patterns", "anomaly detection", "historical data", "trend analysis"],
        sizes=["normal", "expanded", "hero"],
        height_units=3,
        rag_strategy="single_metric",
        required_fields=["timeSeries"],
        optional_fields=["label", "units", "threshold", "annotations"],
        aggregation="hourly",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        series = data.get("series", [])
        if not series:
            errors.append("Missing timeSeries data")
        return errors

    def format_data(self, raw: dict) -> dict:
        series = raw.get("series", [])
        return {
            "timeSeries": series[0].get("data", []) if series else [],
            "label": raw.get("meta", {}).get("column", "Value"),
            "units": raw.get("meta", {}).get("unit", ""),
        }
