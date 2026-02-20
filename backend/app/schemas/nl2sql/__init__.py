"""Schemas for Natural Language to SQL feature."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from backend.app.utils.validation import is_safe_id, is_safe_name


class NL2SQLGenerateRequest(BaseModel):
    """Request to generate SQL from natural language."""
    question: str = Field(..., min_length=3, max_length=2000)
    connection_id: str = Field(..., min_length=1, max_length=64)
    tables: Optional[List[str]] = Field(None, max_length=50)
    context: Optional[str] = Field(None, max_length=1000)

    @field_validator("connection_id")
    @classmethod
    def validate_connection_id(cls, value: str) -> str:
        if not is_safe_id(value):
            raise ValueError("Connection ID must be alphanumeric with dashes/underscores only")
        return value

    @field_validator("tables")
    @classmethod
    def validate_table_name(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        for i, name in enumerate(value):
            if not name or len(name) > 128:
                raise ValueError("Table name must be 1-128 characters")
            value[i] = name.strip()
        return value


class NL2SQLExecuteRequest(BaseModel):
    """Request to execute a SQL query."""
    sql: str = Field(..., min_length=1, max_length=10000)
    connection_id: str = Field(..., min_length=1, max_length=64)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    include_total: bool = Field(default=False)

    @field_validator("connection_id")
    @classmethod
    def validate_connection_id(cls, value: str) -> str:
        if not is_safe_id(value):
            raise ValueError("Connection ID must be alphanumeric with dashes/underscores only")
        return value


class NL2SQLSaveRequest(BaseModel):
    """Request to save a query as a reusable data source."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sql: str = Field(..., min_length=1, max_length=10000)
    connection_id: str = Field(..., min_length=1, max_length=64)
    original_question: Optional[str] = Field(None, max_length=2000)
    tags: Optional[List[str]] = Field(None, max_length=20)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not is_safe_name(value):
            raise ValueError("Name contains invalid characters")
        return value.strip()

    @field_validator("connection_id")
    @classmethod
    def validate_connection_id(cls, value: str) -> str:
        if not is_safe_id(value):
            raise ValueError("Connection ID must be alphanumeric with dashes/underscores only")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tag(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        for i, tag in enumerate(value):
            if len(tag) > 50:
                raise ValueError("Tag must be 50 characters or less")
            value[i] = tag.strip()
        return value


class NL2SQLResult(BaseModel):
    """Result from SQL generation."""
    sql: str
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)
    original_question: str


class QueryExecutionResult(BaseModel):
    """Result from query execution."""
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    total_count: Optional[int] = None
    execution_time_ms: int
    truncated: bool = False


class SavedQuery(BaseModel):
    """A saved SQL query."""
    id: str
    name: str
    description: Optional[str] = None
    sql: str
    connection_id: str
    original_question: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    last_run_at: Optional[str] = None
    run_count: int = 0


class QueryHistoryEntry(BaseModel):
    """An entry in the query history."""
    id: str
    question: str
    sql: str
    connection_id: str
    confidence: float
    success: bool
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    row_count: Optional[int] = None
    created_at: str
