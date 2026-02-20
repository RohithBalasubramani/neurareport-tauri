"""
AI Agents API Routes v2 - Production-grade implementation.

Features:
- Persistent task storage
- Idempotency support
- Progress tracking + SSE streaming
- Task management (cancel, retry)
- Comprehensive error handling
- Cost tracking

All tasks are persisted to SQLite and survive server restarts.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.api.middleware import limiter
from backend.app.services.agents import (
    AgentTaskStatus,
    AgentType,
    TaskConflictError,
    TaskNotFoundError,
)
from backend.app.services.agents import agent_service_v2
from backend.app.services.agents.base_agent import (
    AgentError,
    ValidationError,
)
from backend.app.services.security import require_api_key

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_key)])


# =============================================================================
# REQUEST MODELS
# =============================================================================

class ResearchRequest(BaseModel):
    """Request to run the research agent."""
    topic: str = Field(
        ...,
        max_length=500,
        description="Topic to research (must be at least 2 words)",
        examples=["AI trends in healthcare 2025", "Climate change mitigation strategies"],
    )
    depth: Literal["quick", "moderate", "comprehensive"] = Field(
        default="comprehensive",
        description="Research depth - quick (overview), moderate (balanced), comprehensive (detailed)",
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        max_length=10,
        description="Specific areas to focus on (max 10)",
        examples=[["regulation", "adoption", "startups"]],
    )
    max_sections: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of sections in the report",
    )
    idempotency_key: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Unique key for deduplication (same key returns existing task)",
    )
    priority: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Task priority (0=lowest, 10=highest)",
    )
    webhook_url: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="URL to notify when task completes",
    )
    sync: bool = Field(
        default=True,
        description="If true, wait for completion. If false, return immediately.",
    )

    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Topic cannot be empty or whitespace")
        if len(v.split()) < 2:
            raise ValueError("Topic must contain at least 2 words for meaningful research")
        return v

    @field_validator('focus_areas')
    @classmethod
    def validate_focus_areas(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v:
            return [area.strip() for area in v if area and area.strip()]
        return v


class DataAnalystRequest(BaseModel):
    """Request to run the data analyst agent."""
    question: str = Field(
        ..., min_length=5, max_length=1000,
        description="Question to answer about the data",
    )
    data: List[Dict[str, Any]] = Field(
        ..., min_length=1,
        description="Tabular data as list of objects",
    )
    data_description: Optional[str] = Field(
        default=None, max_length=2000,
        description="Optional description of the dataset",
    )
    generate_charts: bool = Field(
        default=True,
        description="Whether to suggest chart visualisations",
    )
    idempotency_key: Optional[str] = Field(default=None, max_length=64)
    priority: int = Field(default=0, ge=0, le=10)
    webhook_url: Optional[str] = Field(default=None, max_length=2000)
    sync: bool = Field(default=True)

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v.split()) < 2:
            raise ValueError("Question must contain at least 2 words")
        return v


class EmailDraftRequest(BaseModel):
    """Request to run the email draft agent."""
    context: str = Field(
        ..., min_length=5, max_length=5000,
        description="Background context for the email",
    )
    purpose: str = Field(
        ..., min_length=3, max_length=1000,
        description="Purpose/intent of the email",
    )
    tone: str = Field(
        default="professional",
        description="Tone: professional, friendly, formal, casual, empathetic, assertive",
    )
    recipient_info: Optional[str] = Field(
        default=None, max_length=2000,
        description="Information about the recipient",
    )
    previous_emails: Optional[List[str]] = Field(
        default=None,
        description="Previous emails in thread (last 3 kept)",
    )
    include_subject: bool = Field(default=True)
    idempotency_key: Optional[str] = Field(default=None, max_length=64)
    priority: int = Field(default=0, ge=0, le=10)
    webhook_url: Optional[str] = Field(default=None, max_length=2000)
    sync: bool = Field(default=True)


class ContentRepurposeRequest(BaseModel):
    """Request to run the content repurposing agent."""
    content: str = Field(
        ..., min_length=20, max_length=50000,
        description="Source content to repurpose",
    )
    source_format: str = Field(
        ..., min_length=1, max_length=50,
        description="Format of the source content (article, report, transcript, etc.)",
    )
    target_formats: List[str] = Field(
        ..., min_length=1,
        description="Target formats: tweet_thread, linkedin_post, blog_summary, slides, "
                    "email_newsletter, video_script, infographic, podcast_notes, press_release, "
                    "executive_summary",
    )
    preserve_key_points: bool = Field(default=True)
    adapt_length: bool = Field(default=True)
    idempotency_key: Optional[str] = Field(default=None, max_length=64)
    priority: int = Field(default=0, ge=0, le=10)
    webhook_url: Optional[str] = Field(default=None, max_length=2000)
    sync: bool = Field(default=True)


class ProofreadingRequest(BaseModel):
    """Request to run the proofreading agent."""
    text: str = Field(
        ..., min_length=10, max_length=50000,
        description="Text to proofread",
    )
    style_guide: Optional[str] = Field(
        default=None,
        description="Style guide: ap, chicago, apa, mla, none",
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Focus areas: grammar, spelling, punctuation, clarity, conciseness, "
                    "tone, consistency, formatting, word_choice, structure",
    )
    preserve_voice: bool = Field(
        default=True,
        description="Preserve the author's voice while correcting",
    )
    idempotency_key: Optional[str] = Field(default=None, max_length=64)
    priority: int = Field(default=0, ge=0, le=10)
    webhook_url: Optional[str] = Field(default=None, max_length=2000)
    sync: bool = Field(default=True)


class ReportAnalystRequest(BaseModel):
    """Request to run the Report Analyst agent."""
    run_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Report run ID to analyze",
    )
    analysis_type: str = Field(
        default="summarize",
        description="Analysis type: summarize, insights, compare, qa",
    )
    question: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Question text (required for 'qa' analysis type)",
    )
    compare_run_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Second run ID for comparison (required for 'compare' analysis type)",
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Optional areas to focus analysis on",
    )
    idempotency_key: Optional[str] = Field(default=None, max_length=64)
    priority: int = Field(default=0, ge=0, le=10)
    webhook_url: Optional[str] = Field(default=None, max_length=2000)
    sync: bool = Field(default=True)


class GenerateReportFromAgentRequest(BaseModel):
    """Request to trigger report generation from an agent task result."""
    template_id: str = Field(..., min_length=1, description="Template to use for report generation")
    connection_id: str = Field(..., min_length=1, description="Database connection to use")
    start_date: str = Field(..., description="Report start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Report end date (YYYY-MM-DD)")
    key_values: Optional[Dict[str, Any]] = Field(default=None, description="Additional key-value parameters")
    docx: bool = Field(default=False, description="Generate DOCX artifact")
    xlsx: bool = Field(default=False, description="Generate XLSX artifact")


class CancelRequest(BaseModel):
    """Request to cancel a task."""
    reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional cancellation reason",
    )


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class ProgressResponse(BaseModel):
    """Progress information for a task."""
    percent: int = Field(..., ge=0, le=100)
    message: Optional[str] = None
    current_step: Optional[str] = None
    total_steps: Optional[int] = None
    current_step_num: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error information for a failed task."""
    code: Optional[str] = None
    message: Optional[str] = None
    retryable: bool = True


