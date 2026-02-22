"""Excel Template API Routes.

This module contains endpoints for Excel template operations:
- Excel template verification
- Excel mapping operations
- Excel report generation
- Excel artifacts
"""
from __future__ import annotations

import contextlib
import logging
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile

from backend.app.services.security import require_api_key
from backend.app.schemas.generate.charts import (
    ChartSuggestPayload,
    SavedChartCreatePayload,
    SavedChartUpdatePayload,
)
from backend.app.schemas.generate.reports import RunPayload, DiscoverPayload
from backend.app.services.generate.chart_suggestions_service import suggest_charts as suggest_charts_service
from backend.app.services.generate.saved_charts_service import (
    create_saved_chart as create_saved_chart_service,
    delete_saved_chart as delete_saved_chart_service,
    list_saved_charts as list_saved_charts_service,
    update_saved_chart as update_saved_chart_service,
)
from backend.app.services.background_tasks import (
    enqueue_background_job,
    iter_ndjson_events_async,
    run_event_stream_async,
)
from backend.app.services.contract.ContractBuilderV2 import load_contract_v2
from backend.app.services.prompts.llm_prompts_charts import (
    CHART_SUGGEST_PROMPT_VERSION,
    build_chart_suggestions_prompt,
)
from backend.app.services.reports.discovery_excel import discover_batches_and_counts as discover_batches_and_counts_excel
from backend.app.services.reports.discovery_metrics import (
    build_batch_field_catalog_and_stats,
    build_batch_metrics,
)
import backend.app.services.state_access as state_access
from backend.app.services.templates.TemplateVerify import get_openai_client
from backend.app.services.utils import call_chat_completion, get_correlation_id, strip_code_fences

from backend.legacy.services.template_service import verify_excel, generator_assets
from backend.legacy.services.mapping.approve import run_mapping_approve
from backend.legacy.services.mapping.corrections import run_corrections_preview
from backend.legacy.services.mapping.key_options import mapping_key_options as mapping_key_options_service
from backend.legacy.services.mapping.preview import run_mapping_preview
from backend.legacy.services.file_service import artifact_head_response, artifact_manifest_response
from backend.legacy.services.report_service import queue_report_job, run_report as run_report_service
from backend.legacy.schemas.template_schema import CorrectionsPreviewPayload, GeneratorAssetsPayload, MappingPayload
from backend.legacy.utils.connection_utils import db_path_from_payload_or_default
from backend.legacy.utils.schedule_utils import clean_key_values
from backend.legacy.utils.template_utils import normalize_template_id, template_dir

logger = logging.getLogger("neura.api.excel")

router = APIRouter(dependencies=[Depends(require_api_key)])

MAX_UPLOAD_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB


def _correlation(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


def _request_with_correlation(correlation_id: str | None) -> SimpleNamespace:
    return SimpleNamespace(state=SimpleNamespace(correlation_id=correlation_id))


def _wrap(payload: dict, correlation_id: str | None) -> dict:
    payload = dict(payload)
    if correlation_id is not None:
        payload["correlation_id"] = correlation_id
    return payload


def _ensure_template_exists(template_id: str) -> tuple[str, dict]:
    normalized = normalize_template_id(template_id)
    record = state_access.get_template_record(normalized)
    if not record:
        raise HTTPException(status_code=404, detail="template_not_found")
    return normalized, record


async def _persist_upload(file: UploadFile, suffix: str) -> tuple[Path, str]:
    filename = Path(file.filename or f"upload{suffix}").name
    tmp = tempfile.NamedTemporaryFile(prefix="nr-upload-", suffix=suffix, delete=False)
    tmp_path = Path(tmp.name)
    try:
        total_bytes = 0
        with tmp:
            file.file.seek(0)
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds maximum upload size of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB",
                    )
                tmp.write(chunk)
    except HTTPException:
        # Clean up temp file on size rejection
        with contextlib.suppress(FileNotFoundError):
            tmp_path.unlink(missing_ok=True)
        raise
    except Exception:
        # Clean up temp file on any failure
        with contextlib.suppress(FileNotFoundError):
            tmp_path.unlink(missing_ok=True)
        raise
    finally:
        with contextlib.suppress(Exception):
            await file.close()
    return tmp_path, filename


# =============================================================================
# Excel Template Verification
# =============================================================================

