"""Timeline widget plugin — chronological event timeline."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class TimelineWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="timeline",
        variants=["timeline-linear", "timeline-status", "timeline-multilane",
                  "timeline-forensic", "timeline-dense"],
        description="Chronological timeline of events, status changes, or milestones",
        good_for=["event sequence", "status history", "incident timeline"],
        sizes=["expanded", "hero"],
        height_units=3,
        rag_strategy="events_in_range",
        required_fields=["events"],
        aggregation="raw",
    )

    def validate_data(self, data: dict) -> list[str]:
        return []

    def format_data(self, raw: dict) -> dict:
        return raw