class CostResponse(BaseModel):
    """Cost tracking information."""
    tokens_input: int = 0
    tokens_output: int = 0
    estimated_cost_cents: int = 0


class AttemptsResponse(BaseModel):
    """Retry attempt information."""
    count: int = 0
    max: int = 3


class TimestampsResponse(BaseModel):
    """Task timestamps."""
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class LinksResponse(BaseModel):
    """HATEOAS links for task."""
    self_link: str = Field(..., alias="self")
    cancel: Optional[str] = None
    retry: Optional[str] = None
    events: str
    stream: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class TaskResponse(BaseModel):
    """Standard task response."""
    task_id: str
    agent_type: str
    status: str
    progress: ProgressResponse
    result: Optional[Dict[str, Any]] = None
    error: Optional[ErrorResponse] = None
    timestamps: TimestampsResponse
    cost: CostResponse
    attempts: AttemptsResponse
    links: LinksResponse

    model_config = ConfigDict(populate_by_name=True)


class TaskListResponse(BaseModel):
    """Response for task listing."""
    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int


class TaskEventResponse(BaseModel):
    """Task event for audit trail."""
    id: int
    event_type: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class StatsResponse(BaseModel):
    """Service statistics."""
    pending: int = 0
    running: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    retrying: int = 0
    total: int = 0


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def task_to_response(task) -> TaskResponse:
    """Convert AgentTaskModel to API response."""
    return TaskResponse(
        task_id=task.task_id,
        agent_type=task.agent_type.value if hasattr(task.agent_type, 'value') else task.agent_type,
        status=task.status.value if hasattr(task.status, 'value') else task.status,
        progress=ProgressResponse(
            percent=task.progress_percent,
            message=task.progress_message,
            current_step=task.current_step,
            total_steps=task.total_steps,
            current_step_num=task.current_step_num,
        ),
        result=task.result,
        error=ErrorResponse(
            code=task.error_code,
            message=task.error_message,
            retryable=task.is_retryable,
        ) if task.error_message else None,
        timestamps=TimestampsResponse(
            created_at=task.created_at.isoformat() if task.created_at else None,
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
        ),
        cost=CostResponse(
            tokens_input=task.tokens_input,
            tokens_output=task.tokens_output,
            estimated_cost_cents=task.estimated_cost_cents,
        ),
        attempts=AttemptsResponse(
            count=task.attempt_count,
            max=task.max_attempts,
        ),
        links=LinksResponse(
            **{
                "self": f"/agents/v2/tasks/{task.task_id}",
                "cancel": f"/agents/v2/tasks/{task.task_id}/cancel" if task.can_cancel() else None,
                "retry": f"/agents/v2/tasks/{task.task_id}/retry" if task.can_retry() else None,
                "events": f"/agents/v2/tasks/{task.task_id}/events",
                "stream": f"/agents/v2/tasks/{task.task_id}/stream" if task.is_active() else None,
            }
        ),
    )


