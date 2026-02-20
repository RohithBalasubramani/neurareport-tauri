from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TemplateImportResult(BaseModel):
    template_id: str
    name: str
    kind: str
    artifacts: dict
    correlation_id: Optional[str] = None

