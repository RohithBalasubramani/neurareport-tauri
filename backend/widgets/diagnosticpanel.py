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
        if not data.get("checks") and not data.get("equipment"):
            errors.append("Missing checks or equipment field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return {
            "checks": raw.get("checks", []),
            "equipment": raw.get("equipment", ""),
            "faultCodes": raw.get("faultCodes", []),
            "recommendations": raw.get("recommendations", []),
        }

    def get_demo_data(self) -> dict:
        return {
            "equipment": "Motor A",
            "checks": [
                {"name": "Vibration", "status": "pass", "value": "0.8 mm/s"},
                {"name": "Temperature", "status": "warning", "value": "78°C"},
            ],
            "faultCodes": [],
            "recommendations": ["Schedule bearing inspection within 30 days"],
        }
