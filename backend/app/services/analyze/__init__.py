# mypy: ignore-errors
from __future__ import annotations

from .document_analysis_service import (
    analyze_document_streaming,
    get_analysis,
    get_analysis_data,
    suggest_charts_for_analysis,
)
from .extraction_pipeline import (
    ExtractedContent,
    extract_document_content,
    extract_pdf_content,
    extract_excel_content,
    format_content_for_llm,
)
from .enhanced_extraction_service import EnhancedExtractionService
from .analysis_engines import AnalysisEngineService
from .visualization_engine import VisualizationEngine
from .data_transform_export import DataExportService
from .advanced_ai_features import AdvancedAIService
from .user_experience import UserExperienceService
from .integrations import IntegrationService
from .enhanced_analysis_orchestrator import (
    EnhancedAnalysisOrchestrator,
    get_orchestrator,
)

# Create a convenience class reference
DocumentAnalysisService = type("DocumentAnalysisService", (), {
    "analyze_streaming": staticmethod(analyze_document_streaming),
    "get_analysis": staticmethod(get_analysis),
    "get_data": staticmethod(get_analysis_data),
    "suggest_charts": staticmethod(suggest_charts_for_analysis),
})

__all__ = [
    # Legacy
    "DocumentAnalysisService",
    "analyze_document_streaming",
    "get_analysis",
    "get_analysis_data",
    "suggest_charts_for_analysis",
    "ExtractedContent",
    "extract_document_content",
    "extract_pdf_content",
    "extract_excel_content",
    "format_content_for_llm",
    # Enhanced services
    "EnhancedExtractionService",
    "AnalysisEngineService",
    "VisualizationEngine",
    "DataExportService",
    "AdvancedAIService",
    "UserExperienceService",
    "IntegrationService",
    "EnhancedAnalysisOrchestrator",
    "get_orchestrator",
]
