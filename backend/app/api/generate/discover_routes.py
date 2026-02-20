from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.schemas.generate.reports import DiscoverPayload
from backend.app.services.generate.discovery_service import discover_reports as discover_reports_service


def build_discover_router(
    *,
    template_dir_fn,
    db_path_fn,
    load_contract_fn,
    clean_key_values_fn,
    discover_pdf_fn,
    discover_excel_fn,
    build_field_catalog_fn,
    build_batch_metrics_fn,
    load_manifest_fn,
    manifest_endpoint_fn_pdf,
    manifest_endpoint_fn_excel,
    logger,
) -> APIRouter:
    router = APIRouter()

    def _discover(kind: str, payload: DiscoverPayload):
        discover_fn = discover_pdf_fn if kind == "pdf" else discover_excel_fn
        manifest_endpoint_fn = manifest_endpoint_fn_pdf if kind == "pdf" else manifest_endpoint_fn_excel
        return discover_reports_service(
            payload,
            kind=kind,
            template_dir_fn=lambda tpl: template_dir_fn(tpl, kind=kind),
            db_path_fn=db_path_fn,
            load_contract_fn=load_contract_fn,
            clean_key_values_fn=clean_key_values_fn,
            discover_fn=discover_fn,
            build_field_catalog_fn=build_field_catalog_fn,
            build_batch_metrics_fn=build_batch_metrics_fn,
            load_manifest_fn=lambda tdir: load_manifest_fn(tdir),
            manifest_endpoint_fn=lambda tpl: manifest_endpoint_fn(tpl, kind=kind),
            logger=logger,
        )

    @router.post("/reports/discover")
    def discover_reports(payload: DiscoverPayload, _request: Request):
        return _discover("pdf", payload)

    @router.post("/excel/reports/discover")
    def discover_reports_excel(payload: DiscoverPayload, _request: Request):
        return _discover("excel", payload)

    return router
