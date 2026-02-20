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
        if not data.get("timeSeries") and not data.get("series") and not data.get("datasets"):
            errors.append("Missing timeSeries data")
        return errors

    def format_data(self, raw: dict) -> dict:
        # Flat format from data resolver — single_metric returns timeSeries + value
        ts = raw.get("timeSeries", [])
        if ts:
            return {
                "labels": [p.get("time", "") for p in ts],
                "datasets": [{
                    "label": raw.get("label", "Value"),
                    "data": [p.get("value", 0) for p in ts],
                }],
            }
        # Already in chart format (labels + datasets)
        if "labels" in raw and "datasets" in raw:
            return raw
        # Legacy nested format
        series = raw.get("series", [])
        return {
            "timeSeries": series[0].get("data", []) if series else [],
            "label": raw.get("meta", {}).get("column", "Value"),
            "units": raw.get("meta", {}).get("unit", ""),
        }
