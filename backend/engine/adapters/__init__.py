"""Adapters layer - IO operations isolated behind interfaces."""

from .persistence import Repository, UnitOfWork
from .databases import DataSource, SQLiteDataSource
from .rendering import Renderer, RenderResult
from .llm import LLMClient, LLMResponse, LLMMessage, OpenAIClient
from .extraction import Extractor, ExtractionResult, PDFExtractor, ExcelExtractor

__all__ = [
    # Persistence
    "Repository",
    "UnitOfWork",
    # Databases
    "DataSource",
    "SQLiteDataSource",
    # Rendering
    "Renderer",
    "RenderResult",
    # LLM
    "LLMClient",
    "LLMResponse",
    "LLMMessage",
    "OpenAIClient",
    # Extraction
    "Extractor",
    "ExtractionResult",
    "PDFExtractor",
    "ExcelExtractor",
]
