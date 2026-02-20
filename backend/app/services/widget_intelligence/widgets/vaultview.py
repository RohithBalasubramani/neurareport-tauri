"""Vault view widget plugin — secure data vault and document archive."""

from backend.app.services.widget_intelligence.widgets.base import WidgetPlugin, WidgetMeta


class VaultViewWidget(WidgetPlugin):
    meta = WidgetMeta(
        scenario="vaultview",
        variants=["vaultview"],
        description="Secure data vault showing stored documents, archived reports, compliance records, and audit logs",
        good_for=["vault", "archive", "documents", "compliance", "audit log", "records", "stored data", "reports"],
        sizes=["normal", "expanded"],
        height_units=2,
        rag_strategy="none",
        required_fields=["items"],
        optional_fields=["categories", "searchQuery", "accessLog"],
        aggregation="none",
    )

    def validate_data(self, data: dict) -> list[str]:
        errors = []
        if not isinstance(data.get("items"), list):
            errors.append("Missing or invalid items field")
        return errors

    def format_data(self, raw: dict) -> dict:
        return {
            "items": raw.get("items", []),
            "categories": raw.get("categories", []),
        }
