"""PDF extraction adapter."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseExtractor, ExtractionResult, ExtractedTable, ExtractedText

logger = logging.getLogger("neura.adapters.extraction.pdf")


class PDFExtractor(BaseExtractor):
    """Extract data from PDF documents.

    Uses multiple extraction backends for best results:
    - pdfplumber for tables
    - PyMuPDF for text
    - Tabula as fallback
    """

    def __init__(
        self,
        *,
        prefer_backend: str = "pdfplumber",
        extract_text: bool = True,
    ) -> None:
        self._prefer_backend = prefer_backend
        self._extract_text = extract_text

    def supports(self, path: Path) -> bool:
        """Check if this extractor supports the file."""
        return path.suffix.lower() == ".pdf"

    def extract(self, path: Path) -> ExtractionResult:
        """Extract all data from a PDF."""
        self._validate_path(path)
        start = time.perf_counter()
        errors: List[str] = []
        tables: List[ExtractedTable] = []
        text_blocks: List[ExtractedText] = []
        page_count = 0
        metadata: Dict[str, Any] = {}

        # Try to get page count and metadata
        try:
            page_count, metadata = self._get_pdf_info(path)
        except Exception as e:
            errors.append(f"Failed to read PDF info: {e}")

        # Extract tables
        try:
            tables = self.extract_tables(path)
        except Exception as e:
            errors.append(f"Table extraction failed: {e}")

        # Extract text
        if self._extract_text:
            try:
                text_blocks = self._extract_text_blocks(path)
            except Exception as e:
                errors.append(f"Text extraction failed: {e}")

        extraction_time = (time.perf_counter() - start) * 1000

        return ExtractionResult(
            source_path=path,
            page_count=page_count,
            tables=tables,
            text_blocks=text_blocks,
            metadata=metadata,
            errors=errors,
            extraction_time_ms=extraction_time,
        )

    def extract_tables(self, path: Path) -> List[ExtractedTable]:
        """Extract tables from a PDF."""
        self._validate_path(path)

        if self._prefer_backend == "pdfplumber":
            return self._extract_with_pdfplumber(path)
        elif self._prefer_backend == "tabula":
            return self._extract_with_tabula(path)
        else:
            # Try pdfplumber first, fall back to tabula
            try:
                return self._extract_with_pdfplumber(path)
            except Exception:
                return self._extract_with_tabula(path)

    def _get_pdf_info(self, path: Path) -> tuple[int, Dict[str, Any]]:
        """Get PDF page count and metadata."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            try:
                page_count = len(doc)
                metadata = dict(doc.metadata) if doc.metadata else {}
                return page_count, metadata
            finally:
                doc.close()
        except ImportError:
            pass

        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                return len(pdf.pages), {}
        except ImportError:
            pass

        return 0, {}

    def _extract_with_pdfplumber(self, path: Path) -> List[ExtractedTable]:
        """Extract tables using pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "pdfplumber is required. Install with: pip install pdfplumber"
            )

        tables: List[ExtractedTable] = []

        with pdfplumber.open(path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for table_idx, table in enumerate(page_tables):
                    if not table or len(table) < 2:
                        continue

                    headers = [str(h or "") for h in table[0]]
                    rows = [[str(c or "") for c in row] for row in table[1:]]

                    tables.append(
                        ExtractedTable(
                            page_number=page_idx + 1,
                            table_index=table_idx,
                            headers=headers,
                            rows=rows,
                            confidence=0.8,
                        )
                    )

        return tables

    def _extract_with_tabula(self, path: Path) -> List[ExtractedTable]:
        """Extract tables using tabula-py."""
        try:
            import tabula
        except ImportError:
            raise ImportError(
                "tabula-py is required. Install with: pip install tabula-py"
            )

        tables: List[ExtractedTable] = []
        dfs = tabula.read_pdf(str(path), pages="all", multiple_tables=True)

        for table_idx, df in enumerate(dfs):
            if df.empty:
                continue

            headers = [str(c) for c in df.columns.tolist()]
            rows = df.fillna("").astype(str).values.tolist()

            tables.append(
                ExtractedTable(
                    page_number=1,  # Tabula doesn't always track page
                    table_index=table_idx,
                    headers=headers,
                    rows=rows,
                    confidence=0.7,
                )
            )

        return tables

    def _extract_text_blocks(self, path: Path) -> List[ExtractedText]:
        """Extract text blocks from PDF."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.warning("PyMuPDF not available for text extraction")
            return []

        text_blocks: List[ExtractedText] = []
        doc = fitz.open(str(path))

        for page_idx, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    text = ""
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text += span.get("text", "")
                        text += "\n"

                    if text.strip():
                        text_blocks.append(
                            ExtractedText(
                                page_number=page_idx + 1,
                                content=text.strip(),
                                bbox=tuple(block.get("bbox", [])),
                            )
                        )

        doc.close()
        return text_blocks
