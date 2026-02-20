from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from backend.app.utils.validation import is_safe_id, is_safe_name, sanitize_id, sanitize_filename


class ConnectionTestRequest(BaseModel):
    db_url: Optional[str] = Field(None, max_length=1000)
    database: Optional[str] = Field(None, max_length=500)
    db_type: str = Field(default="sqlite", max_length=50)

    @field_validator("db_type")
    @classmethod
    def enforce_supported_type(cls, value: str) -> str:
        supported = {"sqlite", "postgresql", "postgres"}
        if (value or "").lower() not in supported:
            raise ValueError(f"Only {', '.join(sorted(supported))} are supported")
        v = value.lower()
        return "postgresql" if v == "postgres" else v

    @field_validator("database")
    @classmethod
    def validate_database_path(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        # Ensure no path traversal
        if ".." in value:
            raise ValueError("Path traversal not allowed")
        return value


class ConnectionUpsertRequest(ConnectionTestRequest):
    id: Optional[str] = Field(None, max_length=64)
    name: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)
    latency_ms: Optional[float] = Field(None, ge=0, le=1000000)
    tags: Optional[list[str]] = Field(None, max_length=20)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not is_safe_id(value):
            raise ValueError("ID must be alphanumeric with dashes/underscores only")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not is_safe_name(value):
            raise ValueError("Name contains invalid characters")
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


class ConnectionResponse(BaseModel):
    id: str
    name: str
    db_type: str
    database_path: Optional[Path] = None
    status: str
    latency_ms: Optional[float] = None

