"""Comparison widget plugin — side-by-side value comparison."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class ComparisonWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="comparison",
        variants=["comparison-side-by-side", "comparison-delta-bar",
                  "comparison-grouped-bar", "comparison-waterfall",
                  "comparison-small-multiples", "comparison-composition-split"],
        description="Side-by-side comparison of multiple metrics or equipment",
        good_for=["comparing equipment", "before/after", "delta analysis", "benchmarking"],
        sizes=["normal", "expanded", "hero"],
        height_units=2,
        rag_strategy="multi_metric",
        required_fields=["items"],
        optional_fields=["labels", "units", "baseline"],
        aggregation="latest_multi",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        summary = data.get("summary", {})
        if len(summary) < 2:
            errors.append("Comparison needs at least 2 items")
        return errors

    def format_data(self, raw: dict) -> dict:
        return raw
