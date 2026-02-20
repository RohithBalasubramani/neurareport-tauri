from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.schemas.generate.charts import ChartSuggestPayload
from backend.app.services.generate.chart_suggestions_service import suggest_charts as suggest_charts_service


def build_chart_suggest_router(
    *,
    template_dir_fn,
    db_path_fn,
    load_contract_fn,
    clean_key_values_fn,
    discover_pdf_fn,
    discover_excel_fn,
    build_field_catalog_fn,
    build_metrics_fn,
    build_prompt_fn,
    call_chat_completion_fn,
    model,
    strip_code_fences_fn,
    get_correlation_id_fn,
    logger,
) -> APIRouter:
    router = APIRouter()

    def _route(template_id: str, payload: ChartSuggestPayload, request: Request, kind: str):
        correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id_fn()
        discover_fn = discover_pdf_fn if kind == "pdf" else discover_excel_fn
        return suggest_charts_service(
            template_id,
            payload,
            kind=kind,
            correlation_id=correlation_id,
            template_dir_fn=lambda tpl: template_dir_fn(tpl, kind=kind),
            db_path_fn=db_path_fn,
            load_contract_fn=load_contract_fn,
            clean_key_values_fn=clean_key_values_fn,
            discover_fn=discover_fn,
            build_field_catalog_fn=build_field_catalog_fn,
            build_metrics_fn=build_metrics_fn,
            build_prompt_fn=build_prompt_fn,
            call_chat_completion_fn=call_chat_completion_fn,
            model=model,
            strip_code_fences_fn=strip_code_fences_fn,
            logger=logger,
        )

    @router.post("/templates/{template_id}/charts/suggest")
    def suggest_charts(template_id: str, payload: ChartSuggestPayload, request: Request):
        return _route(template_id, payload, request, kind="pdf")

    @router.post("/excel/{template_id}/charts/suggest")
    def suggest_charts_excel(template_id: str, payload: ChartSuggestPayload, request: Request):
        return _route(template_id, payload, request, kind="excel")

    return router
