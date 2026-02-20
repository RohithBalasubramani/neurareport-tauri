"""KPI widget plugin — single metric display."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class KPIWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="kpi",
        variants=["kpi-live", "kpi-alert", "kpi-accumulated", "kpi-lifecycle", "kpi-status"],
        description="Single metric display with value, trend indicator, and unit",
        good_for=["single metric", "status", "live reading", "threshold monitoring"],
        sizes=["compact", "normal"],
        height_units=1,
        rag_strategy="single_metric",
        required_fields=["value"],
        optional_fields=["label", "units", "trend", "threshold", "status"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        summary = data.get("summary", {}).get("value", {})
        if not summary and "value" not in data:
            errors.append("Missing value field")
        return errors

    def format_data(self, raw: dict) -> dict:
        summary = raw.get("summary", {}).get("value", {})
        return {
            "value": summary.get("latest", 0),
            "label": raw.get("meta", {}).get("column", "Metric"),
            "units": raw.get("meta", {}).get("unit", ""),
            "trend": summary.get("trend", "stable"),
        }
