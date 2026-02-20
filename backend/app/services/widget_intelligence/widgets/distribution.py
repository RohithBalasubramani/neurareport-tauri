"""Distribution widget plugin — pie/donut/bar breakdown."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class DistributionWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="distribution",
        variants=["distribution-donut", "distribution-100-stacked-bar",
                  "distribution-horizontal-bar", "distribution-pie",
                  "distribution-grouped-bar", "distribution-pareto-bar"],
        description="Pie/donut/bar chart showing value distribution across categories",
        good_for=["proportional breakdown", "share analysis", "category distribution"],
        sizes=["normal", "expanded"],
        height_units=3,
        rag_strategy="multi_metric",
        required_fields=["items"],
        optional_fields=["labels", "colors", "total"],
        aggregation="latest_multi",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        summary = data.get("summary", {})
        if len(summary) < 2:
            errors.append("Distribution needs at least 2 items")
        return errors

    def format_data(self, raw: dict) -> dict:
        return raw
