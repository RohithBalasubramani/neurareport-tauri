"""Template repository port."""

from __future__ import annotations

from typing import Protocol

from backend.app.domain.templates import Template


class TemplateRepository(Protocol):
    async def get(self, template_id: str) -> Template | None: ...
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[Template]: ...
    async def upsert(self, template: Template) -> Template: ...
    async def delete(self, template_id: str) -> bool: ...

