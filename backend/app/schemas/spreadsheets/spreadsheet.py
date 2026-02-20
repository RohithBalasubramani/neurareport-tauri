"""
Spreadsheet Schemas - Request/Response models for spreadsheet operations.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================
# Spreadsheet CRUD Schemas
# ============================================

class CreateSpreadsheetRequest(BaseModel):
    """Request to create a new spreadsheet."""

    name: str = Field(..., min_length=1, max_length=255)
    initial_data: Optional[list[list[Any]]] = None


class UpdateSpreadsheetRequest(BaseModel):
    """Request to update spreadsheet metadata."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    metadata: Optional[dict[str, Any]] = None


class CellFormat(BaseModel):
    """Cell formatting options."""

    bold: bool = False
    italic: bool = False
    underline: bool = False
    font_size: int = 11
    font_color: str = "#000000"
    background_color: Optional[str] = None
    horizontal_align: str = "left"
    vertical_align: str = "middle"
    number_format: Optional[str] = None


class SheetResponse(BaseModel):
    """Sheet response model."""

    id: str
    name: str
    index: int
    row_count: int
    col_count: int
    frozen_rows: int
    frozen_cols: int


class SpreadsheetResponse(BaseModel):
    """Spreadsheet response model."""

    id: str
    name: str
    sheets: list[SheetResponse]
    created_at: str
    updated_at: str
    owner_id: Optional[str]
    metadata: dict[str, Any]


class SpreadsheetListResponse(BaseModel):
    """List of spreadsheets response."""

    spreadsheets: list[SpreadsheetResponse]
    total: int
    offset: int
    limit: int


class SpreadsheetDataResponse(BaseModel):
    """Spreadsheet with full data response."""

    id: str
    name: str
    sheet_id: str
    sheet_name: str
    data: list[list[Any]]
    formats: dict[str, CellFormat]
    column_widths: dict[int, int]
    row_heights: dict[int, int]
    frozen_rows: int
    frozen_cols: int


# ============================================
# Cell Operations
# ============================================

class CellUpdate(BaseModel):
    """Single cell update."""

    row: int = Field(..., ge=0)
    col: int = Field(..., ge=0)
    value: Any


class CellUpdateRequest(BaseModel):
    """Request to update cells."""

    updates: list[CellUpdate] = Field(..., min_length=1, max_length=10000)


class CellFormatRequest(BaseModel):
    """Request to format cells."""

    range: str = Field(..., pattern=r"^[A-Z]+[0-9]+:[A-Z]+[0-9]+$")
    format: CellFormat


# ============================================
# Sheet Operations
# ============================================

class AddSheetRequest(BaseModel):
    """Request to add a new sheet."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)


class RenameSheetRequest(BaseModel):
    """Request to rename a sheet."""

    name: str = Field(..., min_length=1, max_length=100)


class FreezePanesRequest(BaseModel):
    """Request to freeze panes."""

    rows: int = Field(default=0, ge=0, le=100)
    cols: int = Field(default=0, ge=0, le=26)


# ============================================
# Conditional Formatting
# ============================================

class ConditionalFormatRule(BaseModel):
    """Conditional format rule."""

    type: str = Field(..., pattern="^(greaterThan|lessThan|equals|between|text|custom)$")
    value: Any
    value2: Optional[Any] = None
    format: CellFormat


class ConditionalFormatRequest(BaseModel):
    """Request to add conditional formatting."""

    range: str = Field(..., pattern=r"^[A-Z]+[0-9]+:[A-Z]+[0-9]+$")
    rules: list[ConditionalFormatRule] = Field(..., min_length=1)


# ============================================
# Data Validation
# ============================================

class DataValidationRequest(BaseModel):
    """Request to add data validation."""

    range: str = Field(..., pattern=r"^[A-Z]+[0-9]+:[A-Z]+[0-9]+$")
    type: str = Field(..., pattern="^(list|number|date|text|custom)$")
    criteria: str = Field(default="equals")
    value: Any
    value2: Optional[Any] = None
    allow_blank: bool = True
    show_dropdown: bool = True
    error_message: Optional[str] = None


# ============================================
# Import/Export
# ============================================

class ImportRequest(BaseModel):
    """Request to import data."""

    format: str = Field(default="csv", pattern="^(csv|tsv|xlsx|xls)$")
    delimiter: str = Field(default=",", max_length=1)
    has_headers: bool = True


class ExportRequest(BaseModel):
    """Request to export data."""

    format: str = Field(default="csv", pattern="^(csv|tsv|xlsx)$")
    sheet_index: int = Field(default=0, ge=0)
    delimiter: str = Field(default=",", max_length=1)


class ExportResponse(BaseModel):
    """Export response."""

    content: str
    filename: str
    mime_type: str


# ============================================
# Pivot Tables
# ============================================

class PivotValue(BaseModel):
    """Pivot table value aggregation."""

    field: str
    aggregation: str = Field(default="SUM", pattern="^(SUM|COUNT|AVERAGE|MIN|MAX|COUNTUNIQUE)$")
    alias: Optional[str] = None


class PivotFilter(BaseModel):
    """Pivot table filter."""

    field: str
    values: list[Any]
    exclude: bool = False


class PivotTableRequest(BaseModel):
    """Request to create pivot table."""

    name: str = Field(default="PivotTable1")
    source_range: str = Field(..., pattern=r"^[A-Z]+[0-9]+:[A-Z]+[0-9]+$")
    row_fields: list[str] = Field(default=[])
    column_fields: list[str] = Field(default=[])
    value_fields: list[PivotValue] = Field(..., min_length=1)
    filters: list[PivotFilter] = Field(default=[])
    show_grand_totals: bool = True
    show_row_totals: bool = True
    show_col_totals: bool = True


class PivotTableResponse(BaseModel):
    """Pivot table response."""

    id: str
    name: str
    headers: list[str]
    rows: list[list[Any]]
    column_totals: Optional[list[Any]]
    grand_total: Optional[Any]


# ============================================
# AI Features
# ============================================

class AIFormulaRequest(BaseModel):
    """Request for natural language to formula conversion."""

    description: str = Field(..., min_length=5, max_length=500)
    available_columns: list[str] = Field(default=[])
    sheet_context: Optional[str] = None


class AIFormulaResponse(BaseModel):
    """AI formula response."""

    formula: str
    explanation: str
    example_result: Optional[str] = None
    confidence: float = 1.0
    alternatives: list[str] = []


class AICleanRequest(BaseModel):
    """Request for AI data cleaning suggestions."""

    sample_data: list[list[Any]] = Field(..., min_length=2)
    columns: list[str] = Field(default=[])


class AICleanResponse(BaseModel):
    """AI data cleaning response."""

    issues: list[dict[str, Any]]
    suggestions: list[dict[str, Any]]
    cleaned_data: Optional[list[list[Any]]] = None


class AIAnomalyRequest(BaseModel):
    """Request for anomaly detection."""

    column: str
    data: list[Any]
    method: str = Field(default="zscore", pattern="^(zscore|iqr|isolation_forest)$")


class AIAnomalyResponse(BaseModel):
    """Anomaly detection response."""

    anomalies: list[dict[str, Any]]
    statistics: dict[str, float]
    narrative: str


class AIExplainFormulaRequest(BaseModel):
    """Request to explain a formula."""

    formula: str = Field(..., min_length=2)


class AIExplainFormulaResponse(BaseModel):
    """Formula explanation response."""

    formula: str
    explanation: str
    step_by_step: list[str]
    functions_used: list[dict[str, str]]
