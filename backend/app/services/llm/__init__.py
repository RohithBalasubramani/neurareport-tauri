# mypy: ignore-errors
"""
LLM abstraction layer using Claude Code CLI.

NeuraReport uses Claude Code CLI as the exclusive LLM backend.
The CLI handles authentication via its own session - no API keys needed.

Features:
- Claude Code CLI integration for all LLM operations
- Vision-Language Model integration for document understanding
- CrewAI-style multi-agent orchestration
- Text-to-SQL generation with SQLCoder patterns
- RAG (Retrieval-Augmented Generation) for context retrieval

Usage:
    from backend.app.services.llm import get_llm_client, call_completion

    # Basic completion
    client = get_llm_client()
    response = call_completion(
        client,
        messages=[{"role": "user", "content": "Hello"}],
        description="test_call"
    )

    # Vision analysis
    from backend.app.services.llm import get_vlm
    vlm = get_vlm()
    result = vlm.analyze_document("path/to/document.png")

    # Text-to-SQL
    from backend.app.services.llm import get_text_to_sql
    t2sql = get_text_to_sql()
    sql = t2sql.generate_sql("Find all orders from last month")

    # RAG query
    from backend.app.services.llm import create_retriever
    retriever = create_retriever()
    retriever.add_document("Document content here...")
    answer = retriever.query_with_context("What is this about?")
"""

from .client import (
    LLMClient,
    get_llm_client,
    call_completion,
    call_completion_with_vision,
    get_available_models,
    health_check,
)
from .config import LLMConfig, LLMProvider, get_llm_config
from .providers import (
    BaseProvider,
    ClaudeCodeCLIProvider,
    LiteLLMProvider,  # Alias for ClaudeCodeCLIProvider for backwards compat
    get_provider,
)
from .vision import (
    VisionLanguageModel,
    DocumentAnalysisResult,
    TableExtractionResult,
    get_vlm,
    analyze_document_image,
    extract_tables_from_image,
)
from .agents import (
    Agent,
    AgentConfig,
    AgentRole,
    Task,
    TaskResult,
    Crew,
    Tool,
    create_document_analyzer_agent,
    create_data_extractor_agent,
    create_sql_generator_agent,
    create_chart_suggester_agent,
    create_template_mapper_agent,
    create_quality_reviewer_agent,
    create_document_processing_crew,
    create_report_generation_crew,
)
from .text_to_sql import (
    TextToSQL,
    TableSchema,
    SQLGenerationResult,
    get_text_to_sql,
    generate_sql,
)
from .rag import (
    RAGRetriever,
    Document,
    RetrievalResult,
    BM25Index,
    create_retriever,
    quick_rag_query,
)
from .document_extractor import (
    EnhancedDocumentExtractor,
    ExtractedContent,
    ExtractedTable,
    FieldSchema,
    extract_document,
    extract_tables,
)

__all__ = [
    # Main client interface
    "LLMClient",
    "get_llm_client",
    "call_completion",
    "call_completion_with_vision",
    "get_available_models",
    "health_check",
    # Configuration
    "LLMConfig",
    "LLMProvider",
    "get_llm_config",
    # Providers
    "BaseProvider",
    "ClaudeCodeCLIProvider",
    "LiteLLMProvider",  # Alias for backwards compat
    "get_provider",
    # Vision-Language Models
    "VisionLanguageModel",
    "DocumentAnalysisResult",
    "TableExtractionResult",
    "get_vlm",
    "analyze_document_image",
    "extract_tables_from_image",
    # Multi-Agent System
    "Agent",
    "AgentConfig",
    "AgentRole",
    "Task",
    "TaskResult",
    "Crew",
    "Tool",
    "create_document_analyzer_agent",
    "create_data_extractor_agent",
    "create_sql_generator_agent",
    "create_chart_suggester_agent",
    "create_template_mapper_agent",
    "create_quality_reviewer_agent",
    "create_document_processing_crew",
    "create_report_generation_crew",
    # Text-to-SQL
    "TextToSQL",
    "TableSchema",
    "SQLGenerationResult",
    "get_text_to_sql",
    "generate_sql",
    # RAG
    "RAGRetriever",
    "Document",
    "RetrievalResult",
    "BM25Index",
    "create_retriever",
    "quick_rag_query",
    # Document Extraction
    "EnhancedDocumentExtractor",
    "ExtractedContent",
    "ExtractedTable",
    "FieldSchema",
    "extract_document",
    "extract_tables",
]
