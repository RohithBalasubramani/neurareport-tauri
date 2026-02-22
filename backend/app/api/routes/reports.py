"""Reports API Routes.

This module contains endpoints for report generation and management:
- Report generation (sync and async)
- Report run history
- Report discovery
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.services.security import require_api_key
from backend.app.schemas.generate.reports import RunPayload, DiscoverPayload
from backend.legacy.services.report_service import (
    queue_report_job,
    run_report as run_report_service,
    list_report_runs as list_report_runs_service,
    get_report_run as get_report_run_service,
)

router = APIRouter(dependencies=[Depends(require_api_key)])


def _correlation(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


# =============================================================================
# Report Generation
# =============================================================================

@router.post("/run")
def run_report(payload: RunPayload, request: Request):
    """Run a report synchronously. Auto-detects kind from template record."""
    import backend.app.services.state_access as state_access

    rec = state_access.get_template_record(payload.template_id)
    if not rec:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "template_not_found", "message": f"Template '{payload.template_id}' not found."},
        )
    kind = str(rec.get("kind") or "pdf").strip().lower() or "pdf"
    # Validate connection_id exists
    if payload.connection_id:
        conn = state_access.get_connection_record(payload.connection_id)
        if not conn:
            raise HTTPException(
                status_code=404,
                detail={"status": "error", "code": "connection_not_found", "message": f"Connection '{payload.connection_id}' not found."},
            )
    try:
        return run_report_service(payload, request, kind=kind)
    except HTTPException:
        raise
    except Exception as exc:
        import logging
        logging.getLogger("neura.api").exception("report_generation_failed", extra={"template_id": payload.template_id, "kind": kind})
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "code": "report_generation_failed", "message": f"Report generation failed for kind={kind}: {type(exc).__name__}"},
        )


@router.post("/jobs/run-report")
async def enqueue_report_job(payload: RunPayload | list[RunPayload], request: Request):
    """Queue a report job for async generation.

    Auto-detects the template kind (pdf/excel) from the template record.
    """
    import backend.app.services.state_access as state_access

    payloads = payload if isinstance(payload, list) else [payload]
    kinds = set()
    for item in payloads:
        rec = state_access.get_template_record(item.template_id) or {}
        kinds.add(str(rec.get("kind") or "pdf").strip().lower() or "pdf")
    if len(kinds) > 1:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "code": "mixed_template_kinds",
                "message": "All runs in a batch must share the same template kind.",
            },
        )
    kind = next(iter(kinds)) if kinds else "pdf"
    return await queue_report_job(payload, request, kind=kind)


# =============================================================================
# Report Discovery
# =============================================================================

@router.post("/discover")
def discover_reports(payload: DiscoverPayload, request: Request):
    """Discover available batches for report generation."""
    from backend.app.services.generate.discovery_service import discover_reports as discover_reports_service
    from backend.legacy.utils.template_utils import template_dir
    from backend.legacy.utils.connection_utils import db_path_from_payload_or_default
    from backend.app.services.contract.ContractBuilderV2 import load_contract_v2
    from backend.legacy.utils.schedule_utils import clean_key_values
    from backend.app.services.reports.discovery import discover_batches_and_counts
    from backend.app.services.reports.discovery_metrics import build_batch_field_catalog_and_stats, build_batch_metrics
    from backend.app.services.utils.artifacts import load_manifest
    from backend.legacy.utils.template_utils import manifest_endpoint
    import logging

    logger = logging.getLogger("neura.api")
    return discover_reports_service(
        payload,
        kind="pdf",
        template_dir_fn=lambda tpl: template_dir(tpl, kind="pdf"),
        db_path_fn=db_path_from_payload_or_default,
        load_contract_fn=load_contract_v2,
        clean_key_values_fn=clean_key_values,
        discover_fn=discover_batches_and_counts,
        build_field_catalog_fn=build_batch_field_catalog_and_stats,
        build_batch_metrics_fn=build_batch_metrics,
        load_manifest_fn=load_manifest,
        manifest_endpoint_fn=lambda tpl: manifest_endpoint(tpl, kind="pdf"),
        logger=logger,
    )


# =============================================================================
# Report Run History
# =============================================================================

@router.get("/runs")
def list_report_runs_route(
    request: Request,
    template_id: Optional[str] = None,
    connection_id: Optional[str] = None,
    schedule_id: Optional[str] = None,
    limit: int = 50,
):
    """List report generation runs with optional filtering."""
    runs = list_report_runs_service(
        template_id=template_id,
        connection_id=connection_id,
        schedule_id=schedule_id,
        limit=limit,
    )
    return {"runs": runs, "correlation_id": _correlation(request)}


@router.get("/runs/{run_id}")
def get_report_run_route(run_id: str, request: Request):
    """Get a specific report run by ID."""
    run = get_report_run_service(run_id)
    if not run:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "run_not_found", "message": "Run not found."}
        )
    return {"run": run, "correlation_id": _correlation(request)}