# =============================================================================
# RESEARCH AGENT ENDPOINT
# =============================================================================

@router.post(
    "/research",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run Research Agent",
    description="""
    Run the research agent to compile a comprehensive report on a topic.

    The agent will:
    1. Generate a research outline based on the topic and depth
    2. Research each section with relevant findings
    3. Synthesize findings into a cohesive report with recommendations

    **Idempotency**: Provide an `idempotency_key` to ensure the same request
    doesn't create duplicate tasks. If a task with the same key exists,
    it will be returned instead of creating a new one.

    **Async Mode**: Set `sync=false` to return immediately with task ID.
    Poll the task endpoint or use webhook for completion notification.
    """,
    responses={
        202: {"description": "Task created/returned successfully"},
        400: {"description": "Invalid input parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("10/minute")
async def run_research_agent(request: Request, response: Response, body: ResearchRequest):
    """Run the research agent to compile a report on a topic."""
    try:
        task = await agent_service_v2.run_research(
            topic=body.topic,
            depth=body.depth,
            focus_areas=body.focus_areas,
            max_sections=body.max_sections,
            idempotency_key=body.idempotency_key,
            priority=body.priority,
            webhook_url=body.webhook_url,
            sync=body.sync,
        )
        return task_to_response(task)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": e.code,
                "message": e.message,
                "field": e.details.get("field"),
            },
        )

    except AgentError as e:
        if e.code == "LLM_RATE_LIMITED":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": e.code,
                    "message": e.message,
                    "retry_after": e.details.get("retry_after", 60),
                },
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": e.code,
                "message": e.message,
                "retryable": e.retryable,
            },
        )

    except Exception as e:
        logger.exception("Agent failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
            },
        )


def _handle_agent_error(e: Exception) -> None:
    """Shared error handler for all agent endpoints."""
    if isinstance(e, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message, "field": e.details.get("field")},
        )
    if isinstance(e, AgentError):
        if e.code == "LLM_RATE_LIMITED":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"code": e.code, "message": e.message, "retry_after": e.details.get("retry_after", 60)},
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": e.code, "message": e.message, "retryable": e.retryable},
        )
    logger.exception("Agent failed: %s", e)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": "INTERNAL_ERROR", "message": "An internal error occurred"},
    )


# =============================================================================
# DATA ANALYST ENDPOINT
# =============================================================================

@router.post(
    "/data-analyst",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run Data Analyst Agent",
    description="Analyse tabular data: answer questions, compute statistics, suggest charts, generate SQL.",
)
@limiter.limit("10/minute")
async def run_data_analyst_agent(request: Request, response: Response, body: DataAnalystRequest):
    """Run the data analyst agent."""
    try:
        task = await agent_service_v2.run_data_analyst(
            question=body.question,
            data=body.data,
            data_description=body.data_description,
            generate_charts=body.generate_charts,
            idempotency_key=body.idempotency_key,
            priority=body.priority,
            webhook_url=body.webhook_url,
            sync=body.sync,
        )
        return task_to_response(task)
    except Exception as e:
        _handle_agent_error(e)


