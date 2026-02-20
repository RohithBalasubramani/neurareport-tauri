"""Flow Sankey widget plugin — energy/material flow diagram."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class FlowSankeyWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="flow-sankey",
        variants=["flow-sankey-standard", "flow-sankey-energy-balance",
                  "flow-sankey-multi-source", "flow-sankey-layered",
                  "flow-sankey-time-sliced"],
        description="Sankey/flow diagram showing energy or material flows between nodes",
        good_for=["energy flow", "power distribution", "material balance", "source-to-load"],
        sizes=["expanded", "hero"],
        height_units=4,
        rag_strategy="flow_analysis",
        required_fields=["nodes", "links"],
        aggregation="latest_multi",
    )

    def validate_data(self, data: dict) -> list[str]:
        return []

    def format_data(self, raw: dict) -> dict:
        return raw
