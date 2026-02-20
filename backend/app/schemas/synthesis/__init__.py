"""Schemas for Multi-Document Synthesis."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DocumentType(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    WORD = "word"
    TEXT = "text"
    JSON = "json"


class SynthesisDocument(BaseModel):
    """A document added to a synthesis session."""

    id: str
    name: str
    doc_type: DocumentType
    content_hash: str
    extracted_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Inconsistency(BaseModel):
    """An inconsistency found between documents."""

    id: str
    description: str
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    documents_involved: List[str]
    field_or_topic: str
    values: Dict[str, Any]  # doc_id -> value
    suggested_resolution: Optional[str] = None


class SynthesisSession(BaseModel):
    """A synthesis session containing multiple documents."""

    id: str
    name: str
    documents: List[SynthesisDocument] = Field(default_factory=list)
    inconsistencies: List[Inconsistency] = Field(default_factory=list)
    synthesis_result: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="active", pattern="^(active|processing|completed|error)$")


class SynthesisRequest(BaseModel):
    """Request to synthesize documents in a session."""

    focus_topics: Optional[List[str]] = Field(None, max_length=10)
    output_format: str = Field(default="structured", pattern="^(structured|narrative|comparison)$")
    include_sources: bool = Field(default=True)
    max_length: int = Field(default=5000, ge=500, le=20000)


class SynthesisResult(BaseModel):
    """Result of document synthesis."""

    session_id: str
    synthesis: Dict[str, Any]
    inconsistencies: List[Inconsistency]
    source_references: List[Dict[str, Any]]
    confidence: float = Field(ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
