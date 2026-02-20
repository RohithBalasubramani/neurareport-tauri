# mypy: ignore-errors
"""
Enhanced Analysis API Routes - Comprehensive endpoints for AI-powered document analysis.

Provides endpoints for:
- Document upload and analysis
- Natural language Q&A
- Chart generation
- Data export
- Collaboration features
- Integrations
"""
from __future__ import annotations

import contextlib
import json
import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

from backend.app.services.auth import current_optional_user
from backend.app.services.config import get_settings
from backend.app.services.security import require_api_key
from backend.app.services.validation import validate_file_extension
from backend.app.schemas.analyze.enhanced_analysis import (
    AnalysisDepth,
    AnalysisPreferences,
    ChartType,
    ExportFormat,
    SummaryMode,
)
from backend.app.services.analyze.enhanced_analysis_orchestrator import (
    get_orchestrator,
)
from backend.app.services.analyze.integrations import DataSourceType
from backend.app.services.background_tasks import enqueue_background_job, run_event_stream_async

logger = logging.getLogger("neura.analyze.routes")

router = APIRouter(prefix="/analyze/v2", tags=["Enhanced Analysis"], dependencies=[Depends(require_api_key)])

ALLOWED_EXTENSIONS = [".pdf", ".xlsx", ".xls", ".xlsm"]
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/vnd.ms-excel.sheet.macroEnabled.12",
    "application/octet-stream",
}
MAX_FILENAME_LENGTH = 255
READ_CHUNK_BYTES = 1024 * 1024


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class AnalyzePreferencesRequest(BaseModel):
    """Request model for analysis preferences."""
    analysis_depth: str = "standard"
    focus_areas: List[str] = []
    output_format: str = "executive"
    language: str = "en"
    industry: Optional[str] = None
    enable_predictions: bool = True
    enable_recommendations: bool = True
    auto_chart_generation: bool = True
    max_charts: int = 10
    summary_mode: str = "executive"


class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str
    include_sources: bool = True
    max_context_chunks: int = 5


class ChartRequest(BaseModel):
    """Request model for generating charts."""
    query: str
    chart_type: Optional[str] = None
    include_trends: bool = True
    include_forecasts: bool = False


class ExportRequest(BaseModel):
    """Request model for exporting analysis."""
    format: str = "json"
    include_raw_data: bool = True
    include_charts: bool = True


class CompareRequest(BaseModel):
    """Request model for comparing documents."""
    analysis_id_1: str
    analysis_id_2: str


class CommentRequest(BaseModel):
    """Request model for adding comments."""
    content: str
    element_type: Optional[str] = None
    element_id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None


class ShareRequest(BaseModel):
    """Request model for creating share links."""
    access_level: str = "view"
    expires_hours: Optional[int] = None
    password_protected: bool = False
    allowed_emails: List[str] = []


class IntegrationRequest(BaseModel):
    name: str
    integration_type: str
    config: Dict[str, Any] = {}


