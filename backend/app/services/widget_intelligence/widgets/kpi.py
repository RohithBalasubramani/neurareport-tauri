"""KPI widget plugin — single metric display."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


def _to_num(v):
    """Coerce to float, return None on failure."""
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0


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
        if "value" not in data and not data.get("summary", {}).get("value"):
            errors.append("Missing value field")
        return errors

    def format_data(self, raw: dict) -> dict:
        # Flat format from data resolver
        if "value" in raw or "timeSeries" in raw:
            return {
                "value": _to_num(raw.get("value", 0)),
                "label": raw.get("label", "Metric"),
                "units": raw.get("units", ""),
                "trend": raw.get("trend", "stable"),
                "previousValue": _to_num(raw.get("previousValue")),
                "timeSeries": raw.get("timeSeries", []),
                "threshold": raw.get("threshold"),
                "status": raw.get("status", "ok"),
            }
        # Legacy nested format
        summary = raw.get("summary", {}).get("value", {})
        return {
            "value": summary.get("latest", 0),
            "label": raw.get("meta", {}).get("column", "Metric"),
            "units": raw.get("meta", {}).get("unit", ""),
            "trend": summary.get("trend", "stable"),
        }
