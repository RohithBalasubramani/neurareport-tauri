"""People hex-grid widget plugin — hexagonal personnel map."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class PeopleHexGridWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="peoplehexgrid",
        variants=["peoplehexgrid"],
        description="Hexagonal grid showing personnel distribution across zones",
        good_for=["zone staffing", "spatial workforce view", "facility map"],
        sizes=["expanded", "hero"],
        height_units=4,
        rag_strategy="alert_query",
        required_fields=["hexCells"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if "hexCells" not in data:
            errors.append("Missing hexCells field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return raw
