"""Document extraction adapters."""

from .base import Extractor, ExtractionResult, ExtractedTable
from .pdf import PDFExtractor
from .excel import ExcelExtractor

__all__ = [
    "Extractor",
    "ExtractionResult",
    "ExtractedTable",
    "PDFExtractor",
    "ExcelExtractor",
]
