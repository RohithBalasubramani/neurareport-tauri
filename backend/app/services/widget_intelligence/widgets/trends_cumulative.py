"""Trends cumulative widget plugin — accumulated value over time."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class TrendsCumulativeWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="trends-cumulative",
        variants=["trends-cumulative"],
        description="Cumulative/running total chart showing accumulated values over time",
        good_for=["energy consumption", "production output", "running totals"],
        sizes=["expanded", "hero"],
        height_units=3,
        rag_strategy="single_metric",
        required_fields=["timeSeries"],
        aggregation="hourly",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if "timeSeries" not in data:
            errors.append("Missing timeSeries field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return raw