# =============================================================================
# EMAIL DRAFT ENDPOINT
# =============================================================================

@router.post(
    "/email-draft",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run Email Draft Agent",
    description="Compose email drafts with tone control, thread context, and follow-up actions.",
)
@limiter.limit("10/minute")
async def run_email_draft_agent(request: Request, response: Response, body: EmailDraftRequest):
    """Run the email draft agent."""
    try:
        task = await agent_service_v2.run_email_draft(
            context=body.context,
            purpose=body.purpose,
            tone=body.tone,
            recipient_info=body.recipient_info,
            previous_emails=body.previous_emails,
            include_subject=body.include_subject,
            idempotency_key=body.idempotency_key,
            priority=body.priority,
            webhook_url=body.webhook_url,
            sync=body.sync,
        )
        return task_to_response(task)
    except Exception as e:
        _handle_agent_error(e)


# =============================================================================
# CONTENT REPURPOSE ENDPOINT
# =============================================================================

@router.post(
    "/content-repurpose",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run Content Repurposing Agent",
    description="Transform content into multiple formats (tweets, LinkedIn, slides, newsletters, etc.).",
)
@limiter.limit("10/minute")
async def run_content_repurpose_agent(request: Request, response: Response, body: ContentRepurposeRequest):
    """Run the content repurposing agent."""
    try:
        task = await agent_service_v2.run_content_repurpose(
            content=body.content,
            source_format=body.source_format,
            target_formats=body.target_formats,
            preserve_key_points=body.preserve_key_points,
            adapt_length=body.adapt_length,
            idempotency_key=body.idempotency_key,
            priority=body.priority,
            webhook_url=body.webhook_url,
            sync=body.sync,
        )
        return task_to_response(task)
    except Exception as e:
        _handle_agent_error(e)


# =============================================================================
# PROOFREADING ENDPOINT
# =============================================================================

@router.post(
    "/proofreading",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run Proofreading Agent",
    description="Grammar, style, and clarity checking with style guide support and readability scoring.",
)
@limiter.limit("10/minute")
async def run_proofreading_agent(request: Request, response: Response, body: ProofreadingRequest):
    """Run the proofreading agent."""
    try:
        task = await agent_service_v2.run_proofreading(
            text=body.text,
            style_guide=body.style_guide,
            focus_areas=body.focus_areas,
            preserve_voice=body.preserve_voice,
            idempotency_key=body.idempotency_key,
            priority=body.priority,
            webhook_url=body.webhook_url,
            sync=body.sync,
        )
        return task_to_response(task)
    except Exception as e:
        _handle_agent_error(e)


# =============================================================================
# REPORT ANALYST ENDPOINT
# =============================================================================

@router.post(
    "/report-analyst",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run Report Analyst Agent",
    description="Analyze, summarize, compare, or ask questions about generated reports.",
)
@limiter.limit("10/minute")
async def run_report_analyst_agent(request: Request, response: Response, body: ReportAnalystRequest):
    """Run the report analyst agent."""
    try:
        task = await agent_service_v2.run_report_analyst(
            run_id=body.run_id,
            analysis_type=body.analysis_type,
            question=body.question,
            compare_run_id=body.compare_run_id,
            focus_areas=body.focus_areas,
            idempotency_key=body.idempotency_key,
            priority=body.priority,
            webhook_url=body.webhook_url,
            sync=body.sync,
        )
        return task_to_response(task)
    except Exception as e:
        _handle_agent_error(e)


# =============================================================================
# AGENT-TRIGGERED REPORT GENERATION ENDPOINT
# =============================================================================

