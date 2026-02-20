"""People network widget plugin — organizational network graph."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class PeopleNetworkWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="peoplenetwork",
        variants=["peoplenetwork"],
        description="Network graph showing team relationships and communication patterns",
        good_for=["org structure", "team connections", "communication flow"],
        sizes=["expanded", "hero"],
        height_units=4,
        rag_strategy="alert_query",
        required_fields=["nodes", "edges"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if "nodes" not in data:
            errors.append("Missing nodes field")
        if "edges" not in data:
            errors.append("Missing edges field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return raw
