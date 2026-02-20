"""Base interfaces for rendering adapters."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

logger = logging.getLogger("neura.adapters.rendering.base")

from backend.engine.domain.reports import OutputFormat


@dataclass
class RenderContext:
    """Context passed to renderers.

    Contains all the data needed to render a document.
    """

    template_html: str
    data: Dict[str, Any]
    output_format: OutputFormat
    output_path: Path
    metadata: Dict[str, Any] = field(default_factory=dict)
    landscape: bool = False
    font_scale: Optional[float] = None
    page_size: str = "A4"
    margins: Optional[Dict[str, str]] = None


@dataclass(frozen=True)
class RenderResult:
    """Result of a render operation."""

    success: bool
    output_path: Optional[Path]
    format: OutputFormat
    size_bytes: int = 0
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    render_time_ms: float = 0.0


class Renderer(Protocol):
    """Interface for document renderers.

    Each output format has its own renderer implementation.
    """

    @property
    def output_format(self) -> OutputFormat:
        """The format this renderer produces."""
        ...

    def render(self, context: RenderContext) -> RenderResult:
        """Render a document from the context."""
        ...

    def supports(self, format: OutputFormat) -> bool:
        """Check if this renderer supports the format."""
        ...


class BaseRenderer(ABC):
    """Abstract base class for renderers with common functionality."""

    @property
    @abstractmethod
    def output_format(self) -> OutputFormat:
        """The format this renderer produces."""
        pass

    @abstractmethod
    def render(self, context: RenderContext) -> RenderResult:
        """Render a document from the context."""
        pass

    def supports(self, format: OutputFormat) -> bool:
        """Check if this renderer supports the format."""
        return format == self.output_format

    def _ensure_output_dir(self, path: Path) -> None:
        """Ensure output directory exists."""
        path.parent.mkdir(parents=True, exist_ok=True)

    def _get_file_size(self, path: Path) -> int:
        """Get file size in bytes."""
        try:
            return path.stat().st_size
        except Exception as e:
            logger.debug("Failed to get file size: %s", e)
            return 0