@router.post(
    "/tasks/{task_id}/generate-report",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Report from Agent Task",
    description="Trigger report generation using an agent task's result as additional context.",
)
@limiter.limit("5/minute")
async def generate_report_from_agent(request: Request, response: Response, task_id: str, body: GenerateReportFromAgentRequest):
    """Generate a report using agent task results as context."""
    task = agent_service_v2.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TASK_NOT_FOUND", "message": f"Task {task_id} not found"},
        )
    if task.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "TASK_NOT_COMPLETED", "message": f"Task must be completed (current: {task.status})"},
        )

    # Merge agent result into key_values so the report template can reference it
    key_values = dict(body.key_values or {})
    if task.result:
        key_values["_agent_context"] = {
            "task_id": task_id,
            "agent_type": task.agent_type if isinstance(task.agent_type, str) else task.agent_type.value,
            "result": task.result,
        }

    try:
        from backend.app.schemas.generate.reports import RunPayload
        from backend.legacy.services.report_service import queue_report_job

        payload = RunPayload(
            template_id=body.template_id,
            connection_id=body.connection_id,
            start_date=body.start_date,
            end_date=body.end_date,
            key_values=key_values,
            docx=body.docx,
            xlsx=body.xlsx,
        )
        # Set correlation_id on request state for tracing
        if not hasattr(request.state, "correlation_id"):
            request.state.correlation_id = f"agent-{task_id}"

        job = await queue_report_job(payload, request, kind="pdf")
        job_id = (job.get("job_id") or job.get("id")) if isinstance(job, dict) else getattr(job, "job_id", getattr(job, "id", str(job)))
        return {
            "job_id": job_id,
            "task_id": task_id,
            "status": "queued",
            "message": "Report generation triggered from agent task result",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to trigger report from agent: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "REPORT_TRIGGER_FAILED", "message": str(e)},
        )


# =============================================================================
# TASK MANAGEMENT ENDPOINTS
# =============================================================================

@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get Task",
    description="Get a task by ID with full status, progress, and result information.",
)
async def get_task(task_id: str):
    """Get task by ID."""
    task = agent_service_v2.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TASK_NOT_FOUND", "message": f"Task {task_id} not found"},
        )
    return task_to_response(task)


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="List Tasks",
    description="List tasks with optional filtering by agent type, status, or user.",
)
async def list_tasks(
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    task_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
):
    """List all tasks with optional filtering."""
    tasks = agent_service_v2.list_tasks(
        agent_type=agent_type,
        status=task_status,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )

    total = agent_service_v2.count_tasks(
        agent_type=agent_type,
        status=task_status,
        user_id=user_id,
    )

    return TaskListResponse(
        tasks=[task_to_response(t) for t in tasks],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/tasks/{task_id}/cancel",
    response_model=TaskResponse,
    summary="Cancel Task",
    description="Cancel a pending or running task. Cannot cancel completed tasks.",
)
async def cancel_task(task_id: str, request: Optional[CancelRequest] = None):
    """Cancel a pending or running task."""
    try:
        reason = request.reason if request else None
        task = agent_service_v2.cancel_task(task_id, reason)
        return task_to_response(task)

    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TASK_NOT_FOUND", "message": f"Task {task_id} not found"},
        )

    except TaskConflictError as e:
        logger.warning("cancel_task_conflict", extra={"task_id": task_id, "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CANNOT_CANCEL", "message": "Task cannot be cancelled in its current state"},
        )


@router.post(
    "/tasks/{task_id}/retry",
    response_model=TaskResponse,
    summary="Retry Task",
    description="Manually retry a failed task. Only works for retryable failures.",
)
async def retry_task(task_id: str):
    """Retry a failed task."""
    try:
        task = await agent_service_v2.retry_task(task_id)
        return task_to_response(task)

    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TASK_NOT_FOUND", "message": f"Task {task_id} not found"},
        )

    except TaskConflictError as e:
        logger.warning("retry_task_conflict", extra={"task_id": task_id, "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CANNOT_RETRY", "message": "Task cannot be retried in its current state"},
        )


@router.get(
    "/tasks/{task_id}/events",
    response_model=List[TaskEventResponse],
    summary="Get Task Events",
    description="Get audit trail events for a task.",
)
async def get_task_events(
    task_id: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of events"),
):
    """Get audit events for a task."""
    # First check if task exists
    task = agent_service_v2.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TASK_NOT_FOUND", "message": f"Task {task_id} not found"},
        )

    events = agent_service_v2.get_task_events(task_id, limit=limit)
    return [TaskEventResponse(**e) for e in events]


# =============================================================================
# SSE PROGRESS STREAMING (Trade-off 2)
# =============================================================================

