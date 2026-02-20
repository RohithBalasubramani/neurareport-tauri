"""Chat stream widget plugin — conversational message feed."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class ChatStreamWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="chatstream",
        variants=["chatstream"],
        description="Conversational chat stream showing AI-generated messages, operator notes, or system dialogue",
        good_for=["chat", "conversation", "messages", "operator notes", "AI response", "dialogue"],
        sizes=["normal", "expanded"],
        height_units=3,
        rag_strategy="none",
        required_fields=["messages"],
        optional_fields=["title", "participants"],
        aggregation="none",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        messages = data.get("messages")
        if not isinstance(messages, list):
            errors.append("Missing or invalid messages field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return {
            "messages": raw.get("messages", []),
        }
