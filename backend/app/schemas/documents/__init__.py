# Document Schemas
"""
Pydantic schemas for document operations.
"""

from .document import (
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

__all__ = [
    "CreateDocumentRequest",
    "UpdateDocumentRequest",
    "DocumentResponse",
    "DocumentListResponse",
    "CommentRequest",
    "CommentResponse",
    "CommentReplyRequest",
    "CollaborationSessionResponse",
    "PresenceUpdateBody",
    "PDFMergeRequest",
    "PDFWatermarkRequest",
    "PDFRedactRequest",
    "PDFReorderRequest",
    "PDFSplitRequest",
    "PDFRotateRequest",
    "AIWritingRequest",
    "AIWritingResponse",
    "CreateFromTemplateRequest",
]
