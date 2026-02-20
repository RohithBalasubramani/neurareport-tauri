"""Schemas for Data Enrichment feature."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from backend.app.utils.validation import is_safe_id, is_safe_name


class EnrichmentSourceType(str, Enum):
    """Types of enrichment sources."""
    COMPANY_INFO = "company_info"
    ADDRESS = "address"
    EXCHANGE_RATE = "exchange_rate"
    CUSTOM = "custom"


class EnrichmentSource(BaseModel):
    """Configuration for an enrichment source."""
    id: str
    name: str
    type: EnrichmentSourceType
    description: Optional[str] = None
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    cache_ttl_hours: int = Field(default=24, ge=1, le=720)  # 1 hour to 30 days
    created_at: str
    updated_at: str


class EnrichmentSourceCreate(BaseModel):
    """Request to create an enrichment source."""
    name: str = Field(..., min_length=1, max_length=100)
    type: EnrichmentSourceType
    description: Optional[str] = Field(None, max_length=500)
    config: Dict[str, Any] = Field(default_factory=dict)
    cache_ttl_hours: int = Field(default=24, ge=1, le=720)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not is_safe_name(value):
            raise ValueError("Name contains invalid characters")
        return value.strip()


class EnrichmentFieldMapping(BaseModel):
    """Mapping of source field to enrichment lookup."""
    source_field: str = Field(..., min_length=1, max_length=128)
    enrichment_source_id: str = Field(..., min_length=1, max_length=64)
    target_fields: List[str] = Field(..., min_length=1, max_length=20)
    lookup_key: Optional[str] = None  # Optional override for the lookup key


class EnrichmentRequest(BaseModel):
    """Request to enrich data."""
    data: List[Dict[str, Any]] = Field(..., min_length=1, max_length=1000)
    mappings: List[EnrichmentFieldMapping] = Field(..., min_length=1, max_length=20)
    use_cache: bool = Field(default=True)


class EnrichedField(BaseModel):
    """A single enriched field."""
    field: str
    original_value: Any
    enriched_value: Any
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str
    cached: bool = False


class EnrichmentResult(BaseModel):
    """Result of enrichment for a single row."""
    row_index: int
    enriched_fields: List[EnrichedField]
    errors: List[str] = Field(default_factory=list)


class EnrichmentResponse(BaseModel):
    """Response from enrichment operation."""
    total_rows: int
    enriched_rows: int
    results: List[EnrichmentResult]
    cache_hits: int = 0
    cache_misses: int = 0
    processing_time_ms: int


class EnrichmentPreviewRequest(BaseModel):
    """Request to preview enrichment without persisting."""
    sample_data: List[Dict[str, Any]] = Field(..., min_length=1, max_length=10)
    mappings: List[EnrichmentFieldMapping] = Field(..., min_length=1, max_length=20)


class EnrichmentConfig(BaseModel):
    """Global enrichment configuration."""
    default_cache_ttl_hours: int = Field(default=24, ge=1, le=720)
    max_batch_size: int = Field(default=100, ge=1, le=1000)
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000)


# Simplified request schemas for frontend compatibility
class SimpleEnrichmentRequest(BaseModel):
    """Simplified request to enrich data (frontend-compatible)."""
    data: List[Dict[str, Any]] = Field(..., min_length=1, max_length=1000)
    sources: List[str] = Field(..., min_length=1, max_length=10)  # Source type names
    options: Dict[str, Any] = Field(default_factory=dict)


class SimplePreviewRequest(BaseModel):
    """Simplified preview request (frontend-compatible)."""
    data: List[Dict[str, Any]] = Field(..., min_length=1, max_length=100)
    sources: List[str] = Field(..., min_length=1, max_length=10)  # Source type names
    sample_size: int = Field(default=5, ge=1, le=10)
