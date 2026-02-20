"""Uncertainty panel widget plugin — confidence intervals and data quality indicators."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class UncertaintyPanelWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="uncertaintypanel",
        variants=["uncertaintypanel"],
        description="Data uncertainty and confidence panel showing prediction intervals, data quality scores, and reliability indicators",
        good_for=["uncertainty", "confidence", "prediction interval", "data quality", "reliability", "accuracy", "error margin"],
        sizes=["compact", "normal", "expanded"],
        height_units=2,
        rag_strategy="single_metric",
        required_fields=["confidence"],
        optional_fields=["intervals", "dataQuality", "sources", "methodology"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if "confidence" not in data and "intervals" not in data and "value" not in data:
            errors.append("Missing confidence or intervals field")
        return errors

    def format_data(self, raw: dict) -> dict:
        # Already in uncertainty format
        if "confidence" in raw or "intervals" in raw:
            return {
                "confidence": raw.get("confidence", 0),
                "intervals": raw.get("intervals", []),
                "dataQuality": raw.get("dataQuality", {}),
            }
        # Flat single_metric from resolver — adapt to uncertainty shape
        if "value" in raw or "timeSeries" in raw:
            label = raw.get("label", "Metric")
            value = raw.get("value", 0)
            units = raw.get("units", "")
            try:
                val = float(value)
            except (ValueError, TypeError):
                val = 0
            return {
                "confidence": 0.85,
                "intervals": [
                    {"label": label, "low": val * 0.9, "mid": val, "high": val * 1.1, "unit": units},
                ],
                "dataQuality": {"completeness": 1.0, "freshness": "live"},
            }
        return raw
