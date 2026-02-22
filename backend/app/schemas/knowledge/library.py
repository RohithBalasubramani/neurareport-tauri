"""Knowledge Management Schemas.

Pydantic models for document library and knowledge management.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    IMAGE = "image"
    OTHER = "other"


class LibraryDocumentCreate(BaseModel):
    """Request to add a document to the library."""
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    document_type: DocumentType = DocumentType.OTHER
    tags: list[str] = Field(default_factory=list)
    collections: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LibraryDocumentUpdate(BaseModel):
    """Request to update a library document."""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    collections: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class LibraryDocumentResponse(BaseModel):
    """Library document response model."""
    id: str
    title: str
    description: Optional[str]
    file_path: Optional[str]
    file_url: Optional[str]
    document_type: DocumentType
    file_size: Optional[int]
    tags: list[str]
    collections: list[str]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime]
    is_favorite: bool = False


class CollectionCreate(BaseModel):
    """Request to create a collection."""
    name: str
    description: Optional[str] = None
    document_ids: list[str] = Field(default_factory=list)
    is_smart: bool = False
    smart_filter: Optional[dict[str, Any]] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CollectionUpdate(BaseModel):
    """Request to update a collection."""
    name: Optional[str] = None
    description: Optional[str] = None
    document_ids: Optional[list[str]] = None
    is_smart: Optional[bool] = None
    smart_filter: Optional[dict[str, Any]] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CollectionResponse(BaseModel):
    """Collection response model."""
    id: str
    name: str
    description: Optional[str]
    document_ids: list[str]
    document_count: int
    is_smart: bool
    smart_filter: Optional[dict[str, Any]]
    icon: Optional[str]
    color: Optional[str]
    created_at: datetime
    updated_at: datetime


class TagCreate(BaseModel):
    """Request to create a tag."""
    name: str
    color: Optional[str] = None
    description: Optional[str] = None


class TagResponse(BaseModel):
    """Tag response model."""
    id: str
    name: str
    color: Optional[str]
    description: Optional[str]
    document_count: int
    created_at: datetime


class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    content: Optional[str] = None
    document_types: list[DocumentType] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    collections: list[str] = Field(default_factory=list)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 50
    offset: int = 0


class SemanticSearchRequest(BaseModel):
    """Semantic search request model."""
    query: str
    document_ids: list[str] = Field(default_factory=list)
    top_k: int = 10
    threshold: float = 0.5


class SearchResult(BaseModel):
    """Search result model."""
    document: LibraryDocumentResponse
    score: float
    highlights: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Search response model."""
    results: list[SearchResult]
    total: int
    query: str
    took_ms: float


class AutoTagRequest(BaseModel):
    """Request to auto-tag a document."""
    document_id: str
    max_tags: int = 5


class AutoTagResponse(BaseModel):
    """Auto-tag response model."""
    document_id: str
    suggested_tags: list[str]
    confidence_scores: dict[str, float]


class RelatedDocumentsRequest(BaseModel):
    """Request to find related documents."""
    document_id: str
    limit: int = 10


class RelatedDocumentsResponse(BaseModel):
    """Related documents response model."""
    document_id: str
    related: list[SearchResult]


class KnowledgeGraphRequest(BaseModel):
    """Request to build a knowledge graph."""
    document_ids: list[str] = Field(default_factory=list)
    depth: int = 2
    include_entities: bool = True
    include_relationships: bool = True


class KnowledgeGraphNode(BaseModel):
    """Knowledge graph node."""
    id: str
    type: str  # document, entity, concept
    label: str
    properties: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphEdge(BaseModel):
    """Knowledge graph edge."""
    source: str
    target: str
    type: str
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphResponse(BaseModel):
    """Knowledge graph response model."""
    nodes: list[KnowledgeGraphNode]
    edges: list[KnowledgeGraphEdge]
    metadata: dict[str, Any] = Field(default_factory=dict)


class FAQGenerateRequest(BaseModel):
    """Request to generate FAQ from documents."""
    document_ids: list[str]
    max_questions: int = 10
    categories: list[str] = Field(default_factory=list)


class FAQItem(BaseModel):
    """FAQ item model."""
    question: str
    answer: str
    source_document_id: str
    confidence: float
    category: Optional[str] = None


class FAQResponse(BaseModel):
    """FAQ response model."""
    items: list[FAQItem]
    source_documents: list[str]
