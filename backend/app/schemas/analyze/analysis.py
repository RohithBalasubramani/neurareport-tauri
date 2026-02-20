# mypy: ignore-errors
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from backend.app.schemas.generate.charts import ChartSpec


class ExtractedTable(BaseModel):
    """A table extracted from the document."""

    id: str
    title: Optional[str] = None
    headers: list[str]
    rows: list[list[Any]]  # Values can be str, int, float, None, etc.
    data_types: Optional[list[str]] = None
    source_page: Optional[int] = None
    source_sheet: Optional[str] = None


class ExtractedDataPoint(BaseModel):
    """A key metric or data point extracted from the document."""

    key: str
    value: Any
    data_type: str = "text"  # "numeric", "date", "text", "percentage", "currency"
    unit: Optional[str] = None
    confidence: float = 1.0
    context: Optional[str] = None


class TimeSeriesCandidate(BaseModel):
    """Information about potential time series data in the document."""

    date_column: str
    value_columns: list[str]
    frequency: Optional[str] = None  # "daily", "weekly", "monthly", "yearly"
    table_id: Optional[str] = None


class FieldInfo(BaseModel):
    """Metadata about a field in the extracted data."""

    name: str
    type: str  # "datetime", "numeric", "text", "category"
    description: Optional[str] = None
    sample_values: Optional[list[Any]] = None


class AnalysisPayload(BaseModel):
    """Request payload for document analysis."""

    template_id: Optional[str] = None
    connection_id: Optional[str] = None
    analysis_mode: str = Field(
        default="standalone",
        description="'standalone' for ad-hoc analysis, 'template_linked' for template association",
    )


class AnalysisResult(BaseModel):
    """Complete result of document analysis."""

    analysis_id: str
    document_name: str
    document_type: str  # "pdf" | "excel"
    processing_time_ms: int
    summary: Optional[str] = None

    tables: list[ExtractedTable] = Field(default_factory=list)
    data_points: list[ExtractedDataPoint] = Field(default_factory=list)
    time_series_candidates: list[TimeSeriesCandidate] = Field(default_factory=list)
    chart_suggestions: list[ChartSpec] = Field(default_factory=list)

    raw_data: list[dict[str, Any]] = Field(default_factory=list)
    field_catalog: list[FieldInfo] = Field(default_factory=list)

    template_id: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)


class AnalysisSuggestChartsPayload(BaseModel):
    """Request payload for chart suggestions on an existing analysis."""

    question: Optional[str] = None
    include_sample_data: bool = True
    table_ids: Optional[list[str]] = None
    date_range: Optional[dict[str, str]] = None
