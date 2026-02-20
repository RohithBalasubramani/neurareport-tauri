"""Narrative widget plugin — text-based insight summary."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class NarrativeWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="narrative",
        variants=["narrative"],
        description="Text-based narrative summary of key insights, findings, or recommendations",
        good_for=["summary", "insight", "explanation", "context", "recommendation", "narrative"],
        sizes=["compact", "normal", "expanded"],
        height_units=2,
        rag_strategy="narrative",
        required_fields=["text"],
        optional_fields=["title", "highlights", "citations"],
        aggregation="none",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if not data.get("text"):
            errors.append("Missing text field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return {
            "text": raw.get("text", ""),
            "title": raw.get("title", ""),
        }

    def get_demo_data(self) -> dict:
        return {
            "text": "System performance remains within normal parameters.",
            "title": "Summary",
        }
