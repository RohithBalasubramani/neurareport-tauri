"""Agents view widget plugin — AI agent status and activity monitor."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class AgentsViewWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="agentsview",
        variants=["agentsview"],
        description="AI agent activity monitor showing active agents, their tasks, status, and recent actions",
        good_for=["agents", "AI agents", "automation", "bot status", "agent tasks", "autonomous", "pipeline agents"],
        sizes=["normal", "expanded"],
        height_units=2,
        rag_strategy="none",
        required_fields=["agents"],
        optional_fields=["tasks", "metrics", "logs"],
        aggregation="none",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if not isinstance(data.get("agents"), list):
            errors.append("Missing or invalid agents field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return {
            "agents": raw.get("agents", []),
            "tasks": raw.get("tasks", []),
        }

    def get_demo_data(self) -> dict:
        return {
            "agents": [
                {"id": "agent-1", "name": "Data Collector", "status": "active", "lastAction": "Fetched 120 records"},
                {"id": "agent-2", "name": "Anomaly Detector", "status": "idle", "lastAction": "No anomalies found"},
            ],
            "tasks": [],
        }
