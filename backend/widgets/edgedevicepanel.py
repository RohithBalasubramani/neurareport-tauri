"""Edge device panel widget plugin — IoT/edge device status and readings."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class EdgeDevicePanelWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="edgedevicepanel",
        variants=["edgedevicepanel"],
        description="Edge/IoT device panel showing device status, sensor readings, connectivity, and alerts",
        good_for=["edge device", "IoT", "sensor", "gateway", "device status", "connectivity", "PLC", "RTU"],
        sizes=["normal", "expanded"],
        height_units=2,
        rag_strategy="single_metric",
        required_fields=["device"],
        optional_fields=["readings", "alerts", "connectivity", "firmware"],
        aggregation="latest",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if not data.get("device"):
            errors.append("Missing device field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return {
            "device": raw.get("device", {}),
            "readings": raw.get("readings", []),
            "alerts": raw.get("alerts", []),
        }

    def get_demo_data(self) -> dict:
        return {
            "device": {"id": "EDG-001", "name": "Gateway A", "status": "online"},
            "readings": [{"sensor": "temperature", "value": 42.5, "unit": "°C"}],
            "alerts": [],
        }
