"""Domain entities for templates.

Pure business logic: no I/O or framework imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class TemplateStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    ARCHIVED = "archived"


class TemplateKind(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"


@dataclass(frozen=True, slots=True)
class Template:
    id: str
    name: str
    kind: TemplateKind
    status: TemplateStatus = TemplateStatus.DRAFT
    description: str | None = None
    connection_id: str | None = None
    artifacts: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

