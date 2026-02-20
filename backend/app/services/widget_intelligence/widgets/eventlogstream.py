"""Event log stream widget plugin."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class EventLogStreamWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="eventlogstream",
        variants=["eventlogstream-chronological", "eventlogstream-compact-feed",
                  "eventlogstream-tabular", "eventlogstream-correlation",
                  "eventlogstream-grouped-asset"],
        description="Real-time scrolling log of system events and alerts",
        good_for=["live events", "log monitoring", "alert feed"],
        sizes=["normal", "expanded", "hero"],
        height_units=4,
        rag_strategy="alert_query",
        required_fields=["events"],
        aggregation="raw",
    )

    def validate_data(self, data: dict) -> list[str]:
        return []

    def format_data(self, raw: dict) -> dict:
        return raw
