"""Diagnostic panel widget plugin — equipment diagnostics and health checks."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class DiagnosticPanelWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="diagnosticpanel",
        variants=["diagnosticpanel"],
        description="Equipment diagnostic panel showing health checks, test results, fault codes, and maintenance recommendations",
        good_for=["diagnostic", "health check", "fault code", "troubleshoot", "root cause", "maintenance", "inspection"],
        sizes=["normal", "expanded"],
        height_units=3,
        rag_strategy="single_metric",
        required_fields=["checks"],
        optional_fields=["equipment", "faultCodes", "recommendations", "lastInspection"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if not data.get("checks") and not data.get("equipment") and "value" not in data:
            errors.append("Missing checks or equipment field")
        return errors

    def format_data(self, raw: dict) -> dict:
        # Already in diagnostic format
        if "checks" in raw:
            return {
                "checks": raw["checks"],
                "equipment": raw.get("equipment", ""),
                "faultCodes": raw.get("faultCodes", []),
                "recommendations": raw.get("recommendations", []),
            }
        # Flat single_metric from resolver — adapt to diagnostic shape
        if "value" in raw or "timeSeries" in raw:
            label = raw.get("label", "Metric")
            value = raw.get("value", 0)
            try:
                value = float(value)
            except (ValueError, TypeError):
                value = 0
            return {
                "checks": [
                    {"name": label, "status": "pass" if value > 0 else "warning", "value": str(value)},
                ],
                "equipment": raw.get("label", "System"),
                "faultCodes": [],
                "recommendations": [],
            }
        return raw
