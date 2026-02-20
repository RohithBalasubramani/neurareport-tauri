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
    """Run a PDF report synchronously."""
    return run_report_service(payload, request, kind="pdf")


@router.post("/jobs/run-report")
async def enqueue_report_job(payload: RunPayload | list[RunPayload], request: Request):
    """Queue a PDF report job for async generation."""
    return await queue_report_job(payload, request, kind="pdf")


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
