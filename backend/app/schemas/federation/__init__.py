"""Schemas for Cross-Database Federation feature."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TableReference(BaseModel):
    """Reference to a table in a connection."""
    connection_id: str
    table_name: str
    alias: Optional[str] = None


class JoinCondition(BaseModel):
    """A join condition between two tables."""
    left_table: str
    left_column: str
    right_table: str
    right_column: str
    join_type: str = "INNER"  # INNER, LEFT, RIGHT, FULL


class JoinSuggestion(BaseModel):
    """AI-suggested join between tables."""
    left_connection_id: str
    left_table: str
    left_column: str
    right_connection_id: str
    right_table: str
    right_column: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    suggested_join_type: str = "INNER"


class VirtualSchema(BaseModel):
    """A virtual schema spanning multiple databases."""
    id: str
    name: str
    description: Optional[str] = None
    connections: List[str]  # Connection IDs
    tables: List[TableReference]
    joins: List[JoinCondition]
    created_at: str
    updated_at: str


class VirtualSchemaCreate(BaseModel):
    """Request to create a virtual schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    connection_ids: List[str] = Field(..., min_length=1, max_length=10)


class SuggestJoinsRequest(BaseModel):
    """Request to suggest joins between connections."""
    connection_ids: List[str] = Field(..., min_length=2, max_length=10)


class FederatedQueryRequest(BaseModel):
    """Request to execute a federated query."""
    virtual_schema_id: str
    sql: str = Field(..., min_length=1, max_length=10000)
    limit: int = Field(default=100, ge=1, le=1000)
