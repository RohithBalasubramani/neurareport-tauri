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
        if not data.get("device") and "value" not in data:
            errors.append("Missing device field")
        return errors

    def format_data(self, raw: dict) -> dict:
        # Already in device format
        if "device" in raw:
            return {
                "device": raw["device"],
                "readings": raw.get("readings", []),
                "alerts": raw.get("alerts", []),
            }
        # Flat single_metric from resolver — adapt to device shape
        if "value" in raw or "timeSeries" in raw:
            label = raw.get("label", "Sensor")
            value = raw.get("value", 0)
            units = raw.get("units", "")
            return {
                "device": {"id": "auto", "name": label, "status": "online"},
                "readings": [{"sensor": label, "value": value, "unit": units}],
                "alerts": [],
            }
        return raw