@router.get(
    "/tasks/{task_id}/stream",
    summary="Stream Task Progress (SSE)",
    description="""
    Stream real-time progress updates for a task using Server-Sent Events.

    Returns an NDJSON stream of progress events. Each line is a JSON object
    with `event` and `data` fields. The stream terminates when the task
    reaches a terminal state (completed, failed, cancelled) or the timeout
    is reached.

    **Content-Type**: `text/event-stream`

    **Events**:
    - `progress`: Task progress update with percent, message, step info
    - `complete`: Task reached terminal state (includes result or error)
    - `error`: An error occurred (task not found, stream timeout)

    **Example usage** (JavaScript):
    ```js
    const eventSource = new EventSource('/agents/v2/tasks/abc123/stream');
    eventSource.onmessage = (e) => {
      const data = JSON.parse(e.data);
      console.log(data.event, data.data);
    };
    ```
    """,
    responses={
        200: {"description": "SSE progress stream", "content": {"text/event-stream": {}}},
        404: {"description": "Task not found"},
    },
)
async def stream_task_progress(
    task_id: str,
    request: Request,
    poll_interval: float = Query(0.5, ge=0.1, le=5.0, description="Poll interval in seconds"),
    timeout: float = Query(300.0, ge=10.0, le=600.0, description="Stream timeout in seconds"),
):
    """Stream real-time progress for a task via Server-Sent Events."""
    # Verify task exists before opening stream
    task = agent_service_v2.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TASK_NOT_FOUND", "message": f"Task {task_id} not found"},
        )

    async def _event_generator():
        async for event in agent_service_v2.stream_task_progress(
            task_id,
            poll_interval=poll_interval,
            timeout=timeout,
        ):
            # Check if client disconnected
            if await request.is_disconnected():
                return
            # SSE format: data: {json}\n\n
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get Statistics",
    description="Get task counts by status.",
)
async def get_stats():
    """Get service statistics."""
    stats = agent_service_v2.get_stats()
    return StatsResponse(**stats)


@router.get(
    "/types",
    summary="List Agent Types",
    description="List available agent types with descriptions.",
)
async def list_agent_types():
    """List available agent types."""
    return {
        "types": [
            {
                "id": "research",
                "name": "Research Agent",
                "description": "Deep-dive research and report compilation",
                "endpoint": "/agents/v2/research",
            },
            {
                "id": "data_analyst",
                "name": "Data Analyst Agent",
                "description": "Analyse tabular data with statistics, insights, chart suggestions, and SQL",
                "endpoint": "/agents/v2/data-analyst",
            },
            {
                "id": "email_draft",
                "name": "Email Draft Agent",
                "description": "Compose email drafts with tone control, thread context, and follow-ups",
                "endpoint": "/agents/v2/email-draft",
            },
            {
                "id": "content_repurpose",
                "name": "Content Repurposing Agent",
                "description": "Transform content into 10 output formats (tweets, slides, newsletters, etc.)",
                "endpoint": "/agents/v2/content-repurpose",
            },
            {
                "id": "proofreading",
                "name": "Proofreading Agent",
                "description": "Grammar, style, and clarity checking with style guide support",
                "endpoint": "/agents/v2/proofreading",
            },
            {
                "id": "report_analyst",
                "name": "Report Analyst",
                "description": "Analyze, summarize, compare, or ask questions about generated reports",
                "endpoint": "/agents/v2/report-analyst",
            },
        ]
    }


@router.get(
    "/formats/repurpose",
    summary="List Repurpose Formats",
    description="List available content repurposing target formats with descriptions.",
)
async def list_repurpose_formats():
    """List available content repurposing formats."""
    return {
        "formats": [
            {"id": "tweet_thread", "name": "Twitter Thread", "description": "5-10 tweets, 280 chars each"},
            {"id": "linkedin_post", "name": "LinkedIn Post", "description": "Professional, 1300 chars max"},
            {"id": "blog_summary", "name": "Blog Summary", "description": "300-500 words"},
            {"id": "slides", "name": "Presentation Slides", "description": "Title + bullet points per slide"},
            {"id": "email_newsletter", "name": "Email Newsletter", "description": "Catchy subject, scannable body"},
            {"id": "video_script", "name": "Video Script", "description": "Conversational, 2-3 minutes"},
            {"id": "infographic", "name": "Infographic Copy", "description": "Headlines, stats, takeaways"},
            {"id": "podcast_notes", "name": "Podcast Show Notes", "description": "Summary, timestamps, links"},
            {"id": "press_release", "name": "Press Release", "description": "Headline, lead, quotes"},
            {"id": "executive_summary", "name": "Executive Summary", "description": "1 page, key decisions"},
        ]
    }


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the agents service is healthy.",
)
async def health_check():
    """Health check endpoint."""
    try:
        stats = agent_service_v2.get_stats()
        return {
            "status": "healthy",
            "tasks": stats,
        }
    except Exception as e:
        logger.warning("Agents v2 health check failed: %s", e)
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": "Service unavailable"},
        )
