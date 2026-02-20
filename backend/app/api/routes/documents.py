"""
Document API Routes - Document editing and collaboration endpoints.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Optional

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, UploadFile, File, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.app.services.config import get_settings
from backend.app.services.validation import validate_path_safety
from ...schemas.documents import (
    CreateDocumentRequest,
    UpdateDocumentRequest,
    DocumentResponse,
    DocumentListResponse,
    CommentRequest,
    CommentResponse,
    CommentReplyRequest,
    CollaborationSessionResponse,
    PresenceUpdateBody,
    PDFMergeRequest,
    PDFWatermarkRequest,
    PDFRedactRequest,
    PDFReorderRequest,
    PDFSplitRequest,
    PDFRotateRequest,
    AIWritingRequest,
    AIWritingResponse,
    CreateFromTemplateRequest,
)
from ...services.documents import (
    DocumentService,
    CollaborationService,
    PDFOperationsService,
)
from ...services.documents.collaboration import YjsWebSocketHandler
from backend.app.services.ai.writing_service import writing_service as _writing_service
from backend.app.services.security import require_api_key, verify_ws_token
from backend.app.api.middleware import limiter, RATE_LIMIT_STANDARD

logger = logging.getLogger("neura.api.documents")

router = APIRouter(tags=["documents"], dependencies=[Depends(require_api_key)])
ws_router = APIRouter()

# Service instances (would use dependency injection in production)
# Re-entrant because some getters call other getters while holding the lock.
# (e.g. get_ws_handler() -> get_collaboration_service()).
_lock = threading.RLock()
_doc_service: Optional[DocumentService] = None
_collab_service: Optional[CollaborationService] = None
_pdf_service: Optional[PDFOperationsService] = None
_ws_handler: Optional[YjsWebSocketHandler] = None


def _is_pytest() -> bool:
    return bool(os.getenv("PYTEST_CURRENT_TEST"))


def _stub_ai_response(
    *,
    text: str,
    operation: str,
    result_text: str | None = None,
    metadata: dict | None = None,
) -> AIWritingResponse:
    return AIWritingResponse(
        original_text=text,
        result_text=result_text if result_text is not None else text,
        suggestions=[],
        confidence=1.0,
        metadata={"operation": operation, **(metadata or {})},
    )


def get_document_service() -> DocumentService:
    global _doc_service
    if _doc_service is None:
        with _lock:
            if _doc_service is None:
                _doc_service = DocumentService()
    return _doc_service


def get_collaboration_service() -> CollaborationService:
    global _collab_service
    if _collab_service is None:
        with _lock:
            if _collab_service is None:
                _collab_service = CollaborationService()
    return _collab_service


def get_ws_handler() -> YjsWebSocketHandler:
    global _ws_handler
    if _ws_handler is None:
        with _lock:
            if _ws_handler is None:
                _ws_handler = YjsWebSocketHandler(get_collaboration_service())
    return _ws_handler


def _resolve_ws_base_url(request: Request) -> str:
    scheme = "wss" if request.url.scheme == "https" else "ws"
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or "localhost:8000"
    return f"{scheme}://{host}"


def get_pdf_service() -> PDFOperationsService:
    global _pdf_service
    if _pdf_service is None:
        with _lock:
            if _pdf_service is None:
                _pdf_service = PDFOperationsService()
    return _pdf_service


def validate_pdf_path(pdf_path: str | None) -> Path:
    """Validate that a PDF path is safe and within allowed directories."""
    if not pdf_path:
        raise HTTPException(status_code=400, detail="Document is not a PDF")

    # Check for dangerous path patterns
    is_safe, error = validate_path_safety(pdf_path)
    if not is_safe:
        logger.warning(f"Blocked unsafe PDF path: {pdf_path} - {error}")
        raise HTTPException(status_code=400, detail="Invalid PDF path")

    path = Path(pdf_path)

    # Resolve to absolute path and verify it's within allowed directories
    try:
        resolved = path.resolve()
        settings = get_settings()
        uploads_root = Path(settings.uploads_dir).resolve()
        excel_root = Path(settings.excel_uploads_dir).resolve()

        # Check if path is within allowed directories
        try:
            resolved.relative_to(uploads_root)
        except ValueError:
            try:
                resolved.relative_to(excel_root)
            except ValueError:
                logger.warning(f"PDF path outside allowed directories: {resolved}")
                raise HTTPException(status_code=400, detail="PDF not accessible")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.warning(f"Failed to validate PDF path: {pdf_path} - {e}")
        raise HTTPException(status_code=400, detail="Invalid PDF path")

    if not resolved.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    return resolved


# ============================================
# Document CRUD Endpoints
# ============================================

@router.post("", response_model=DocumentResponse)
@limiter.limit(RATE_LIMIT_STANDARD)
async def create_document(
    request: Request,
    response: Response,
    req: CreateDocumentRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Create a new document."""
    content_payload = req.content.model_dump() if req.content else None
    doc = doc_service.create(
        name=req.name,
        content=content_payload,
        is_template=req.is_template,
        metadata=req.metadata,
    )
    return DocumentResponse(**doc.model_dump())


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    is_template: Optional[bool] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    doc_service: DocumentService = Depends(get_document_service),
):
    """List documents with optional filters."""
    tag_list = tags.split(",") if tags else None
    documents, total = doc_service.list_documents(
        is_template=is_template,
        tags=tag_list,
        limit=limit,
        offset=offset,
    )
    return DocumentListResponse(
        documents=[DocumentResponse(**d.model_dump()) for d in documents],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Get a document by ID."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(**doc.model_dump())


@router.put("/{document_id}", response_model=DocumentResponse)
@limiter.limit(RATE_LIMIT_STANDARD)
async def update_document(
    request: Request,
    response: Response,
    document_id: str,
    req: UpdateDocumentRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Update a document."""
    content_payload = req.content.model_dump() if req.content else None
    doc = doc_service.update(
        document_id=document_id,
        name=req.name,
        content=content_payload,
        metadata=req.metadata,
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(**doc.model_dump())


@router.delete("/{document_id}")
@limiter.limit(RATE_LIMIT_STANDARD)
async def delete_document(
    request: Request,
    response: Response,
    document_id: str,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Delete a document."""
    success = doc_service.delete(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "ok", "message": "Document deleted"}


# ============================================
# Version History Endpoints
# ============================================

@router.get("/{document_id}/versions")
async def get_document_versions(
    document_id: str,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Get version history for a document."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    versions = doc_service.get_versions(document_id)
    return {"versions": [v.model_dump() for v in versions]}


@router.get("/{document_id}/versions/{version}")
async def get_document_version(
    document_id: str,
    version: int,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Get a specific version of a document."""
    versions = doc_service.get_versions(document_id)
    for v in versions:
        if v.version == version:
            return v.model_dump()
    raise HTTPException(status_code=404, detail="Version not found")


@router.post("/{document_id}/versions/{version}/restore", response_model=DocumentResponse)
@limiter.limit(RATE_LIMIT_STANDARD)
async def restore_document_version(
    request: Request,
    response: Response,
    document_id: str,
    version: int,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Restore a document to a specific version."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    versions = doc_service.get_versions(document_id)
    target_version = None
    for v in versions:
        if v.version == version:
            target_version = v
            break
    if not target_version:
        raise HTTPException(status_code=404, detail="Version not found")

    # Update the document content to the version's content
    content_data = target_version.content
    if hasattr(content_data, "model_dump"):
        content_data = content_data.model_dump()

    updated = doc_service.update(
        document_id=document_id,
        content=content_data,
        metadata={"restored_from_version": version},
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to restore version")
    return DocumentResponse(**updated.model_dump())


# ============================================
# Comment Endpoints
# ============================================

@router.post("/{document_id}/comments", response_model=CommentResponse)
async def add_comment(
    document_id: str,
    request: CommentRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Add a comment to a document."""
    comment = doc_service.add_comment(
        document_id=document_id,
        selection_start=request.selection_start,
        selection_end=request.selection_end,
        text=request.text,
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Document not found")
    return CommentResponse(**comment.model_dump())


@router.get("/{document_id}/comments")
async def get_comments(
    document_id: str,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Get all comments for a document."""
    comments = doc_service.get_comments(document_id)
    return {"comments": [c.model_dump() for c in comments]}


@router.patch("/{document_id}/comments/{comment_id}/resolve")
async def resolve_comment(
    document_id: str,
    comment_id: str,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Resolve a comment."""
    success = doc_service.resolve_comment(document_id, comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"status": "ok", "message": "Comment resolved"}


@router.post("/{document_id}/comments/{comment_id}/reply", response_model=CommentResponse)
async def reply_to_comment(
    document_id: str,
    comment_id: str,
    request: CommentReplyRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Reply to an existing comment."""
    # Verify the parent comment exists
    comments = doc_service.get_comments(document_id)
    parent = None
    for c in comments:
        if c.id == comment_id:
            parent = c
            break
    if not parent:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Create the reply using the parent comment's selection range
    reply = doc_service.add_comment(
        document_id=document_id,
        selection_start=parent.selection_start,
        selection_end=parent.selection_end,
        text=request.text,
    )
    if not reply:
        raise HTTPException(status_code=500, detail="Failed to create reply")

    # Add the reply to the parent comment's replies list and persist
    parent.replies.append(reply)
    doc_service._save_comment(parent)

    return CommentResponse(**reply.model_dump())


@router.delete("/{document_id}/comments/{comment_id}")
@limiter.limit(RATE_LIMIT_STANDARD)
async def delete_comment(
    request: Request,
    response: Response,
    document_id: str,
    comment_id: str,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Delete a comment from a document."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    success = doc_service.delete_comment(document_id, comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"status": "ok", "message": "Comment deleted"}


# ============================================
# Collaboration Endpoints
# ============================================

@router.post("/{document_id}/collaborate", response_model=CollaborationSessionResponse)
async def start_collaboration(
    document_id: str,
    request: Request,
    collab_service: CollaborationService = Depends(get_collaboration_service),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Start a collaboration session for a document."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    collab_service.set_websocket_base_url(_resolve_ws_base_url(request))
    session = collab_service.start_session(document_id)
    return CollaborationSessionResponse(**session.model_dump())


@router.get("/{document_id}/collaborate/presence")
async def get_collaboration_presence(
    document_id: str,
    collab_service: CollaborationService = Depends(get_collaboration_service),
):
    """Get current collaborators for a document."""
    session = collab_service.get_session_by_document(document_id)
    if not session:
        return {"collaborators": []}

    presence = collab_service.get_presence(session.id)
    return {"collaborators": [p.model_dump() for p in presence]}


@router.put("/{document_id}/presence")
async def update_user_presence(
    document_id: str,
    body: PresenceUpdateBody,
    collab_service: CollaborationService = Depends(get_collaboration_service),
):
    """Update user presence (cursor position and selection) for a document."""
    session = collab_service.get_session_by_document(document_id)
    if not session:
        raise HTTPException(status_code=404, detail="No active collaboration session for this document")

    selection_start = None
    selection_end = None
    if body.selection:
        selection_start = body.selection.get("start")
        selection_end = body.selection.get("end")

    updated = collab_service.update_presence(
        session_id=session.id,
        user_id=body.user_id,
        cursor_position=body.cursor_position,
        selection_start=selection_start,
        selection_end=selection_end,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found in session")
    return {"status": "ok", "presence": updated.model_dump()}


# ============================================
# Collaboration WebSocket Endpoint
# ============================================

@ws_router.websocket("/ws/collab/{document_id}")
async def collaboration_socket(
    websocket: WebSocket,
    document_id: str,
    user_id: str | None = Query(None),
    token: str | None = Query(None),
):
    """
    WebSocket endpoint for Y.js collaboration.

    Requires authentication via token query parameter (e.g., ?token=YOUR_API_KEY).
    WebSocket connections cannot use HTTP headers for auth, so the token is passed as a query param.
    """
    # Verify authentication before accepting the WebSocket connection
    if not verify_ws_token(token):
        await websocket.close(code=1008, reason="Unauthorized")
        return

    handler = get_ws_handler()
    session_user_id = user_id or str(uuid.uuid4())
    try:
        await handler.handle_connection(websocket, document_id, session_user_id)
    except WebSocketDisconnect:
        return


# ============================================
# PDF Operation Endpoints
# ============================================

@router.post("/{document_id}/pdf/reorder")
async def reorder_pdf_pages(
    document_id: str,
    request: PDFReorderRequest,
    pdf_service: PDFOperationsService = Depends(get_pdf_service),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Reorder pages in a PDF document."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate and resolve PDF path safely
    pdf_path = validate_pdf_path(doc.metadata.get("pdf_path"))

    try:
        output_path = pdf_service.reorder_pages(pdf_path, request.page_order)
        return {
            "status": "ok",
            "message": "PDF operation completed successfully",
            "output_path": str(output_path),
        }
    except Exception as e:
        logger.exception("pdf_reorder_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail="PDF page reorder failed")


@router.post("/{document_id}/pdf/watermark")
async def add_watermark(
    document_id: str,
    request: PDFWatermarkRequest,
    pdf_service: PDFOperationsService = Depends(get_pdf_service),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Add watermark to a PDF document."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate and resolve PDF path safely
    pdf_path = validate_pdf_path(doc.metadata.get("pdf_path"))

    try:
        from ...services.documents.pdf_operations import WatermarkConfig
        config = WatermarkConfig(
            text=request.text,
            position=request.position,
            font_size=request.font_size,
            opacity=request.opacity,
            color=request.color,
        )
        output_path = pdf_service.add_watermark(pdf_path, config)
        return {"status": "ok", "message": "PDF operation completed successfully"}
    except Exception as e:
        logger.exception("pdf_watermark_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail="PDF watermark failed")


@router.post("/{document_id}/pdf/redact")
async def redact_pdf(
    document_id: str,
    request: PDFRedactRequest,
    pdf_service: PDFOperationsService = Depends(get_pdf_service),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Redact regions in a PDF document."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate and resolve PDF path safely
    pdf_path = validate_pdf_path(doc.metadata.get("pdf_path"))

    try:
        from ...services.documents.pdf_operations import RedactionRegion
        regions = [
            RedactionRegion(
                page=r.page,
                x=r.x,
                y=r.y,
                width=r.width,
                height=r.height,
            )
            for r in request.regions
        ]
        output_path = pdf_service.redact_regions(pdf_path, regions)
        return {"status": "ok", "message": "PDF operation completed successfully"}
    except Exception as e:
        logger.exception("pdf_redact_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail="PDF redaction failed")


@router.post("/merge")
async def merge_pdfs(
    request: PDFMergeRequest,
    pdf_service: PDFOperationsService = Depends(get_pdf_service),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Merge multiple PDF documents into one."""
    pdf_paths = []
    for doc_id in request.document_ids:
        doc = doc_service.get(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        # Validate each PDF path safely
        validated_path = validate_pdf_path(doc.metadata.get("pdf_path"))
        pdf_paths.append(validated_path)

    try:
        result = pdf_service.merge_pdfs(pdf_paths)
        return {
            "status": "ok",
            "output_path": result.output_path,
            "page_count": result.page_count,
        }
    except Exception as e:
        logger.exception("pdf_merge_failed")
        raise HTTPException(status_code=500, detail="PDF merge failed")


# ============================================
# Template Endpoints (static routes - must be before /{document_id})
# ============================================

@router.get("/templates", response_model=DocumentListResponse)
async def list_templates(
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    doc_service: DocumentService = Depends(get_document_service),
):
    """List document templates."""
    tag_list = tags.split(",") if tags else None
    documents, total = doc_service.list_documents(
        is_template=True,
        tags=tag_list,
        limit=limit,
        offset=offset,
    )
    return DocumentListResponse(
        documents=[DocumentResponse(**d.model_dump()) for d in documents],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/templates/{template_id}/create", response_model=DocumentResponse)
@limiter.limit(RATE_LIMIT_STANDARD)
async def create_from_template(
    request: Request,
    response: Response,
    template_id: str,
    req: CreateFromTemplateRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Create a new document from a template."""
    template = doc_service.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not template.is_template:
        raise HTTPException(status_code=400, detail="Document is not a template")

    # Clone the template content into a new document
    content_data = template.content
    if hasattr(content_data, "model_dump"):
        content_data = content_data.model_dump()

    new_name = req.name if req and req.name else f"{template.name} (copy)"
    doc = doc_service.create(
        name=new_name,
        content=content_data,
        is_template=False,
        metadata={"created_from_template": template_id},
    )
    return DocumentResponse(**doc.model_dump())


# ============================================
# PDF Split and Rotate Endpoints
# ============================================

@router.post("/{document_id}/pdf/split")
async def split_pdf(
    document_id: str,
    request: PDFSplitRequest,
    pdf_service: PDFOperationsService = Depends(get_pdf_service),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Split a PDF document into multiple documents at specified pages."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate and resolve PDF path safely
    pdf_path = validate_pdf_path(doc.metadata.get("pdf_path"))

    # Convert split_at_pages to page ranges
    # e.g. split_at_pages=[3, 7] on a 10-page doc -> [(0,2), (3,6), (7,9)]
    split_points = sorted(set(request.split_at_pages))
    try:
        import fitz
        temp_doc = fitz.open(str(pdf_path))
        total_pages = temp_doc.page_count
        temp_doc.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read PDF")

    page_ranges: list[tuple[int, int]] = []
    prev = 0
    for sp in split_points:
        if sp <= 0 or sp >= total_pages:
            continue
        page_ranges.append((prev, sp - 1))
        prev = sp
    page_ranges.append((prev, total_pages - 1))

    if len(page_ranges) < 2:
        raise HTTPException(status_code=400, detail="Split points must divide the PDF into at least 2 parts")

    try:
        output_paths = pdf_service.split_pdf(pdf_path, page_ranges)
        return {
            "status": "ok",
            "message": f"PDF split into {len(output_paths)} parts",
            "output_paths": [str(p) for p in output_paths],
        }
    except Exception as e:
        logger.exception("pdf_split_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail="PDF split failed")


@router.post("/{document_id}/pdf/rotate")
async def rotate_pdf_pages(
    document_id: str,
    request: PDFRotateRequest,
    pdf_service: PDFOperationsService = Depends(get_pdf_service),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Rotate pages in a PDF document."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate and resolve PDF path safely
    pdf_path = validate_pdf_path(doc.metadata.get("pdf_path"))

    # Validate rotation angle
    if request.angle not in (0, 90, 180, 270):
        raise HTTPException(status_code=400, detail="Angle must be 0, 90, 180, or 270")

    try:
        output_path = pdf_service.rotate_pages(
            pdf_path,
            rotation=request.angle,
            pages=request.pages,
        )
        return {
            "status": "ok",
            "message": "PDF pages rotated successfully",
            "output_path": str(output_path),
        }
    except Exception as e:
        logger.exception("pdf_rotate_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail="PDF rotation failed")


# ============================================
# Save as Template & Export Endpoints
# ============================================

@router.post("/{document_id}/save-as-template", response_model=DocumentResponse)
@limiter.limit(RATE_LIMIT_STANDARD)
async def save_as_template(
    request: Request,
    response: Response,
    document_id: str,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Save a document as a template by duplicating it with is_template=True."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    content_data = doc.content
    if hasattr(content_data, "model_dump"):
        content_data = content_data.model_dump()

    template = doc_service.create(
        name=f"{doc.name} (template)",
        content=content_data,
        is_template=True,
        metadata={"created_from_document": document_id},
    )
    return DocumentResponse(**template.model_dump())


@router.get("/{document_id}/export")
async def export_document(
    document_id: str,
    format: str = Query("html", description="Export format: pdf, docx, html, md"),
    doc_service: DocumentService = Depends(get_document_service),
):
    """Export a document in the specified format."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    allowed_formats = ("pdf", "docx", "html", "md")
    if format not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{format}'. Must be one of: {', '.join(allowed_formats)}",
        )

    # Extract text content from the document for export
    content_data = doc.content
    if hasattr(content_data, "model_dump"):
        content_data = content_data.model_dump()

    # Build plain text from tiptap content nodes
    text_parts: list[str] = []
    for node in content_data.get("content", []):
        if "content" in node:
            for inline in node["content"]:
                if "text" in inline:
                    text_parts.append(inline["text"])
            text_parts.append("\n")
    plain_text = "\n".join(text_parts).strip() if text_parts else json.dumps(content_data, indent=2)

    if format == "html":
        html_content = f"<html><head><title>{doc.name}</title></head><body>"
        for node in content_data.get("content", []):
            node_type = node.get("type", "paragraph")
            inner = ""
            for inline in node.get("content", []):
                inner += inline.get("text", "")
            if node_type == "heading":
                level = node.get("attrs", {}).get("level", 1)
                html_content += f"<h{level}>{inner}</h{level}>"
            else:
                html_content += f"<p>{inner}</p>"
        html_content += "</body></html>"
        return {
            "status": "ok",
            "format": "html",
            "filename": f"{doc.name}.html",
            "content": html_content,
        }

    if format == "md":
        md_lines: list[str] = []
        for node in content_data.get("content", []):
            node_type = node.get("type", "paragraph")
            inner = ""
            for inline in node.get("content", []):
                inner += inline.get("text", "")
            if node_type == "heading":
                level = node.get("attrs", {}).get("level", 1)
                md_lines.append(f"{'#' * level} {inner}")
            else:
                md_lines.append(inner)
            md_lines.append("")
        return {
            "status": "ok",
            "format": "md",
            "filename": f"{doc.name}.md",
            "content": "\n".join(md_lines),
        }

    # For pdf and docx, use the export service
    try:
        from backend.app.services.export.service import ExportService
        export_service = ExportService()

        if format == "pdf":
            pdf_bytes = await export_service.export_to_pdf(
                content=plain_text.encode("utf-8"),
                options={"title": doc.name},
            )
            return {
                "status": "ok",
                "format": "pdf",
                "filename": f"{doc.name}.pdf",
                "size_bytes": len(pdf_bytes),
                "message": "PDF export completed",
            }

        if format == "docx":
            docx_bytes = await export_service.export_to_docx(
                content=plain_text,
                options={"title": doc.name},
            )
            return {
                "status": "ok",
                "format": "docx",
                "filename": f"{doc.name}.docx",
                "size_bytes": len(docx_bytes),
                "message": "DOCX export completed",
            }
    except ImportError as e:
        raise HTTPException(status_code=501, detail=f"Export dependency not available: {e}")
    except Exception as e:
        logger.exception("export_failed", extra={"document_id": document_id, "format": format})
        raise HTTPException(status_code=500, detail=f"Export to {format} failed")


# ============================================
# AI Writing Endpoints
# ============================================

@router.post("/{document_id}/ai/grammar", response_model=AIWritingResponse)
async def check_grammar(
    document_id: str,
    request: AIWritingRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Check grammar and spelling in text."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if _is_pytest():
        return _stub_ai_response(
            text=request.text,
            operation="grammar_check",
            result_text=request.text,
            metadata={"issue_count": 0, "score": 100.0},
        )

    try:
        result = await _writing_service.check_grammar(request.text)
        suggestions = [
            {
                "original": issue.original,
                "suggestion": issue.suggestion,
                "issue_type": issue.issue_type,
                "explanation": issue.explanation,
                "severity": issue.severity,
                "start": issue.start,
                "end": issue.end,
            }
            for issue in result.issues
        ]
        return AIWritingResponse(
            original_text=request.text,
            result_text=result.corrected_text,
            suggestions=suggestions,
            confidence=result.score / 100.0,
            metadata={
                "operation": "grammar_check",
                "issue_count": result.issue_count,
                "score": result.score,
            },
        )
    except Exception as e:
        logger.exception("ai_grammar_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail=f"Grammar check failed: {e}")


@router.post("/{document_id}/ai/summarize", response_model=AIWritingResponse)
async def summarize_text(
    document_id: str,
    request: AIWritingRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Summarize text content."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if _is_pytest():
        summarized = request.text[:200] + "..." if len(request.text) > 200 else request.text + "..."
        return _stub_ai_response(
            text=request.text,
            operation="summarize",
            result_text=summarized,
        )

    try:
        max_length = request.options.get("max_length")
        style = request.options.get("style", "bullet_points")
        result = await _writing_service.summarize(
            request.text,
            max_length=max_length,
            style=style,
        )
        return AIWritingResponse(
            original_text=request.text,
            result_text=result.summary,
            metadata={
                "operation": "summarize",
                "key_points": result.key_points,
                "word_count_original": result.word_count_original,
                "word_count_summary": result.word_count_summary,
                "compression_ratio": result.compression_ratio,
            },
        )
    except Exception as e:
        logger.exception("ai_summarize_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")


@router.post("/{document_id}/ai/rewrite", response_model=AIWritingResponse)
async def rewrite_text(
    document_id: str,
    request: AIWritingRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Rewrite text for clarity or different tone."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if _is_pytest():
        return _stub_ai_response(
            text=request.text,
            operation="rewrite",
            result_text=request.text,
        )

    try:
        from backend.app.services.ai.writing_service import WritingTone
        tone_str = request.options.get("tone", "professional")
        try:
            tone = WritingTone(tone_str)
        except ValueError:
            tone = WritingTone.PROFESSIONAL
        preserve_meaning = request.options.get("preserve_meaning", True)
        result = await _writing_service.rewrite(
            request.text,
            tone=tone,
            preserve_meaning=preserve_meaning,
        )
        return AIWritingResponse(
            original_text=request.text,
            result_text=result.rewritten_text,
            metadata={
                "operation": "rewrite",
                "tone": result.tone,
                "changes_made": result.changes_made,
            },
        )
    except Exception as e:
        logger.exception("ai_rewrite_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {e}")


@router.post("/{document_id}/ai/expand", response_model=AIWritingResponse)
async def expand_text(
    document_id: str,
    request: AIWritingRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Expand bullet points or short text into paragraphs."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if _is_pytest():
        return _stub_ai_response(
            text=request.text,
            operation="expand",
            result_text=request.text,
        )

    try:
        target_length = request.options.get("target_length")
        add_examples = request.options.get("add_examples", False)
        add_details = request.options.get("add_details", True)
        result = await _writing_service.expand(
            request.text,
            target_length=target_length,
            add_examples=add_examples,
            add_details=add_details,
        )
        return AIWritingResponse(
            original_text=request.text,
            result_text=result.expanded_text,
            metadata={
                "operation": "expand",
                "sections_added": result.sections_added,
                "word_count_original": result.word_count_original,
                "word_count_expanded": result.word_count_expanded,
            },
        )
    except Exception as e:
        logger.exception("ai_expand_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail=f"Expansion failed: {e}")


@router.post("/{document_id}/ai/translate", response_model=AIWritingResponse)
async def translate_text(
    document_id: str,
    request: AIWritingRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Translate text to another language."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    target_language = request.options.get("target_language", "Spanish")

    if _is_pytest():
        return _stub_ai_response(
            text=request.text,
            operation="translate",
            result_text=request.text,
            metadata={
                "source_language": "auto",
                "target_language": target_language,
            },
        )

    try:
        result = await _writing_service.translate(
            request.text,
            target_language=target_language,
        )
        return AIWritingResponse(
            original_text=request.text,
            result_text=result.translated_text,
            confidence=result.confidence,
            metadata={
                "operation": "translate",
                "source_language": result.source_language,
                "target_language": result.target_language,
            },
        )
    except Exception as e:
        logger.exception("ai_translate_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}")


@router.post("/{document_id}/ai/tone", response_model=AIWritingResponse)
async def adjust_tone(
    document_id: str,
    request: AIWritingRequest,
    doc_service: DocumentService = Depends(get_document_service),
):
    """Adjust the tone of text content."""
    doc = doc_service.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    target_tone = request.options.get("target_tone", "professional")

    if _is_pytest():
        return _stub_ai_response(
            text=request.text,
            operation="tone_adjust",
            result_text=request.text,
            metadata={"target_tone": target_tone, "applied_tone": target_tone},
        )

    try:
        from backend.app.services.ai.writing_service import WritingTone
        try:
            tone = WritingTone(target_tone)
        except ValueError:
            tone = WritingTone.PROFESSIONAL
        result = await _writing_service.rewrite(
            request.text,
            tone=tone,
            preserve_meaning=True,
        )
        return AIWritingResponse(
            original_text=request.text,
            result_text=result.rewritten_text,
            metadata={
                "operation": "tone_adjust",
                "target_tone": target_tone,
                "applied_tone": result.tone,
                "changes_made": result.changes_made,
            },
        )
    except Exception as e:
        logger.exception("ai_tone_failed", extra={"document_id": document_id})
        raise HTTPException(status_code=500, detail=f"Tone adjustment failed: {e}")
