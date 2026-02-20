"""Rendering adapters for document generation."""

from .base import Renderer, RenderResult, RenderContext
from .html import HTMLRenderer
from .pdf import PDFRenderer
from .docx import DOCXRenderer
from .xlsx import XLSXRenderer

__all__ = [
    "Renderer",
    "RenderResult",
    "RenderContext",
    "HTMLRenderer",
    "PDFRenderer",
    "DOCXRenderer",
    "XLSXRenderer",
]