class IntegrationMessageRequest(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None


class IntegrationItemRequest(BaseModel):
    data: Dict[str, Any] = {}


class DataSourceRequest(BaseModel):
    name: str
    source_type: str
    config: Dict[str, Any] = {}


class DataFetchRequest(BaseModel):
    query: Optional[str] = None


class TriggerRequest(BaseModel):
    name: str
    trigger_type: str
    config: Dict[str, Any] = {}
    action: str


class PipelineRequest(BaseModel):
    name: str
    steps: List[Dict[str, Any]] = []


class PipelineExecuteRequest(BaseModel):
    input_data: Dict[str, Any] = {}


class ScheduleRequest(BaseModel):
    name: str
    source_config: Dict[str, Any] = {}
    schedule: str
    analysis_config: Dict[str, Any] = {}
    notifications: List[str] = []


class WebhookRequest(BaseModel):
    url: str
    events: List[str] = []
    secret: Optional[str] = None


class WebhookSendRequest(BaseModel):
    event: str
    payload: Dict[str, Any] = {}


# =============================================================================
# DOCUMENT ANALYSIS ENDPOINTS
# =============================================================================

def _validate_upload(file: UploadFile) -> str:
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(status_code=400, detail="No file provided")
    if len(filename) > MAX_FILENAME_LENGTH:
        raise HTTPException(status_code=400, detail=f"Filename too long (max {MAX_FILENAME_LENGTH} characters)")
    is_valid, error = validate_file_extension(filename, ALLOWED_EXTENSIONS)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported content type '{file.content_type}'")
    return filename


async def _persist_upload_with_limit(upload: UploadFile, max_bytes: int, suffix: str) -> tuple[Path, int]:
    size = 0
    tmp = tempfile.NamedTemporaryFile(prefix="nr-analyze-v2-", suffix=suffix, delete=False)
    try:
        with tmp:
            while True:
                chunk = await upload.read(READ_CHUNK_BYTES)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(status_code=413, detail=f"File too large (max {max_bytes} bytes)")
                tmp.write(chunk)
    finally:
        with contextlib.suppress(Exception):
            await upload.close()
    return Path(tmp.name), size


@router.post("/upload")
async def analyze_document(
    file: UploadFile = File(...),
    preferences: Optional[str] = Form(None),
    background: bool = Query(False, description="Run in background"),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload and analyze a document with AI-powered analysis.

    Returns streaming NDJSON events with progress and final result.

    **Features:**
    - Intelligent table extraction with cross-page stitching
    - Entity and metric extraction (dates, money, percentages, etc.)
    - Form and invoice parsing
    - Multi-mode summaries (executive, data, comprehensive, etc.)
    - Sentiment and tone analysis
    - Statistical analysis with outlier detection
    - Auto-generated visualizations
    - AI-powered insights, risks, and opportunities
    - Predictive analytics
    """
    settings = get_settings()
    file_name = _validate_upload(file)

    # Parse preferences
    prefs = None
    if preferences:
        try:
            prefs_dict = json.loads(preferences)
            prefs = AnalysisPreferences(
                analysis_depth=AnalysisDepth[prefs_dict.get("analysis_depth", "standard").upper()],
                focus_areas=prefs_dict.get("focus_areas", []),
                output_format=prefs_dict.get("output_format", "executive"),
                language=prefs_dict.get("language", "en"),
                industry=prefs_dict.get("industry"),
                enable_predictions=prefs_dict.get("enable_predictions", True),
                enable_recommendations=prefs_dict.get("enable_recommendations", True),
                auto_chart_generation=prefs_dict.get("auto_chart_generation", True),
                max_charts=prefs_dict.get("max_charts", 10),
                summary_mode=SummaryMode[prefs_dict.get("summary_mode", "executive").upper()],
            )
        except Exception as e:
            logger.warning(f"Failed to parse preferences: {e}")

    orchestrator = get_orchestrator()

    if background:
        suffix = Path(file_name).suffix or ".bin"
        upload_path, size_bytes = await _persist_upload_with_limit(file, settings.max_upload_bytes, suffix=suffix)
        analysis_id = orchestrator.new_analysis_id()

        async def runner(job_id: str) -> None:
            try:
                async def _events():
                    async for event in orchestrator.analyze_document_streaming(
                        file_bytes=None,
                        file_name=file_name,
                        file_path=upload_path,
                        preferences=prefs,
                        analysis_id=analysis_id,
                    ):
                        yield event

                def _result_builder(event: dict) -> dict:
                    if event.get("event") != "result":
                        return {}
                    tables = event.get("tables") or []
                    charts = event.get("chart_suggestions") or []
                    return {
                        "analysis_id": event.get("analysis_id"),
                        "document_name": event.get("document_name"),
                        "table_count": len(tables),
                        "chart_count": len(charts),
                        "warnings": event.get("warnings") or [],
                    }

                await run_event_stream_async(job_id, _events(), result_builder=_result_builder)
            finally:
                with contextlib.suppress(FileNotFoundError):
                    upload_path.unlink(missing_ok=True)

        job = await enqueue_background_job(
            job_type="enhanced_analyze_document",
            template_name=file_name,
            meta={
                "filename": file_name,
                "size_bytes": size_bytes,
                "analysis_id": analysis_id,
                "background": True,
            },
            runner=runner,
        )

        return {
            "status": "queued",
            "job_id": job["id"],
            "analysis_id": analysis_id,
        }

    suffix = Path(file_name).suffix or ".bin"
    upload_path, _ = await _persist_upload_with_limit(file, settings.max_upload_bytes, suffix=suffix)

    async def generate_events():
        try:
            async for event in orchestrator.analyze_document_streaming(
                file_bytes=None,
                file_name=file_name,
                file_path=upload_path,
                preferences=prefs,
            ):
                yield json.dumps(event) + "\n"
        finally:
            with contextlib.suppress(FileNotFoundError):
                upload_path.unlink(missing_ok=True)

    return StreamingResponse(
        generate_events(),
        media_type="application/x-ndjson",
        headers={
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get a previously computed analysis result."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return result.model_dump()


@router.get("/{analysis_id}/summary/{mode}")
async def get_summary(
    analysis_id: str,
    mode: str,
):
    """Get a specific summary mode for an analysis."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    summary = result.summaries.get(mode)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Summary mode '{mode}' not found")

    return summary.model_dump()


# =============================================================================
# QUESTION & ANSWER ENDPOINTS
# =============================================================================

@router.post("/{analysis_id}/ask")
async def ask_question(
    analysis_id: str,
    request: QuestionRequest,
):
    """
    Ask a natural language question about the analyzed document.

    Uses RAG (Retrieval-Augmented Generation) to find relevant context
    and generate accurate answers with source citations.
    """
    orchestrator = get_orchestrator()

    response = await orchestrator.ask_question(
        analysis_id=analysis_id,
        question=request.question,
        include_sources=request.include_sources,
        max_context_chunks=request.max_context_chunks,
    )

    return response.model_dump()


@router.get("/{analysis_id}/suggested-questions")
async def get_suggested_questions(analysis_id: str):
    """Get AI-generated suggested questions for an analysis."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    questions = orchestrator.ux_service.generate_suggested_questions(
        tables=result.tables,
        metrics=result.metrics,
        entities=result.entities,
    )

    return {"questions": questions}


# =============================================================================
# VISUALIZATION ENDPOINTS
# =============================================================================

@router.post("/{analysis_id}/charts/generate")
async def generate_charts(
    analysis_id: str,
    request: ChartRequest,
):
    """
    Generate charts from natural language query.

    Examples:
    - "Show me revenue by quarter as a line chart"
    - "Compare sales across regions"
    - "Create a pie chart of market share"
    """
    orchestrator = get_orchestrator()

    result = await orchestrator.generate_charts_from_query(
        analysis_id=analysis_id,
        query=request.query,
        include_trends=request.include_trends,
        include_forecasts=request.include_forecasts,
    )

    return result


@router.get("/{analysis_id}/charts")
async def get_charts(analysis_id: str):
    """Get all charts for an analysis."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "charts": [c.model_dump() for c in result.chart_suggestions],
        "suggestions": [s.model_dump() for s in result.visualization_suggestions],
    }


