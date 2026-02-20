"""
PDF Operations Service - PDF manipulation operations.
"""

from __future__ import annotations

import io
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Optional, Sequence

from pydantic import BaseModel

from backend.app.services.config import get_settings

logger = logging.getLogger("neura.pdf_operations")


class PageInfo(BaseModel):
    """PDF page information."""

    page_number: int
    width: float
    height: float
    rotation: int = 0


class WatermarkConfig(BaseModel):
    """Watermark configuration."""

    text: str
    position: str = "center"  # center, diagonal, top, bottom
    font_size: int = 48
    opacity: float = 0.3
    color: str = "#808080"
    rotation: float = -45  # For diagonal


class RedactionRegion(BaseModel):
    """Region to redact in PDF."""

    page: int
    x: float
    y: float
    width: float
    height: float
    color: str = "#000000"


class PDFMergeResult(BaseModel):
    """Result of PDF merge operation."""

    output_path: str
    page_count: int
    source_files: list[str]


class PDFOperationsService:
    """Service for PDF manipulation operations."""

    def __init__(self, output_dir: Optional[Path] = None):
        base_root = get_settings().uploads_root
        self._output_dir = output_dir or (base_root / "pdf_outputs")
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def _validate_pdf_input(
        self,
        pdf_path: Path,
        *,
        required_pages: Optional[list[int]] = None,
        operation: str = "process",
    ) -> None:
        """Validate a PDF file before performing operations.

        Centralizes file-existence, readability, corruption, and page-bounds
        checks that previously failed deep inside PyMuPDF with opaque errors.

        Args:
            pdf_path: Path to the PDF file
            required_pages: If specified, validate these page numbers exist
            operation: Name of the operation (for error messages)

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file is not readable
            ValueError: If the file is not a valid PDF or pages are out of range
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not os.access(pdf_path, os.R_OK):
            raise PermissionError(f"PDF file not readable: {pdf_path}")

        if pdf_path.stat().st_size == 0:
            raise ValueError(f"PDF file is empty: {pdf_path}")

        # Validate PDF header
        try:
            with open(pdf_path, "rb") as f:
                header = f.read(5)
                if header != b"%PDF-":
                    raise ValueError(
                        f"File does not appear to be a valid PDF (bad header): {pdf_path}"
                    )
        except (OSError, IOError) as e:
            raise ValueError(f"Cannot read PDF file: {pdf_path}: {e}") from e

        # Validate page numbers if specified
        if required_pages is not None:
            import fitz
            doc = None
            try:
                doc = fitz.open(str(pdf_path))
                total = doc.page_count
                for page_num in required_pages:
                    if page_num < 0 or page_num >= total:
                        raise ValueError(
                            f"Page {page_num} out of range for {operation} "
                            f"(PDF has {total} pages, valid range: 0-{total - 1})"
                        )
            except ValueError:
                raise
            except Exception as e:
                raise ValueError(f"Cannot open PDF for validation: {pdf_path}: {e}") from e
            finally:
                if doc:
                    doc.close()

    def get_page_info(self, pdf_path: Path) -> list[PageInfo]:
        """Get information about all pages in a PDF."""
        self._validate_pdf_input(pdf_path, operation="get_page_info")
        import fitz  # PyMuPDF

        doc = None
        try:
            doc = fitz.open(str(pdf_path))
            pages = []
            for i, page in enumerate(doc):
                rect = page.rect
                pages.append(PageInfo(
                    page_number=i,
                    width=rect.width,
                    height=rect.height,
                    rotation=page.rotation,
                ))
            return pages
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            raise
        finally:
            if doc:
                doc.close()

    def reorder_pages(
        self,
        pdf_path: Path,
        new_order: list[int],
        output_path: Optional[Path] = None,
    ) -> Path:
        """Reorder pages in a PDF according to new_order list."""
        self._validate_pdf_input(pdf_path, required_pages=new_order, operation="reorder_pages")
        import fitz

        doc = None
        new_doc = None
        try:
            doc = fitz.open(str(pdf_path))

            # Validate page numbers
            total_pages = doc.page_count
            for page_num in new_order:
                if page_num < 0 or page_num >= total_pages:
                    raise ValueError(f"Invalid page number: {page_num}")

            # Create new document with reordered pages
            new_doc = fitz.open()
            for page_num in new_order:
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

            # Save to output path
            if output_path is None:
                output_path = self._output_dir / f"{uuid.uuid4()}_reordered.pdf"

            new_doc.save(str(output_path))
            logger.info(f"Reordered pages to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error reordering pages: {e}")
            raise
        finally:
            if new_doc:
                new_doc.close()
            if doc:
                doc.close()

    def add_watermark(
        self,
        pdf_path: Path,
        config: WatermarkConfig,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Add a watermark to all pages of a PDF."""
        self._validate_pdf_input(pdf_path, operation="add_watermark")
        import fitz

        doc = None
        try:
            doc = fitz.open(str(pdf_path))

            for page in doc:
                rect = page.rect

                # Calculate position
                if config.position == "center":
                    point = fitz.Point(rect.width / 2, rect.height / 2)
                elif config.position == "diagonal":
                    point = fitz.Point(rect.width / 2, rect.height / 2)
                elif config.position == "top":
                    point = fitz.Point(rect.width / 2, 50)
                elif config.position == "bottom":
                    point = fitz.Point(rect.width / 2, rect.height - 50)
                else:
                    point = fitz.Point(rect.width / 2, rect.height / 2)

                # Parse color
                color = self._hex_to_rgb(config.color)

                rotate = 0
                morph = None
                if config.position == "diagonal":
                    angle = config.rotation or -45
                    morph = (point, fitz.Matrix(1, 1).prerotate(angle))

                page.insert_text(
                    point,
                    config.text,
                    fontsize=config.font_size,
                    color=color,
                    rotate=rotate,
                    morph=morph,
                    overlay=True,
                )

                # Apply opacity by setting blend mode
                # Note: PyMuPDF doesn't directly support opacity for text
                # For true opacity, would need to use pikepdf

            # Save to output path
            if output_path is None:
                output_path = self._output_dir / f"{uuid.uuid4()}_watermarked.pdf"

            doc.save(str(output_path))
            logger.info(f"Added watermark to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error adding watermark: {e}")
            raise
        finally:
            if doc:
                doc.close()

    def redact_regions(
        self,
        pdf_path: Path,
        regions: list[RedactionRegion],
        output_path: Optional[Path] = None,
    ) -> Path:
        """Redact specified regions in a PDF."""
        self._validate_pdf_input(pdf_path, operation="redact_regions")
        import fitz

        doc = None
        try:
            doc = fitz.open(str(pdf_path))

            for region in regions:
                if region.page < 0 or region.page >= doc.page_count:
                    continue

                page = doc[region.page]
                rect = fitz.Rect(
                    region.x,
                    region.y,
                    region.x + region.width,
                    region.y + region.height,
                )

                # Add redaction annotation
                page.add_redact_annot(rect, fill=self._hex_to_rgb(region.color))

            # Apply redactions
            for page in doc:
                page.apply_redactions()

            # Save to output path
            if output_path is None:
                output_path = self._output_dir / f"{uuid.uuid4()}_redacted.pdf"

            doc.save(str(output_path))
            logger.info(f"Applied redactions to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error applying redactions: {e}")
            raise
        finally:
            if doc:
                doc.close()

    def merge_pdfs(
        self,
        pdf_paths: Sequence[Path],
        output_path: Optional[Path] = None,
    ) -> PDFMergeResult:
        """Merge multiple PDFs into one."""
        import fitz

        merged_doc = None
        try:
            merged_doc = fitz.open()
            source_files = []

            for pdf_path in pdf_paths:
                try:
                    self._validate_pdf_input(pdf_path, operation="merge_pdfs")
                except (FileNotFoundError, PermissionError, ValueError) as e:
                    logger.warning(f"Skipping invalid PDF in merge: {e}")
                    continue

                doc = None
                try:
                    doc = fitz.open(str(pdf_path))
                    merged_doc.insert_pdf(doc)
                    source_files.append(str(pdf_path))
                finally:
                    if doc:
                        doc.close()

            # Save to output path
            if output_path is None:
                output_path = self._output_dir / f"{uuid.uuid4()}_merged.pdf"

            merged_doc.save(str(output_path))
            page_count = merged_doc.page_count

            logger.info(f"Merged {len(source_files)} PDFs to: {output_path}")
            return PDFMergeResult(
                output_path=str(output_path),
                page_count=page_count,
                source_files=source_files,
            )
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            raise
        finally:
            if merged_doc:
                merged_doc.close()

    def split_pdf(
        self,
        pdf_path: Path,
        page_ranges: list[tuple[int, int]],
        output_dir: Optional[Path] = None,
    ) -> list[Path]:
        """Split a PDF into multiple files based on page ranges."""
        self._validate_pdf_input(pdf_path, operation="split_pdf")
        import fitz

        doc = None
        try:
            doc = fitz.open(str(pdf_path))
            output_dir = output_dir or self._output_dir
            output_paths = []

            for i, (start, end) in enumerate(page_ranges):
                # Validate range
                start = max(0, start)
                end = min(doc.page_count - 1, end)

                if start > end:
                    continue

                # Create new document with range
                new_doc = None
                try:
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=start, to_page=end)

                    output_path = output_dir / f"{uuid.uuid4()}_split_{i+1}.pdf"
                    new_doc.save(str(output_path))
                    output_paths.append(output_path)
                finally:
                    if new_doc:
                        new_doc.close()

            logger.info(f"Split PDF into {len(output_paths)} files")
            return output_paths
        except Exception as e:
            logger.error(f"Error splitting PDF: {e}")
            raise
        finally:
            if doc:
                doc.close()

    def rotate_pages(
        self,
        pdf_path: Path,
        rotation: int,
        pages: Optional[list[int]] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Rotate pages in a PDF."""
        self._validate_pdf_input(pdf_path, operation="rotate_pages")
        import fitz

        doc = None
        try:
            doc = fitz.open(str(pdf_path))

            # Normalize rotation to 0, 90, 180, or 270
            rotation = rotation % 360
            if rotation not in [0, 90, 180, 270]:
                rotation = 0

            # Rotate specified pages or all pages
            pages_to_rotate = pages if pages else list(range(doc.page_count))

            for page_num in pages_to_rotate:
                if 0 <= page_num < doc.page_count:
                    page = doc[page_num]
                    page.set_rotation(rotation)

            # Save to output path
            if output_path is None:
                output_path = self._output_dir / f"{uuid.uuid4()}_rotated.pdf"

            doc.save(str(output_path))
            logger.info(f"Rotated pages to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error rotating pages: {e}")
            raise
        finally:
            if doc:
                doc.close()

    def extract_pages(
        self,
        pdf_path: Path,
        pages: list[int],
        output_path: Optional[Path] = None,
    ) -> Path:
        """Extract specific pages from a PDF."""
        self._validate_pdf_input(pdf_path, operation="extract_pages")
        import fitz

        doc = None
        new_doc = None
        try:
            doc = fitz.open(str(pdf_path))
            new_doc = fitz.open()

            for page_num in pages:
                if 0 <= page_num < doc.page_count:
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

            # Save to output path
            if output_path is None:
                output_path = self._output_dir / f"{uuid.uuid4()}_extracted.pdf"

            new_doc.save(str(output_path))
            logger.info(f"Extracted {len(pages)} pages to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error extracting pages: {e}")
            raise
        finally:
            if new_doc:
                new_doc.close()
            if doc:
                doc.close()

    def _hex_to_rgb(self, hex_color: str) -> tuple[float, float, float]:
        """Convert hex color to RGB tuple (0-1 range)."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b)
