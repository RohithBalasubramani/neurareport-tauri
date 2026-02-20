"""LLM client port (structured generation)."""

from __future__ import annotations

from typing import Any, Protocol


class LLMClient(Protocol):
    def complete(self, *, messages: list[dict[str, Any]], model: str | None = None, **kwargs: Any) -> dict[str, Any]: ...