# =============================================================================
# DATA ENDPOINTS
# =============================================================================

@router.get("/{analysis_id}/tables")
async def get_tables(
    analysis_id: str,
    limit: int = Query(10, ge=1, le=50),
):
    """Get extracted tables from an analysis."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "tables": [t.model_dump() for t in result.tables[:limit]],
        "total": len(result.tables),
    }


@router.get("/{analysis_id}/metrics")
async def get_metrics(analysis_id: str):
    """Get extracted metrics from an analysis."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "metrics": [m.model_dump() for m in result.metrics],
        "total": len(result.metrics),
    }


@router.get("/{analysis_id}/entities")
async def get_entities(analysis_id: str):
    """Get extracted entities from an analysis."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "entities": [e.model_dump() for e in result.entities],
        "total": len(result.entities),
    }


@router.get("/{analysis_id}/insights")
async def get_insights(analysis_id: str):
    """Get AI-generated insights, risks, and opportunities."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "insights": [i.model_dump() for i in result.insights],
        "risks": [r.model_dump() for r in result.risks],
        "opportunities": [o.model_dump() for o in result.opportunities],
        "action_items": [a.model_dump() for a in result.action_items],
    }


@router.get("/{analysis_id}/quality")
async def get_data_quality(analysis_id: str):
    """Get data quality assessment for an analysis."""
    orchestrator = get_orchestrator()
    result = orchestrator.get_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if not result.data_quality:
        raise HTTPException(status_code=404, detail="Data quality assessment not available")

    return result.data_quality.model_dump()


