"""Trend multi-line widget plugin — multiple time series on one chart."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class TrendMultiLineWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="trend-multi-line",
        variants=["trend-multi-line"],
        description="Multiple time-series lines overlaid for comparison",
        good_for=["multi-metric comparison", "parallel trends", "correlation"],
        sizes=["expanded", "hero"],
        height_units=3,
        rag_strategy="multi_metric",
        required_fields=["series"],
        aggregation="hourly",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if "series" not in data:
            errors.append("Missing series field")
        elif not isinstance(data["series"], list) or len(data["series"]) < 2:
            errors.append("series must be a list with at least 2 entries")
        return errors

    def format_data(self, raw: dict) -> dict:
        return raw
