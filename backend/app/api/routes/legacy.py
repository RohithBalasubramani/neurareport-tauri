"""Legacy/compatibility routes to expose unused modules for runtime reachability."""
from __future__ import annotations

import asyncio
import contextlib
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from backend.app.services.security import require_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/legacy", tags=["legacy"], dependencies=[Depends(require_api_key)])


# -----------------------------------------------------------------------------
# Legacy legacy/* routers
# -----------------------------------------------------------------------------
from backend.legacy.routes import router as src_router

router.include_router(src_router, prefix="/src")


# -----------------------------------------------------------------------------
# Legacy generate feature routers
# -----------------------------------------------------------------------------
def _build_generate_router() -> APIRouter:
    from backend.app.api.generate.run_routes import build_run_router
    from backend.app.api.generate.discover_routes import build_discover_router
    from backend.app.api.generate.chart_suggest_routes import build_chart_suggest_router
    from backend.app.api.generate.saved_charts_routes import build_saved_charts_router

    from backend.app.services.prompts.llm_prompts_charts import (
        CHART_SUGGEST_PROMPT_VERSION,
        build_chart_suggestions_prompt,
    )
    from backend.app.services.reports.discovery import discover_batches_and_counts
    from backend.app.services.reports.discovery_excel import discover_batches_and_counts as discover_batches_and_counts_excel
    from backend.app.services.reports.discovery_metrics import (
        build_batch_field_catalog_and_stats,
        build_batch_metrics,
    )
    import backend.app.services.state_access as state_access
    from backend.app.services.templates.TemplateVerify import get_openai_client
    from backend.app.services.utils import call_chat_completion, get_correlation_id, strip_code_fences
    from backend.app.services.utils.artifacts import load_manifest
    from backend.app.services.contract.ContractBuilderV2 import load_contract_v2
    from backend.legacy.services.report_service import run_report, queue_report_job
    from backend.legacy.utils.connection_utils import db_path_from_payload_or_default
    from backend.legacy.utils.schedule_utils import clean_key_values
    from backend.legacy.utils.template_utils import manifest_endpoint, normalize_template_id, template_dir
    import logging
    import os

    logger = logging.getLogger("neura.legacy")

    run_router = build_run_router(
        reports_run_fn=run_report,
        enqueue_job_fn=queue_report_job,
    )

    discover_router = build_discover_router(
        template_dir_fn=template_dir,
        db_path_fn=db_path_from_payload_or_default,
        load_contract_fn=load_contract_v2,
        clean_key_values_fn=clean_key_values,
        discover_pdf_fn=discover_batches_and_counts,
        discover_excel_fn=discover_batches_and_counts_excel,
        build_field_catalog_fn=build_batch_field_catalog_and_stats,
        build_batch_metrics_fn=build_batch_metrics,
        load_manifest_fn=load_manifest,
        manifest_endpoint_fn_pdf=manifest_endpoint,
        manifest_endpoint_fn_excel=manifest_endpoint,
        logger=logger,
    )

    chart_suggest_router = build_chart_suggest_router(
        template_dir_fn=template_dir,
        db_path_fn=db_path_from_payload_or_default,
        load_contract_fn=load_contract_v2,
        clean_key_values_fn=clean_key_values,
        discover_pdf_fn=discover_batches_and_counts,
        discover_excel_fn=discover_batches_and_counts_excel,
        build_field_catalog_fn=build_batch_field_catalog_and_stats,
        build_metrics_fn=build_batch_metrics,
        build_prompt_fn=build_chart_suggestions_prompt,
        call_chat_completion_fn=lambda **kwargs: call_chat_completion(
            get_openai_client(), **kwargs, description=CHART_SUGGEST_PROMPT_VERSION
        ),
        model=os.getenv("CLAUDE_CODE_MODEL", "sonnet"),
        strip_code_fences_fn=strip_code_fences,
        get_correlation_id_fn=get_correlation_id,
        logger=logger,
    )

    def _ensure_template_exists(template_id: str) -> tuple[str, dict]:
        normalized = normalize_template_id(template_id)
        record = state_access.get_template_record(normalized)
        if not record:
            raise HTTPException(status_code=404, detail="template_not_found")
        return normalized, record

    saved_charts_router = build_saved_charts_router(
        ensure_template_exists=_ensure_template_exists,
        normalize_template_id=normalize_template_id,
    )

    generate_router = APIRouter()
    generate_router.include_router(run_router)
    generate_router.include_router(discover_router)
    generate_router.include_router(chart_suggest_router)
    generate_router.include_router(saved_charts_router)
    return generate_router


router.include_router(_build_generate_router(), prefix="/generate")


# -----------------------------------------------------------------------------
# Legacy pipeline + orchestration reachability
# -----------------------------------------------------------------------------
@router.get("/pipelines/report/steps")
async def report_pipeline_steps():
    """Expose report pipeline definition."""
    # ARCH-EXC-001: legacy compatibility route requires direct engine access.
    from backend.engine.pipelines.report_pipeline import create_report_pipeline

    pipeline = create_report_pipeline()
    return {
        "pipeline": pipeline.name,
        "steps": [{"name": s.name, "label": s.label} for s in pipeline.steps],
    }


