"""Composition widget plugin — stacked bar/area composition."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class CompositionWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="composition",
        variants=["composition-stacked-bar", "composition-stacked-area",
                  "composition-donut", "composition-waterfall", "composition-treemap"],
        description="Stacked bar/area showing how parts compose a whole",
        good_for=["part-of-whole", "energy mix", "load composition", "source breakdown"],
        sizes=["normal", "expanded", "hero"],
        height_units=3,
        rag_strategy="multi_metric",
        required_fields=["items"],
        aggregation="latest_multi",
    )

    def validate_data(self, data: dict) -> list[str]:
        return []

    def format_data(self, raw: dict) -> dict:
        return raw
