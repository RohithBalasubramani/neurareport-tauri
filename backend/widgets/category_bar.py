"""Category bar widget plugin."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class CategoryBarWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="category-bar",
        variants=["category-bar-vertical", "category-bar-horizontal",
                  "category-bar-stacked", "category-bar-grouped",
                  "category-bar-diverging"],
        description="Bar chart categorized by equipment or metric type",
        good_for=["category comparison", "ranked values", "fleet overview"],
        sizes=["normal", "expanded", "hero"],
        height_units=3,
        rag_strategy="multi_metric",
        required_fields=["categories", "values"],
        aggregation="latest_multi",
    )

    def validate_data(self, data: dict) -> list[str]:
        return []

    def format_data(self, raw: dict) -> dict:
        return raw