@router.post("/verify")
async def verify_excel_route(
    request: Request,
    file: UploadFile = File(...),
    connection_id: str | None = Form(None),
    background: bool = Query(False),
):
    """Verify and process an Excel template."""
    if not background:
        return verify_excel(file=file, request=request, connection_id=connection_id)

    upload_path, filename = await _persist_upload(file, suffix=".xlsx")
    correlation_id = _correlation(request)
    template_name = Path(filename).stem or filename

    async def runner(job_id: str) -> None:
        upload = UploadFile(filename=filename, file=upload_path.open("rb"))
        try:
            response = verify_excel(
                file=upload,
                request=_request_with_correlation(correlation_id),
                connection_id=connection_id,
            )
            await run_event_stream_async(job_id, iter_ndjson_events_async(response.body_iterator))
        finally:
            with contextlib.suppress(Exception):
                await upload.close()
            with contextlib.suppress(FileNotFoundError):
                upload_path.unlink(missing_ok=True)

    job = await enqueue_background_job(
        job_type="verify_excel",
        connection_id=connection_id,
        template_name=template_name,
        template_kind="excel",
        meta={"filename": filename, "background": True},
        runner=runner,
    )
    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}


# =============================================================================
# Excel Mapping Operations
# =============================================================================

@router.post("/{template_id}/mapping/preview")
async def mapping_preview_excel(template_id: str, connection_id: str, request: Request, force_refresh: bool = False):
    """Preview mapping for an Excel template."""
    return await run_mapping_preview(template_id, connection_id, request, force_refresh, kind="excel")


@router.post("/{template_id}/mapping/approve")
async def mapping_approve_excel(template_id: str, payload: MappingPayload, request: Request):
    """Approve mapping for an Excel template."""
    return await run_mapping_approve(template_id, payload, request, kind="excel")


@router.post("/{template_id}/mapping/corrections-preview")
def mapping_corrections_preview_excel(template_id: str, payload: CorrectionsPreviewPayload, request: Request):
    """Preview corrections for Excel template mapping."""
    return run_corrections_preview(template_id, payload, request, kind="excel")


# =============================================================================
# Excel Generator Assets
# =============================================================================

@router.post("/{template_id}/generator-assets/v1")
def generator_assets_excel_route(template_id: str, payload: GeneratorAssetsPayload, request: Request):
    """Generate assets for an Excel template."""
    return generator_assets(template_id, payload, request, kind="excel")


# =============================================================================
# Excel Key Options
# =============================================================================

@router.get("/{template_id}/keys/options")
def mapping_key_options_excel(
    template_id: str,
    request: Request,
    connection_id: str | None = None,
    tokens: str | None = None,
    limit: int = Query(500, ge=1, le=5000),
    start_date: str | None = None,
    end_date: str | None = None,
    debug: bool = False,
):
    """Get available key options for Excel template filtering."""
    return mapping_key_options_service(
        template_id=template_id,
        request=request,
        connection_id=connection_id,
        tokens=tokens,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        kind="excel",
        debug=debug,
    )


# =============================================================================
# Excel Artifacts
# =============================================================================

@router.get("/{template_id}/artifacts/manifest")
def get_artifact_manifest_excel(template_id: str, request: Request):
    """Get the artifact manifest for an Excel template."""
    data = artifact_manifest_response(template_id, kind="excel")
    return _wrap(data, _correlation(request))


@router.get("/{template_id}/artifacts/head")
def get_artifact_head_excel(template_id: str, request: Request, name: str):
    """Get the head (preview) of a specific artifact."""
    data = artifact_head_response(template_id, name, kind="excel")
    return _wrap(data, _correlation(request))


# =============================================================================
# Charts
# =============================================================================

@router.post("/{template_id}/charts/suggest")
def suggest_charts_excel_route(template_id: str, payload: ChartSuggestPayload, request: Request):
    """Get chart suggestions for an Excel template."""
    correlation_id = _correlation(request) or get_correlation_id()
    logger = logging.getLogger("neura.api")
    return suggest_charts_service(
        template_id,
        payload,
        kind="excel",
        correlation_id=correlation_id,
        template_dir_fn=lambda tpl: template_dir(tpl, kind="excel"),
        db_path_fn=db_path_from_payload_or_default,
        load_contract_fn=load_contract_v2,
        clean_key_values_fn=clean_key_values,
        discover_fn=discover_batches_and_counts_excel,
        build_field_catalog_fn=build_batch_field_catalog_and_stats,
        build_metrics_fn=build_batch_metrics,
        build_prompt_fn=build_chart_suggestions_prompt,
        call_chat_completion_fn=lambda **kwargs: call_chat_completion(
            get_openai_client(), **kwargs, description=CHART_SUGGEST_PROMPT_VERSION
        ),
        model=os.getenv("CLAUDE_CODE_MODEL", "sonnet"),
        strip_code_fences_fn=strip_code_fences,
        logger=logger,
    )