# =============================================================================
# EXPORT ENDPOINTS
# =============================================================================

@router.post("/{analysis_id}/export")
async def export_analysis(
    analysis_id: str,
    request: ExportRequest,
):
    """
    Export analysis in various formats.

    Supported formats:
    - json: Full analysis as JSON
    - csv: Tables as CSV
    - excel: Formatted Excel workbook
    - pdf: PDF report
    - markdown: Markdown document
    - html: HTML report
    """
    orchestrator = get_orchestrator()

    try:
        format_enum = ExportFormat[request.format.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid format: {request.format}")

    try:
        content, filename = await orchestrator.export_analysis(
            analysis_id=analysis_id,
            format=format_enum,
            include_raw_data=request.include_raw_data,
            include_charts=request.include_charts,
        )
    except ValueError as e:
        logger.warning("Export not found: %s", e)
        raise HTTPException(status_code=404, detail="Analysis not found for export")
    except RuntimeError as e:
        logger.error("Export not implemented: %s", e)
        raise HTTPException(status_code=501, detail="Export format not supported")

    # Determine content type
    content_types = {
        ExportFormat.JSON: "application/json",
        ExportFormat.CSV: "text/csv",
        ExportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ExportFormat.PDF: "application/pdf",
        ExportFormat.MARKDOWN: "text/markdown",
        ExportFormat.HTML: "text/html",
    }

    return Response(
        content=content,
        media_type=content_types.get(format_enum, "application/octet-stream"),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# =============================================================================
# COMPARISON ENDPOINTS
# =============================================================================

@router.post("/compare")
async def compare_documents(request: CompareRequest):
    """Compare two analyzed documents."""
    orchestrator = get_orchestrator()

    result = await orchestrator.compare_documents(
        analysis_id_1=request.analysis_id_1,
        analysis_id_2=request.analysis_id_2,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# =============================================================================
# COLLABORATION ENDPOINTS
# =============================================================================

@router.post("/{analysis_id}/comments")
async def add_comment(
    analysis_id: str,
    request: CommentRequest,
    user=Depends(current_optional_user),
    settings=Depends(get_settings),
):
    """Add a comment to an analysis."""
    orchestrator = get_orchestrator()

    # Verify analysis exists
    result = orchestrator.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if user is not None:
        user_id = str(user.id)
        user_name = user.full_name or user.email or "User"
    else:
        user_id = "anonymous" if settings.allow_anonymous_api else "api-key"
        user_name = "Anonymous" if settings.allow_anonymous_api else "API Key"

    comment = orchestrator.ux_service.add_comment(
        analysis_id=analysis_id,
        user_id=user_id,
        user_name=user_name,
        content=request.content,
        element_type=request.element_type,
        element_id=request.element_id,
    )

    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
    }


@router.get("/{analysis_id}/comments")
async def get_comments(analysis_id: str):
    """Get all comments for an analysis."""
    orchestrator = get_orchestrator()

    comments = orchestrator.ux_service.get_comments(analysis_id)

    return {
        "comments": [
            {
                "id": c.id,
                "content": c.content,
                "user_name": c.user_name,
                "element_type": c.element_type,
                "element_id": c.element_id,
                "created_at": c.created_at.isoformat(),
                "replies": [
                    {"id": r.id, "content": r.content, "user_name": r.user_name}
                    for r in c.replies
                ],
            }
            for c in comments
        ]
    }


@router.post("/{analysis_id}/share")
async def create_share_link(
    analysis_id: str,
    request: ShareRequest,
):
    """Create a shareable link for an analysis."""
    orchestrator = get_orchestrator()

    # Verify analysis exists
    result = orchestrator.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    share = orchestrator.ux_service.create_share_link(
        analysis_id=analysis_id,
        created_by="api",
        access_level=request.access_level,
        expires_hours=request.expires_hours,
        password_protected=request.password_protected,
        allowed_emails=request.allowed_emails,
    )

    return {
        "share_id": share.id,
        "share_url": f"/analyze/v2/shared/{share.id}",
        "access_level": share.access_level,
        "expires_at": share.expires_at.isoformat() if share.expires_at else None,
    }


@router.get("/shared/{share_id}")
async def get_shared_analysis(share_id: str):
    """Retrieve a shared analysis by share link."""
    orchestrator = get_orchestrator()
    share = orchestrator.ux_service.get_share(share_id)
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")

    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share link expired")

    result = orchestrator.get_analysis(share.analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        orchestrator.ux_service.record_share_access(share_id)
    except Exception:
        pass

    return {
        "share_id": share.id,
        "analysis_id": share.analysis_id,
        "access_level": share.access_level,
        "analysis": result.model_dump(),
    }


# =============================================================================
# INTEGRATION ENDPOINTS
# =============================================================================

@router.get("/integrations")
async def list_integrations():
    """List registered external integrations."""
    orchestrator = get_orchestrator()
    return {"integrations": orchestrator.integration_service.list_integrations()}


@router.post("/integrations")
async def register_integration(request: IntegrationRequest):
    """Register an external integration (Slack/Teams/Jira/Email)."""
    orchestrator = get_orchestrator()
    try:
        integration_id = orchestrator.integration_service.register_integration(
            name=request.name,
            integration_type=request.integration_type,
            config=request.config,
        )
    except ValueError as exc:
        logger.warning("Invalid integration config: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid integration configuration")

    return {"id": integration_id, "type": request.integration_type}


@router.post("/integrations/{integration_id}/notify")
async def send_integration_notification(
    integration_id: str,
    request: IntegrationMessageRequest,
):
    """Send a notification through an integration."""
    orchestrator = get_orchestrator()
    success = await orchestrator.integration_service.send_notification(
        integration_id,
        request.message,
        **(request.data or {}),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found or notification failed")
    return {"status": "sent", "integration_id": integration_id}


@router.post("/integrations/{integration_id}/items")
async def create_integration_item(
    integration_id: str,
    request: IntegrationItemRequest,
):
    """Create an item (ticket/task) in an external integration."""
    orchestrator = get_orchestrator()
    item_id = await orchestrator.integration_service.create_external_item(
        integration_id,
        request.data or {},
    )
    if not item_id:
        raise HTTPException(status_code=404, detail="Integration not found or create failed")
    return {"status": "created", "integration_id": integration_id, "item_id": item_id}


@router.get("/sources")
async def list_data_sources():
    """List registered data sources."""
    orchestrator = get_orchestrator()
    sources = orchestrator.integration_service.list_data_sources()
    return {
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type.value,
                "created_at": s.created_at.isoformat(),
                "last_used": s.last_used.isoformat() if s.last_used else None,
                "is_active": s.is_active,
            }
            for s in sources
        ]
    }


@router.post("/sources")
async def register_data_source(request: DataSourceRequest):
    """Register a data source connection."""
    orchestrator = get_orchestrator()
    try:
        source_type = DataSourceType(request.source_type)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Unknown data source type: {request.source_type}")

    connection = orchestrator.integration_service.register_data_source(
        name=request.name,
        source_type=source_type,
        config=request.config,
    )
    return {
        "id": connection.id,
        "name": connection.name,
        "type": connection.type.value,
        "created_at": connection.created_at.isoformat(),
    }


@router.post("/sources/{connection_id}/fetch")
async def fetch_data_from_source(connection_id: str, request: DataFetchRequest):
    """Fetch data from a registered data source."""
    orchestrator = get_orchestrator()
    result = await orchestrator.integration_service.fetch_from_source(
        connection_id=connection_id,
        query=request.query,
    )
    return {
        "success": result.success,
        "data": result.data,
        "error": result.error,
        "metadata": result.metadata,
    }


@router.post("/triggers")
async def create_trigger(request: TriggerRequest):
    """Create a workflow trigger."""
    orchestrator = get_orchestrator()
    trigger = orchestrator.integration_service.create_trigger(
        name=request.name,
        trigger_type=request.trigger_type,
        config=request.config,
        action=request.action,
    )
    return {
        "id": trigger.id,
        "name": trigger.name,
        "trigger_type": trigger.trigger_type,
        "action": trigger.action,
        "enabled": trigger.enabled,
    }


@router.post("/pipelines")
async def create_pipeline(request: PipelineRequest):
    """Create a workflow pipeline."""
    orchestrator = get_orchestrator()
    pipeline = orchestrator.integration_service.create_pipeline(
        name=request.name,
        steps=request.steps,
    )
    return {"id": pipeline.id, "name": pipeline.name, "step_count": len(pipeline.steps)}


@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(pipeline_id: str, request: PipelineExecuteRequest):
    """Execute a workflow pipeline."""
    orchestrator = get_orchestrator()
    try:
        execution = await orchestrator.integration_service.execute_pipeline(
            pipeline_id=pipeline_id,
            input_data=request.input_data,
        )
    except ValueError as exc:
        logger.warning("Pipeline not found: %s", exc)
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {
        "id": execution.id,
        "pipeline_id": execution.pipeline_id,
        "status": execution.status,
        "started_at": execution.started_at.isoformat(),
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "step_results": execution.step_results,
        "error": execution.error,
    }


@router.post("/schedules")
async def schedule_analysis(request: ScheduleRequest):
    """Schedule a recurring analysis workflow."""
    orchestrator = get_orchestrator()
    scheduled = orchestrator.integration_service.schedule_analysis(
        name=request.name,
        source_config=request.source_config,
        schedule=request.schedule,
        analysis_config=request.analysis_config,
        notifications=request.notifications,
    )
    return scheduled.model_dump()


@router.post("/webhooks")
async def register_webhook(request: WebhookRequest):
    """Register a webhook for analysis events."""
    orchestrator = get_orchestrator()
    webhook = orchestrator.integration_service.register_webhook(
        url=request.url,
        events=request.events,
        secret=request.secret,
    )
    return webhook.model_dump()


@router.post("/webhooks/{webhook_id}/send")
async def send_webhook_test(webhook_id: str, request: WebhookSendRequest):
    """Send a test webhook event."""
    orchestrator = get_orchestrator()
    success = await orchestrator.integration_service.send_webhook(
        webhook_id=webhook_id,
        event=request.event,
        payload=request.payload,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found or send failed")
    return {"status": "sent", "webhook_id": webhook_id}


# =============================================================================
# CONFIGURATION ENDPOINTS
# =============================================================================

@router.get("/config/industries")
async def get_industry_options():
    """Get available industry options for analysis configuration."""
    orchestrator = get_orchestrator()
    return {"industries": orchestrator.get_industry_options()}


@router.get("/config/export-formats")
async def get_export_formats():
    """Get available export formats."""
    orchestrator = get_orchestrator()
    return {"formats": orchestrator.get_export_formats()}


@router.get("/config/chart-types")
async def get_chart_types():
    """Get available chart types."""
    return {
        "chart_types": [
            {"value": ct.value, "label": ct.value.replace("_", " ").title()}
            for ct in ChartType
        ]
    }


@router.get("/config/summary-modes")
async def get_summary_modes():
    """Get available summary modes."""
    return {
        "modes": [
            {
                "value": sm.value,
                "label": sm.value.replace("_", " ").title(),
                "description": {
                    "executive": "C-suite 3-bullet overview",
                    "data": "Key figures and trends",
                    "quick": "One sentence essence",
                    "comprehensive": "Full structured analysis",
                    "action_items": "To-dos and next steps",
                    "risks": "Potential issues and concerns",
                    "opportunities": "Growth areas identified",
                }.get(sm.value, ""),
            }
            for sm in SummaryMode
        ]
    }
