"""Base interfaces for document extraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class ExtractedTable:
    """A table extracted from a document."""

    page_number: int
    table_index: int
    headers: List[str]
    rows: List[List[Any]]
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return len(self.headers)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_number": self.page_number,
            "table_index": self.table_index,
            "headers": self.headers,
            "rows": self.rows,
            "confidence": self.confidence,
            "row_count": self.row_count,
            "column_count": self.column_count,
        }


@dataclass
class ExtractedText:
    """Text extracted from a document."""

    page_number: int
    content: str
    bbox: Optional[tuple] = None
    font_info: Optional[Dict[str, Any]] = None


@dataclass
class ExtractionResult:
    """Result of document extraction."""

    source_path: Path
    page_count: int
    tables: List[ExtractedTable] = field(default_factory=list)
    text_blocks: List[ExtractedText] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    extraction_time_ms: float = 0.0

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def table_count(self) -> int:
        return len(self.tables)


class Extractor(Protocol):
    """Interface for document extractors.

    Extractors pull structured data from documents (PDF, Excel, etc.)
    """

    def extract(self, path: Path) -> ExtractionResult:
        """Extract data from a document."""
        ...

    def extract_tables(self, path: Path) -> List[ExtractedTable]:
        """Extract only tables from a document."""
        ...

    def supports(self, path: Path) -> bool:
        """Check if this extractor supports the file type."""
        ...


class BaseExtractor(ABC):
    """Abstract base for extractors with common functionality."""

    @abstractmethod
    def extract(self, path: Path) -> ExtractionResult:
        """Extract data from a document."""
        pass

    @abstractmethod
    def extract_tables(self, path: Path) -> List[ExtractedTable]:
        """Extract only tables from a document."""
        pass

    @abstractmethod
    def supports(self, path: Path) -> bool:
        """Check if this extractor supports the file type."""
        pass

    def _validate_path(self, path: Path) -> None:
        """Validate that the path exists and is a file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