@router.get("/{template_id}/charts/saved")
def list_saved_charts_excel_route(template_id: str, request: Request):
    """List saved charts for an Excel template."""
    payload = list_saved_charts_service(template_id, _ensure_template_exists)
    return _wrap(payload, _correlation(request))


@router.post("/{template_id}/charts/saved")
def create_saved_chart_excel_route(
    template_id: str,
    payload: SavedChartCreatePayload,
    request: Request,
):
    """Create a saved chart for an Excel template."""
    chart = create_saved_chart_service(
        template_id,
        payload,
        ensure_template_exists=_ensure_template_exists,
        normalize_template_id=normalize_template_id,
    )
    chart_payload = chart.model_dump(mode="json") if hasattr(chart, "model_dump") else chart
    return _wrap(chart_payload, _correlation(request))


@router.put("/{template_id}/charts/saved/{chart_id}")
def update_saved_chart_excel_route(
    template_id: str,
    chart_id: str,
    payload: SavedChartUpdatePayload,
    request: Request,
):
    """Update a saved chart for an Excel template."""
    chart = update_saved_chart_service(template_id, chart_id, payload, _ensure_template_exists)
    chart_payload = chart.model_dump(mode="json") if hasattr(chart, "model_dump") else chart
    return _wrap(chart_payload, _correlation(request))


@router.delete("/{template_id}/charts/saved/{chart_id}")
def delete_saved_chart_excel_route(
    template_id: str,
    chart_id: str,
    request: Request,
):
    """Delete a saved chart for an Excel template."""
    payload = delete_saved_chart_service(template_id, chart_id, _ensure_template_exists)
    return _wrap(payload, _correlation(request))


# =============================================================================
# Excel Report Generation
# =============================================================================

@router.post("/reports/run")
def run_report_excel(payload: RunPayload, request: Request):
    """Run an Excel report synchronously."""
    # C1: docx output is not supported
    if payload.docx:
        raise HTTPException(
            status_code=422,
            detail={
                "status": "error",
                "code": "unsupported_format",
                "message": "DOCX output is not supported. Use PDF or XLSX output instead.",
            },
        )
    # H1: validate connection_id exists
    if payload.connection_id:
        conn = state_access.get_connection_record(payload.connection_id)
        if not conn:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "code": "connection_not_found",
                    "message": f"Connection '{payload.connection_id}' not found.",
                },
            )
    # M4: validate date range
    if payload.start_date and payload.end_date and payload.start_date > payload.end_date:
        raise HTTPException(
            status_code=422,
            detail={
                "status": "error",
                "code": "invalid_date_range",
                "message": "start_date must be before or equal to end_date.",
            },
        )
    return run_report_service(payload, request, kind="excel")


@router.post("/jobs/run-report")
async def enqueue_report_job_excel(payload: RunPayload | list[RunPayload], request: Request):
    """Queue an Excel report job for async generation."""
    return await queue_report_job(payload, request, kind="excel")


# =============================================================================
# Excel Report Discovery
# =============================================================================

@router.post("/reports/discover")
def discover_reports_excel(payload: DiscoverPayload, request: Request):
    """Discover available batches for Excel report generation."""
    from backend.app.services.generate.discovery_service import discover_reports as discover_reports_service
    from backend.app.services.utils.artifacts import load_manifest
    from backend.legacy.utils.template_utils import manifest_endpoint

    logger = logging.getLogger("neura.api")
    return discover_reports_service(
        payload,
        kind="excel",
        template_dir_fn=lambda tpl: template_dir(tpl, kind="excel"),
        db_path_fn=db_path_from_payload_or_default,
        load_contract_fn=load_contract_v2,
        clean_key_values_fn=clean_key_values,
        discover_fn=discover_batches_and_counts_excel,
        build_field_catalog_fn=build_batch_field_catalog_and_stats,
        build_batch_metrics_fn=build_batch_metrics,
        load_manifest_fn=load_manifest,
        manifest_endpoint_fn=lambda tpl: manifest_endpoint(tpl, kind="excel"),
        logger=logger,
    )
