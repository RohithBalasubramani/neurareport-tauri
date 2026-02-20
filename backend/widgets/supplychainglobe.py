"""Supply chain globe widget plugin — 3D globe with supply routes."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class SupplyChainGlobeWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="supplychainglobe",
        variants=["supplychainglobe"],
        description="3D globe visualization of supply chain routes and logistics",
        good_for=["logistics overview", "supply routes", "global operations"],
        sizes=["hero"],
        height_units=6,
        rag_strategy="flow_analysis",
        required_fields=["routes"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if "routes" not in data:
            errors.append("Missing routes field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return raw
