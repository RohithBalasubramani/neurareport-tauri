"""Alerts widget plugin — alert notification panel."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class AlertsWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="alerts",
        variants=["alerts-banner", "alerts-toast", "alerts-card",
                  "alerts-badge", "alerts-modal"],
        description="Alert notification panel showing active alarms and warnings",
        good_for=["active alerts", "alarm summary", "warning notifications", "critical events"],
        sizes=["compact", "normal", "expanded"],
        height_units=2,
        rag_strategy="alert_query",
        required_fields=["alerts"],
        optional_fields=["severity", "count", "acknowledged"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        return []

    def format_data(self, raw: dict) -> dict:
        return raw
