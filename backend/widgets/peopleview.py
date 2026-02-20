"""People view widget plugin — personnel overview card."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class PeopleViewWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="peopleview",
        variants=["peopleview"],
        description="Personnel overview showing worker status and assignments",
        good_for=["workforce status", "shift personnel", "crew overview"],
        sizes=["normal", "expanded"],
        height_units=3,
        rag_strategy="alert_query",
        required_fields=["people"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if "people" not in data:
            errors.append("Missing people field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return raw
