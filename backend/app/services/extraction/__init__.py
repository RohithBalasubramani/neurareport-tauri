# mypy: ignore-errors
"""
Advanced Document Extraction Module.

Integrates multiple extraction tools:
- Tabula (Java-based, high accuracy for structured tables)
- Camelot (Python, good for complex table layouts)
- PyMuPDF (fast, general purpose)
- pdfplumber (detailed layout analysis)
- Marker (PDF to markdown)

Usage:
    from backend.app.services.extraction import extract_pdf_tables, extract_with_best_method

    tables = extract_pdf_tables("document.pdf", method="auto")
"""

from .pdf_extractors import (
    PDFExtractor,
    TabulaExtractor,
    CamelotExtractor,
    PyMuPDFExtractor,
    PDFPlumberExtractor,
    ExtractedTable,
    ExtractionResult,
    extract_pdf_tables,
    extract_with_best_method,
    compare_extractors,
    get_available_extractors,
)
from .excel_extractors import (
    ExcelExtractor,
    ExcelSheet,
    ExcelExtractionResult,
    extract_excel_data,
)

__all__ = [
    "PDFExtractor",
    "TabulaExtractor",
    "CamelotExtractor",
    "PyMuPDFExtractor",
    "PDFPlumberExtractor",
    "ExtractedTable",
    "ExtractionResult",
    "extract_pdf_tables",
    "extract_with_best_method",
    "compare_extractors",
    "get_available_extractors",
    "ExcelExtractor",
    "ExcelSheet",
    "ExcelExtractionResult",
    "extract_excel_data",
]