@router.post("/orchestration/test-run")
async def orchestration_test_run():
    """Run a short orchestration job for validation."""
    from backend.engine.orchestration.executor import get_executor
    from backend.engine.domain.jobs import Job, JobType, JobStep

    executor = get_executor()
    job = Job.create(
        job_type=JobType.REPORT_GENERATION,
        steps=[JobStep(name="noop", label="No-op step")],
    )

    def _runner(job_obj: Job, _executor) -> Dict[str, Any]:
        job_obj.step_running("noop")
        job_obj.step_succeeded("noop", progress=100.0)
        return {"status": "ok"}

    runners = getattr(executor, "_runners", {})
    if JobType.REPORT_GENERATION not in runners:
        executor.register_runner(JobType.REPORT_GENERATION, _runner)

    await executor.submit(job)
    for _ in range(40):
        if job.status.is_terminal:
            break
        await asyncio.sleep(0.05)

    return {"job": job.to_dict()}


# -----------------------------------------------------------------------------
# Extraction helpers (pdf/excel)
# -----------------------------------------------------------------------------
class PdfExtractRequest(BaseModel):
    method: str = "auto"
    max_pages: int = 10


class ExcelExtractRequest(BaseModel):
    max_rows: int = 5000


@router.post("/extraction/pdf")
async def legacy_extract_pdf(
    request: PdfExtractRequest,
    file: UploadFile = File(...),
):
    """Extract PDF tables using legacy extractors."""
    from backend.app.services.extraction.pdf_extractors import ExtractionConfig, extract_pdf_tables

    suffix = Path(file.filename or "document.pdf").suffix or ".pdf"
    tmp = tempfile.NamedTemporaryFile(prefix="nr-legacy-pdf-", suffix=suffix, delete=False)
    tmp_path = Path(tmp.name)
    try:
        with tmp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
        config = ExtractionConfig(max_pages=request.max_pages)
        result = extract_pdf_tables(tmp_path, method=request.method, config=config)
        return result.to_dict()
    finally:
        await file.close()
        with contextlib.suppress(FileNotFoundError):
            tmp_path.unlink(missing_ok=True)


@router.post("/extraction/excel")
async def legacy_extract_excel(
    request: ExcelExtractRequest,
    file: UploadFile = File(...),
):
    """Extract Excel data using legacy extractors."""
    from backend.app.services.extraction.excel_extractors import extract_excel_data

    suffix = Path(file.filename or "document.xlsx").suffix or ".xlsx"
    tmp = tempfile.NamedTemporaryFile(prefix="nr-legacy-excel-", suffix=suffix, delete=False)
    tmp_path = Path(tmp.name)
    try:
        with tmp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
        result = extract_excel_data(tmp_path, max_rows=request.max_rows)
        return result.to_dict()
    finally:
        await file.close()
        with contextlib.suppress(FileNotFoundError):
            tmp_path.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# QuickChart integration
# -----------------------------------------------------------------------------
class QuickChartRequest(BaseModel):
    chart_type: str
    labels: List[str]
    data: Any
    title: Optional[str] = None


@router.post("/charts/quickchart/url")
async def quickchart_url(request: QuickChartRequest):
    """Generate a QuickChart URL without downloading the image."""
    from backend.app.services.charts.quickchart import generate_chart_url

    try:
        url = generate_chart_url(
            request.chart_type,
            request.labels,
            request.data,
            title=request.title,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid export request")
    return {"url": url}


# -----------------------------------------------------------------------------
# LLM utilities (agents, vision, document extractor)
# -----------------------------------------------------------------------------
class DocumentExtractRequest(BaseModel):
    use_vlm: bool = False
    max_pages: int = 10


@router.get("/llm/agents")
async def list_llm_agents():
    """List configured LLM agents and tasks."""
    from backend.app.services.llm.agents import create_document_processing_crew

    crew = create_document_processing_crew(verbose=False)
    agents = [
        {"role": agent.role, "goal": agent.config.goal}
        for agent in crew.agents.values()
    ]
    tasks = [
        {"description": task.description, "agent_role": task.agent_role}
        for task in crew.tasks
    ]
    return {"agents": agents, "tasks": tasks}


@router.get("/llm/vision/model")
async def get_vision_model_info():
    """Return the configured vision model (if available)."""
    try:
        from backend.app.services.llm.vision import VisionLanguageModel
        vlm = VisionLanguageModel()
        return {"model": vlm.model}
    except Exception as exc:
        logger.warning("Vision model not available: %s", exc)
        raise HTTPException(status_code=503, detail="Vision model not available")


@router.post("/llm/document-extract")
async def legacy_document_extract(
    request: DocumentExtractRequest,
    file: UploadFile = File(...),
):
    """Extract document content using the enhanced LLM document extractor."""
    from backend.app.services.llm.document_extractor import EnhancedDocumentExtractor

    suffix = Path(file.filename or "document").suffix or ".pdf"
    tmp = tempfile.NamedTemporaryFile(prefix="nr-legacy-doc-", suffix=suffix, delete=False)
    tmp_path = Path(tmp.name)
    try:
        with tmp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)

        extractor = EnhancedDocumentExtractor(
            use_vlm=request.use_vlm,
            max_pages=request.max_pages,
        )
        result = extractor.extract(tmp_path)
        text_preview = (result.text or "")[:2000]
        return {
            "text_preview": text_preview,
            "table_count": len(result.tables),
            "metadata": result.metadata,
            "warnings": result.warnings,
        }
    finally:
        await file.close()
        with contextlib.suppress(FileNotFoundError):
            tmp_path.unlink(missing_ok=True)
