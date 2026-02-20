"""API routes for Document Q&A Chat."""
from __future__ import annotations

import logging
import threading
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, Request, HTTPException

logger = logging.getLogger("neura.api.docqa")

from backend.app.services.security import require_api_key
from backend.app.services.docqa.service import DocumentQAService
from backend.app.schemas.docqa import AskRequest, FeedbackRequest, RegenerateRequest

router = APIRouter(dependencies=[Depends(require_api_key)])


class CreateSessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class AddDocumentRequest(BaseModel):
    # Limit content to 500KB to prevent memory exhaustion
    # For larger documents, use file upload with chunked processing
    name: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10, max_length=500 * 1024)
    page_count: Optional[int] = None


_lock = threading.Lock()
_docqa_service: DocumentQAService | None = None


def get_service() -> DocumentQAService:
    """Return a singleton DocumentQAService instance."""
    global _docqa_service
    if _docqa_service is None:
        with _lock:
            if _docqa_service is None:
                _docqa_service = DocumentQAService()
    return _docqa_service


@router.post("/sessions")
async def create_session(
    payload: CreateSessionRequest,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Create a new Q&A session."""
    correlation_id = getattr(request.state, "correlation_id", None)
    session = svc.create_session(
        name=payload.name,
        correlation_id=correlation_id,
    )
    return {"status": "ok", "session": session.model_dump(mode="json"), "correlation_id": correlation_id}


@router.get("/sessions")
async def list_sessions(
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: DocumentQAService = Depends(get_service),
):
    """List all Q&A sessions."""
    correlation_id = getattr(request.state, "correlation_id", None)
    sessions = svc.list_sessions()
    page = sessions[offset:offset + limit]
    return {
        "status": "ok",
        "sessions": [s.model_dump(mode="json") for s in page],
        "total": len(sessions),
        "correlation_id": correlation_id,
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Get a Q&A session by ID."""
    correlation_id = getattr(request.state, "correlation_id", None)
    session = svc.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"status": "ok", "session": session.model_dump(mode="json"), "correlation_id": correlation_id}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Delete a Q&A session."""
    correlation_id = getattr(request.state, "correlation_id", None)
    success = svc.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"status": "ok", "deleted": True, "correlation_id": correlation_id}


@router.post("/sessions/{session_id}/documents")
async def add_document(
    session_id: str,
    payload: AddDocumentRequest,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Add a document to a Q&A session."""
    correlation_id = getattr(request.state, "correlation_id", None)
    document = svc.add_document(
        session_id=session_id,
        name=payload.name,
        content=payload.content,
        page_count=payload.page_count,
        correlation_id=correlation_id,
    )

    if not document:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"status": "ok", "document": document.model_dump(mode="json"), "correlation_id": correlation_id}


@router.delete("/sessions/{session_id}/documents/{document_id}")
async def remove_document(
    session_id: str,
    document_id: str,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Remove a document from a session."""
    correlation_id = getattr(request.state, "correlation_id", None)
    success = svc.remove_document(session_id, document_id)

    if not success:
        raise HTTPException(status_code=404, detail="Session or document not found")

    return {"status": "ok", "removed": True, "correlation_id": correlation_id}


@router.post("/sessions/{session_id}/ask")
async def ask_question(
    session_id: str,
    payload: AskRequest,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Ask a question about the documents in a session."""
    correlation_id = getattr(request.state, "correlation_id", None)

    session = svc.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    response = svc.ask(session_id, payload, correlation_id)

    if not response:
        raise HTTPException(status_code=500, detail="Failed to process question")

    return {
        "status": "ok",
        "response": response.model_dump(mode="json"),
        "correlation_id": correlation_id,
    }


@router.post("/sessions/{session_id}/messages/{message_id}/feedback")
async def submit_feedback(
    session_id: str,
    message_id: str,
    payload: FeedbackRequest,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Submit feedback for a chat message."""
    correlation_id = getattr(request.state, "correlation_id", None)

    session = svc.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    message = svc.submit_feedback(
        session_id,
        message_id,
        payload,
        correlation_id,
    )

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return {
        "status": "ok",
        "message": message.model_dump(mode="json"),
        "correlation_id": correlation_id,
    }


@router.post("/sessions/{session_id}/messages/{message_id}/regenerate")
async def regenerate_response(
    session_id: str,
    message_id: str,
    payload: RegenerateRequest,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Regenerate a response for a message."""
    correlation_id = getattr(request.state, "correlation_id", None)

    session = svc.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        response = svc.regenerate_response(
            session_id,
            message_id,
            payload,
            correlation_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail="Document Q&A operation failed") from exc
    except Exception as exc:
        logger.error("Response regeneration failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Response regeneration failed.",
        ) from exc

    if not response:
        raise HTTPException(status_code=404, detail="Message not found")

    return {
        "status": "ok",
        "response": response.model_dump(mode="json"),
        "correlation_id": correlation_id,
    }


@router.get("/sessions/{session_id}/history")
async def get_chat_history(
    session_id: str,
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    svc: DocumentQAService = Depends(get_service),
):
    """Get chat history for a session."""
    correlation_id = getattr(request.state, "correlation_id", None)

    session = svc.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = svc.get_chat_history(session_id, limit)

    return {
        "status": "ok",
        "messages": [m.model_dump(mode="json") for m in messages],
        "count": len(messages),
        "correlation_id": correlation_id,
    }


@router.delete("/sessions/{session_id}/history")
async def clear_chat_history(
    session_id: str,
    request: Request,
    svc: DocumentQAService = Depends(get_service),
):
    """Clear chat history for a session."""
    correlation_id = getattr(request.state, "correlation_id", None)

    success = svc.clear_history(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"status": "ok", "cleared": True, "correlation_id": correlation_id}
