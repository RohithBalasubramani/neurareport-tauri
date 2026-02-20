from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.generate.charts import SavedChartCreatePayload, SavedChartUpdatePayload
from backend.app.services.generate.saved_charts_service import (
    create_saved_chart as create_saved_chart_service,
    delete_saved_chart as delete_saved_chart_service,
    list_saved_charts as list_saved_charts_service,
    update_saved_chart as update_saved_chart_service,
)


def build_saved_charts_router(ensure_template_exists, normalize_template_id) -> APIRouter:
    router = APIRouter()

    @router.get("/templates/{template_id}/charts/saved")
    def list_saved_charts(template_id: str):
        return list_saved_charts_service(template_id, ensure_template_exists)

    @router.post("/templates/{template_id}/charts/saved")
    def create_saved_chart(template_id: str, payload: SavedChartCreatePayload):
        return create_saved_chart_service(
            template_id,
            payload,
            ensure_template_exists=ensure_template_exists,
            normalize_template_id=normalize_template_id,
        )

    @router.put("/templates/{template_id}/charts/saved/{chart_id}")
    def update_saved_chart(template_id: str, chart_id: str, payload: SavedChartUpdatePayload):
        return update_saved_chart_service(template_id, chart_id, payload, ensure_template_exists)

    @router.delete("/templates/{template_id}/charts/saved/{chart_id}")
    def delete_saved_chart(template_id: str, chart_id: str):
        return delete_saved_chart_service(template_id, chart_id, ensure_template_exists)

    @router.get("/excel/{template_id}/charts/saved")
    def list_saved_charts_excel(template_id: str):
        return list_saved_charts_service(template_id, ensure_template_exists)

    @router.post("/excel/{template_id}/charts/saved")
    def create_saved_chart_excel(template_id: str, payload: SavedChartCreatePayload):
        return create_saved_chart_service(
            template_id,
            payload,
            ensure_template_exists=ensure_template_exists,
            normalize_template_id=normalize_template_id,
        )

    @router.put("/excel/{template_id}/charts/saved/{chart_id}")
    def update_saved_chart_excel(template_id: str, chart_id: str, payload: SavedChartUpdatePayload):
        return update_saved_chart_service(template_id, chart_id, payload, ensure_template_exists)

    @router.delete("/excel/{template_id}/charts/saved/{chart_id}")
    def delete_saved_chart_excel(template_id: str, chart_id: str):
        return delete_saved_chart_service(template_id, chart_id, ensure_template_exists)

    return router
