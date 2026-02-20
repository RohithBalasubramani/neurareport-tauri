from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from backend.app.repositories.state import state_store
from .starter_catalog import STARTER_TEMPLATES


TemplateCatalogItem = Dict[str, Any]


def _normalize_str_list(values: Optional[Sequence[str]]) -> list[str]:
    if not values:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in values:
        text = str(raw or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def build_unified_template_catalog() -> List[TemplateCatalogItem]:
    """
    Combine company templates from the persistent state store with the static
    starter catalog into a unified, normalised list.

    Each entry has:
        - id, name, kind
        - domain (optional)
        - tags
        - useCases
        - primaryMetrics
        - source: \"company\" | \"starter\"
    """
    catalog: list[TemplateCatalogItem] = []
    seen_ids: set[str] = set()

    # Company templates from state.json, via the sanitised view.
    for rec in state_store.list_templates():
        template_id = str(rec.get("id") or "").strip()
        if not template_id:
            continue
        if template_id in seen_ids:
            continue
        name = (rec.get("name") or "").strip() or f"Template {template_id[:8]}"
        kind = (rec.get("kind") or "pdf").strip().lower() or "pdf"

        item: TemplateCatalogItem = {
            "id": template_id,
            "name": name,
            "kind": kind,
            "domain": rec.get("domain") or None,
            "tags": _normalize_str_list(rec.get("tags") or []),
            "useCases": _normalize_str_list(rec.get("useCases") or []),
            "primaryMetrics": _normalize_str_list(rec.get("primaryMetrics") or []),
            "description": (rec.get("description") or "").strip() or None,
            "source": "company",
        }
        catalog.append(item)
        seen_ids.add(template_id)

    # Static starter templates.
    for starter in STARTER_TEMPLATES:
        template_id = str(starter.get("id") or "").strip()
        if not template_id or template_id in seen_ids:
            continue
        name = (starter.get("name") or "").strip() or template_id
        kind = (starter.get("kind") or "pdf").strip().lower() or "pdf"

        item: TemplateCatalogItem = {
            "id": template_id,
            "name": name,
            "kind": kind,
            "domain": starter.get("domain") or None,
            "tags": _normalize_str_list(starter.get("tags") or []),
            "useCases": _normalize_str_list(starter.get("useCases") or []),
            "primaryMetrics": _normalize_str_list(starter.get("primaryMetrics") or []),
            "description": (starter.get("description") or "").strip() or None,
            "source": "starter",
        }
        catalog.append(item)
        seen_ids.add(template_id)

    return catalog
