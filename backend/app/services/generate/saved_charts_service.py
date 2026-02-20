from __future__ import annotations

from typing import Callable

from fastapi import HTTPException

from backend.app.repositories.state import state_store
from backend.app.schemas.generate.charts import SavedChartCreatePayload, SavedChartSpec, SavedChartUpdatePayload


def _serialize_saved_chart(record: dict) -> SavedChartSpec:
    spec_payload = record.get("spec") or {}
    return SavedChartSpec(
        id=record["id"],
        template_id=record["template_id"],
        name=record["name"],
        spec=spec_payload,
        created_at=record.get("created_at", ""),
        updated_at=record.get("updated_at", ""),
    )


EnsureTemplateExistsFn = Callable[[str], tuple[str, dict]]
NormalizeTemplateIdFn = Callable[[str], str]


def list_saved_charts(template_id: str, ensure_template_exists: EnsureTemplateExistsFn) -> dict:
    normalized, _ = ensure_template_exists(template_id)
    records = state_store.list_saved_charts(normalized)
    charts = [_serialize_saved_chart(rec) for rec in records]
    return {"charts": charts}


def create_saved_chart(
    template_id: str,
    payload: SavedChartCreatePayload,
    ensure_template_exists: EnsureTemplateExistsFn,
    normalize_template_id: NormalizeTemplateIdFn,
):
    path_template, _ = ensure_template_exists(template_id)
    body_template = normalize_template_id(payload.template_id)
    if body_template != path_template:
        raise HTTPException(status_code=400, detail={"code": "template_mismatch", "message": "template_id in path and payload must match"})
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail={"code": "name_required", "message": "Saved chart name is required."})
    record = state_store.create_saved_chart(path_template, name, payload.spec.model_dump())
    return _serialize_saved_chart(record)


def update_saved_chart(
    template_id: str,
    chart_id: str,
    payload: SavedChartUpdatePayload,
    ensure_template_exists: EnsureTemplateExistsFn,
):
    path_template, _ = ensure_template_exists(template_id)
    existing = state_store.get_saved_chart(chart_id)
    if not existing or existing.get("template_id") != path_template:
        raise HTTPException(status_code=404, detail={"code": "chart_not_found", "message": "Saved chart not found."})
    updates: dict[str, object] = {}
    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail={"code": "name_required", "message": "Saved chart name cannot be empty."})
        updates["name"] = name
    if payload.spec is not None:
        updates["spec"] = payload.spec.model_dump()
    if not updates:
        return _serialize_saved_chart(existing)
    record = state_store.update_saved_chart(chart_id, name=updates.get("name"), spec=updates.get("spec"))
    if not record:
        raise HTTPException(status_code=404, detail={"code": "chart_not_found", "message": "Saved chart not found."})
    return _serialize_saved_chart(record)


def delete_saved_chart(template_id: str, chart_id: str, ensure_template_exists: EnsureTemplateExistsFn):
    path_template, _ = ensure_template_exists(template_id)
    existing = state_store.get_saved_chart(chart_id)
    if not existing or existing.get("template_id") != path_template:
        raise HTTPException(status_code=404, detail={"code": "chart_not_found", "message": "Saved chart not found."})
    removed = state_store.delete_saved_chart(chart_id)
    if not removed:
        raise HTTPException(status_code=404, detail={"code": "chart_not_found", "message": "Saved chart not found."})
    return {"status": "ok"}
