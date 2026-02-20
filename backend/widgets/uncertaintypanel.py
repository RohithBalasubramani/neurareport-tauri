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
        if "confidence" not in data and "intervals" not in data:
            errors.append("Missing confidence or intervals field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return {
            "confidence": raw.get("confidence", 0),
            "intervals": raw.get("intervals", []),
            "dataQuality": raw.get("dataQuality", {}),
        }

    def get_demo_data(self) -> dict:
        return {
            "confidence": 0.87,
            "intervals": [
                {"label": "Prediction", "low": 42.0, "mid": 48.5, "high": 55.0, "unit": "kW"},
            ],
            "dataQuality": {"completeness": 0.95, "freshness": "2min"},
        }
