"""Export API Routes.

REST API endpoints for document export and distribution.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from backend.app.api.middleware import limiter, RATE_LIMIT_STRICT, RATE_LIMIT_STANDARD

from backend.app.schemas.export.export import (
    BulkExportRequest,
    DistributionRequest,
    DistributionResponse,
    EmailCampaignRequest,
    EmbedGenerateRequest,
    EmbedResponse,
    ExportRequest,
    ExportResponse,
    ExportStatus,
    PortalPublishRequest,
    SlackMessageRequest,
    TeamsMessageRequest,
    WebhookDeliveryRequest,
)
from backend.app.services.export.service import distribution_service, export_service

from backend.app.services.security import require_api_key
from fastapi import Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Any, List, Optional


class ExportOptions(BaseModel):
    """Typed export options for format endpoints.

    Known fields are validated; additional fields are passed through
    to the export service to maintain forward compatibility.
    """
    model_config = {"extra": "allow"}

    page_size: Optional[str] = Field(None, max_length=20)
    orientation: Optional[str] = Field(None, pattern="^(portrait|landscape)$")
    include_toc: Optional[bool] = None
    include_cover: Optional[bool] = None
    watermark: Optional[str] = Field(None, max_length=100)
    header: Optional[str] = Field(None, max_length=500)
    footer: Optional[str] = Field(None, max_length=500)
    margin_mm: Optional[int] = Field(None, ge=0, le=100)
    quality: Optional[str] = Field(None, pattern="^(draft|standard|high)$")


class PrintRequest(BaseModel):
    """Request body for printing a document."""
    printer_id: Optional[str] = None
    copies: int = Field(1, ge=1, le=100)
    options: dict[str, Any] = Field(default_factory=dict)


router = APIRouter(tags=["export"], dependencies=[Depends(require_api_key)])


# ── Static-path routes (must be registered before /{document_id} routes) ──


@router.get("/printers")
async def list_printers():
    """List available printers."""
    printers = await export_service.list_printers()
    return {"printers": printers}


@router.get("/jobs")
async def list_export_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    format: Optional[str] = Query(None, description="Filter by export format"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
):
    """List all export jobs with optional filtering."""
    result = await export_service.list_export_jobs(
        status=status,
        format=format,
        limit=limit,
        offset=offset,
    )
    return result


# ── Dynamic-path routes ──


@router.post("/{document_id}/pdf")
@limiter.limit(RATE_LIMIT_STANDARD)
async def export_to_pdf(request: Request, document_id: str, options: Optional[ExportOptions] = None):
    """Export document to PDF format."""
    job = await export_service.create_export_job(
        document_id=document_id,
        format="pdf",
        options=options.model_dump(exclude_none=True) if options else {},
    )
    return job


@router.post("/{document_id}/pdfa")
@limiter.limit(RATE_LIMIT_STANDARD)
async def export_to_pdfa(request: Request, document_id: str, options: Optional[ExportOptions] = None):
    """Export document to PDF/A archival format."""
    opts = options.model_dump(exclude_none=True) if options else {}
    opts["pdfa_compliant"] = True
    job = await export_service.create_export_job(
        document_id=document_id,
        format="pdfa",
        options=opts,
    )
    return job


@router.post("/{document_id}/docx")
@limiter.limit(RATE_LIMIT_STANDARD)
async def export_to_docx(request: Request, document_id: str, options: Optional[ExportOptions] = None):
    """Export document to Word DOCX format."""
    job = await export_service.create_export_job(
        document_id=document_id,
        format="docx",
        options=options.model_dump(exclude_none=True) if options else {},
    )
    return job


@router.post("/{document_id}/pptx")
@limiter.limit(RATE_LIMIT_STANDARD)
async def export_to_pptx(request: Request, document_id: str, options: Optional[ExportOptions] = None):
    """Export document to PowerPoint format."""
    job = await export_service.create_export_job(
        document_id=document_id,
        format="pptx",
        options=options.model_dump(exclude_none=True) if options else {},
    )
    return job


@router.post("/{document_id}/epub")
@limiter.limit(RATE_LIMIT_STANDARD)
async def export_to_epub(request: Request, document_id: str, options: Optional[ExportOptions] = None):
    """Export document to ePub format."""
    job = await export_service.create_export_job(
        document_id=document_id,
        format="epub",
        options=options.model_dump(exclude_none=True) if options else {},
    )
    return job


@router.post("/{document_id}/latex")
@limiter.limit(RATE_LIMIT_STANDARD)
async def export_to_latex(request: Request, document_id: str, options: Optional[ExportOptions] = None):
    """Export document to LaTeX format."""
    job = await export_service.create_export_job(
        document_id=document_id,
        format="latex",
        options=options.model_dump(exclude_none=True) if options else {},
    )
    return job


@router.post("/{document_id}/markdown")
@limiter.limit(RATE_LIMIT_STANDARD)
async def export_to_markdown(request: Request, document_id: str, options: Optional[ExportOptions] = None):
    """Export document to Markdown format."""
    job = await export_service.create_export_job(
        document_id=document_id,
        format="markdown",
        options=options.model_dump(exclude_none=True) if options else {},
    )
    return job


@router.post("/{document_id}/html")
@limiter.limit(RATE_LIMIT_STANDARD)
async def export_to_html(request: Request, document_id: str, options: Optional[ExportOptions] = None):
    """Export document to HTML format."""
    job = await export_service.create_export_job(
        document_id=document_id,
        format="html",
        options=options.model_dump(exclude_none=True) if options else {},
    )
    return job


@router.post("/bulk")
@limiter.limit(RATE_LIMIT_STRICT)
async def bulk_export(request: Request, req: BulkExportRequest):
    """Export multiple documents as a ZIP file."""
    job = await export_service.bulk_export(
        document_ids=req.document_ids,
        format=req.format.value,
        options=req.options,
    )
    return job


@router.get("/jobs/{job_id}")
async def get_export_job(job_id: str):
    """Get export job status."""
    job = await export_service.get_export_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    return job


# Distribution endpoints


@router.post("/distribution/email-campaign")
@limiter.limit(RATE_LIMIT_STRICT)
async def email_campaign(request: Request, body: EmailCampaignRequest):
    """Send documents via bulk email campaign."""
    results = []
    for doc_id in body.document_ids:
        result = await distribution_service.send_email(
            document_id=doc_id,
            recipients=body.recipients,
            subject=body.subject,
            message=body.message,
        )
        results.append(result)

    return {
        "campaign_id": results[0]["job_id"] if results else None,
        "documents_sent": len(results),
        "recipients_count": len(body.recipients),
        "results": results,
    }


@router.post("/distribution/portal/{document_id}")
@limiter.limit(RATE_LIMIT_STANDARD)
async def publish_to_portal(request: Request, document_id: str, body: PortalPublishRequest):
    """Publish document to portal."""
    result = await distribution_service.publish_to_portal(
        document_id=document_id,
        portal_path=body.portal_path,
        options={
            "title": body.title,
            "description": body.description,
            "tags": body.tags,
            "public": body.public,
            "password": body.password,
            "expires_at": body.expires_at,
        },
    )
    # Never echo the password back in the response
    if isinstance(result, dict):
        result.pop("password", None)
        opts = result.get("options", {})
        if isinstance(opts, dict):
            opts.pop("password", None)
        result["password_protected"] = body.password is not None
    return result


@router.post("/distribution/embed/{document_id}", response_model=EmbedResponse)
@limiter.limit(RATE_LIMIT_STANDARD)
async def generate_embed(request: Request, document_id: str, body: EmbedGenerateRequest):
    """Generate embed code for a document."""
    result = await export_service.generate_embed_token(
        document_id=document_id,
        options={
            "width": body.width,
            "height": body.height,
            "allow_download": body.allow_download,
            "allow_print": body.allow_print,
            "show_toolbar": body.show_toolbar,
            "theme": body.theme,
        },
    )
    return EmbedResponse(**result)


@router.post("/distribution/slack")
@limiter.limit(RATE_LIMIT_STANDARD)
async def send_to_slack(request: Request, body: SlackMessageRequest):
    """Send document to Slack channel."""
    result = await distribution_service.send_to_slack(
        document_id=body.document_id,
        channel=body.channel,
        message=body.message,
    )
    return result


@router.post("/distribution/teams")
@limiter.limit(RATE_LIMIT_STANDARD)
async def send_to_teams(request: Request, req: TeamsMessageRequest):
    """Send document to Microsoft Teams."""
    result = await distribution_service.send_to_teams(
        document_id=req.document_id,
        webhook_url=req.webhook_url,
        title=req.title,
        message=req.message,
    )
    return result


@router.post("/distribution/webhook")
async def send_webhook(request: WebhookDeliveryRequest):
    """Deliver document via webhook."""
    result = await distribution_service.send_webhook(
        document_id=request.document_id,
        webhook_url=request.webhook_url,
        method=request.method,
        headers=request.headers,
    )
    return result


# ── Bulk export download ──


@router.get("/bulk/{job_id}/download")
async def download_bulk_export(job_id: str):
    """Download the result of a bulk export job."""
    job = await export_service.get_export_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Bulk export job not found")

    if job.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Export job is not completed (current status: {job.get('status')})",
        )

    download_url = job.get("download_url")
    if not download_url:
        raise HTTPException(status_code=404, detail="Export file not available")

    # Resolve the file path from the uploads directory
    from backend.app.services.config import get_settings

    file_path = get_settings().uploads_root / download_url.lstrip("/uploads/")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found on disk")

    def _iter_file():
        with open(file_path, "rb") as f:
            while chunk := f.read(64 * 1024):
                yield chunk

    filename = file_path.name
    return StreamingResponse(
        _iter_file(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Embed token management ──


@router.delete("/embed/{token_id}")
async def revoke_embed_token(token_id: str):
    """Revoke an embed token."""
    revoked = await export_service.revoke_embed_token(token_id)
    if not revoked:
        raise HTTPException(status_code=404, detail="Embed token not found")
    return {"detail": "Embed token revoked", "token_id": token_id}


@router.get("/{document_id}/embed/tokens")
async def list_embed_tokens(document_id: str):
    """List embed tokens for a document."""
    tokens = await export_service.list_embed_tokens(document_id)
    return {"document_id": document_id, "tokens": tokens}


# ── Print endpoints ──


@router.post("/{document_id}/print")
@limiter.limit(RATE_LIMIT_STANDARD)
async def print_document(request: Request, document_id: str, body: PrintRequest):
    """Print a document."""
    job = await export_service.print_document(
        document_id=document_id,
        printer_id=body.printer_id,
        copies=body.copies,
        options=body.options,
    )
    return job


# ── Job management ──


@router.post("/jobs/{job_id}/cancel")
async def cancel_export_job(job_id: str):
    """Cancel an export job."""
    job = await export_service.cancel_export_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")

    if job.get("status") in ("completed", "failed"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status '{job.get('status')}'",
        )

    return job
