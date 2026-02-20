"""
Document Schemas - Request/Response models for document operations.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================
# Document CRUD Schemas
# ============================================

class DocumentContent(BaseModel):
    """TipTap document content structure."""

    type: str = "doc"
    content: list[dict[str, Any]] = []


class CreateDocumentRequest(BaseModel):
    """Request to create a new document."""

    name: str = Field(..., min_length=1, max_length=255)
    content: Optional[DocumentContent] = None
    is_template: bool = False
    tags: list[str] = []
    metadata: dict[str, Any] = {}


class UpdateDocumentRequest(BaseModel):
    """Request to update a document."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[DocumentContent] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None
    track_changes_enabled: Optional[bool] = None


class DocumentResponse(BaseModel):
    """Document response model."""

    id: str
    name: str
    content: DocumentContent
    content_type: str
    version: int
    created_at: str
    updated_at: str
    owner_id: Optional[str]
    is_template: bool
    track_changes_enabled: bool
    collaboration_enabled: bool
    tags: list[str]
    metadata: dict[str, Any]


class DocumentListResponse(BaseModel):
    """List of documents response."""

    documents: list[DocumentResponse]
    total: int
    offset: int
    limit: int


class DocumentVersionResponse(BaseModel):
    """Document version response."""

    id: str
    document_id: str
    version: int
    content: DocumentContent
    created_at: str
    created_by: Optional[str]
    change_summary: Optional[str]


# ============================================
# Comment Schemas
# ============================================

class CommentRequest(BaseModel):
    """Request to add a comment."""

    selection_start: int = Field(..., ge=0)
    selection_end: int = Field(..., ge=0)
    text: str = Field(..., min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    """Comment response model."""

    id: str
    document_id: str
    selection_start: int
    selection_end: int
    text: str
    author_id: Optional[str]
    author_name: Optional[str]
    created_at: str
    resolved: bool
    replies: list["CommentResponse"] = []


class ResolveCommentRequest(BaseModel):
    """Request to resolve a comment."""

    resolved: bool = True


# ============================================
# Collaboration Schemas
# ============================================

class StartCollaborationRequest(BaseModel):
    """Request to start collaboration session."""

    user_name: Optional[str] = None


class CollaborationSessionResponse(BaseModel):
    """Collaboration session response."""

    id: str
    document_id: str
    websocket_url: str
    created_at: str
    participants: list[str]
    is_active: bool


class PresenceUpdateRequest(BaseModel):
    """Request to update presence."""

    cursor_position: Optional[int] = None
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None


class CollaboratorPresenceResponse(BaseModel):
    """Collaborator presence response."""

    user_id: str
    user_name: str
    cursor_position: Optional[int]
    selection_start: Optional[int]
    selection_end: Optional[int]
    color: str
    last_seen: str


# ============================================
# PDF Operation Schemas
# ============================================

class PDFReorderRequest(BaseModel):
    """Request to reorder PDF pages."""

    page_order: list[int] = Field(..., min_length=1)


class PDFWatermarkRequest(BaseModel):
    """Request to add watermark to PDF."""

    text: str = Field(..., min_length=1, max_length=100)
    position: str = Field(default="center", pattern="^(center|diagonal|top|bottom)$")
    font_size: int = Field(default=48, ge=8, le=200)
    opacity: float = Field(default=0.3, ge=0.1, le=1.0)
    color: str = Field(default="#808080", pattern="^#[0-9A-Fa-f]{6}$")


class RedactionRegion(BaseModel):
    """Region to redact."""

    page: int = Field(..., ge=0)
    x: float = Field(..., ge=0)
    y: float = Field(..., ge=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)


class PDFRedactRequest(BaseModel):
    """Request to redact regions in PDF."""

    regions: list[RedactionRegion] = Field(..., min_length=1)


class PDFMergeRequest(BaseModel):
    """Request to merge PDFs."""

    document_ids: list[str] = Field(..., min_length=2)


class PDFOperationResponse(BaseModel):
    """Response for PDF operations."""

    success: bool
    output_path: Optional[str] = None
    page_count: Optional[int] = None
    error: Optional[str] = None


# ============================================
# AI Writing Schemas
# ============================================

class AIWritingRequest(BaseModel):
    """Request for AI writing assistance."""

    text: str = Field(..., min_length=1, max_length=50000)
    instruction: Optional[str] = None
    options: dict[str, Any] = {}


class GrammarCheckRequest(AIWritingRequest):
    """Request for grammar check."""

    pass


class SummarizeRequest(AIWritingRequest):
    """Request to summarize text."""

    length: str = Field(default="medium", pattern="^(short|medium|long)$")
    style: str = Field(default="paragraph", pattern="^(paragraph|bullets|key_points)$")


class RewriteRequest(AIWritingRequest):
    """Request to rewrite text."""

    tone: str = Field(default="professional", pattern="^(professional|casual|formal|friendly|academic)$")
    style: str = Field(default="clear", pattern="^(clear|concise|detailed|simple)$")


class ExpandRequest(AIWritingRequest):
    """Request to expand text."""

    target_length: str = Field(default="double", pattern="^(double|triple|paragraph)$")


class TranslateRequest(AIWritingRequest):
    """Request to translate text."""

    target_language: str = Field(..., min_length=2, max_length=50)
    preserve_formatting: bool = True


class ToneAdjustRequest(AIWritingRequest):
    """Request to adjust tone."""

    target_tone: str = Field(..., pattern="^(formal|casual|professional|friendly|academic|persuasive)$")


class AIWritingResponse(BaseModel):
    """Response for AI writing operations."""

    original_text: str
    result_text: str
    suggestions: list[dict[str, Any]] = []
    confidence: float = 1.0
    metadata: dict[str, Any] = {}


# ============================================
# Additional Request Schemas
# ============================================

class CommentReplyRequest(BaseModel):
    """Request to reply to a comment."""

    text: str = Field(..., min_length=1, max_length=5000)


class PresenceUpdateBody(BaseModel):
    """Request body for updating user presence."""

    user_id: str = Field(..., min_length=1)
    cursor_position: Optional[int] = None
    selection: Optional[dict[str, int]] = None


class PDFSplitRequest(BaseModel):
    """Request to split a PDF at specific pages."""

    split_at_pages: list[int] = Field(..., min_length=1)


class PDFRotateRequest(BaseModel):
    """Request to rotate pages in a PDF."""

    pages: list[int] = Field(..., min_length=1)
    angle: int = Field(..., description="Rotation angle: 0, 90, 180, or 270")


class CreateFromTemplateRequest(BaseModel):
    """Request to create a document from a template."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
