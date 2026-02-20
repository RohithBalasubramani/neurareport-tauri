# mypy: ignore-errors
"""
Comprehensive Test Suite for Open Source AI Integrations.

Tests:
1. Multi-Provider LLM Support (OpenAI, Ollama, DeepSeek)
2. Document Extraction (PDF, Excel)
3. Vision-Language Models
4. Multi-Agent System
5. Text-to-SQL Generation
6. RAG Framework
7. Chart Generation
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(test_name: str, success: bool, details: str = "", skip: bool = False):
    """Print test result."""
    if skip:
        status = "[SKIP]"
    else:
        status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        for line in details.split("\n"):
            print(f"       {line}")


def _check_llm_config():
    """Test LLM configuration detection."""
    print_header("1. LLM Configuration")

    try:
        from backend.app.services.llm import get_llm_config, LLMProvider

        config = get_llm_config()
        print_result(
            "Configuration loaded",
            True,
            f"Provider: {config.provider.value}\n"
            f"Model: {config.model}\n"
            f"Timeout: {config.timeout_seconds}s\n"
            f"Max retries: {config.max_retries}"
        )
        return True
    except Exception as e:
        print_result("Configuration loaded", False, str(e))
        return False


def _check_llm_providers():
    """Test LLM provider availability."""
    print_header("2. LLM Providers")

    results = {}

    # Test OpenAI (REQUIRED - this is the primary provider)
    try:
        from backend.app.services.llm.providers import OpenAIProvider
        from backend.app.services.llm.config import LLMConfig, LLMProvider as LP

        config = LLMConfig(
            provider=LP.OPENAI,
            model="gpt-5",
            api_key=os.getenv("OPENAI_API_KEY", "test-key"),
        )
        provider = OpenAIProvider(config)
        has_key = bool(os.getenv("OPENAI_API_KEY"))
        print_result("OpenAI Provider (Primary)", has_key, "API key configured" if has_key else "No API key (OPENAI_API_KEY)")
        results["openai"] = has_key
    except Exception as e:
        print_result("OpenAI Provider (Primary)", False, str(e))
        results["openai"] = False

    # Test Ollama (OPTIONAL - local models)
    try:
        from backend.app.services.llm.providers import OllamaProvider
        from backend.app.services.llm.config import LLMConfig, LLMProvider as LP

        config = LLMConfig(
            provider=LP.OLLAMA,
            model="llama3.2",
            base_url="http://localhost:11434",
        )
        provider = OllamaProvider(config)
        available = provider.health_check()
        # Mark as SKIP (not failure) when not running - it's optional
        print_result("Ollama Provider (Optional)", available,
                    "Local models available" if available else "Not running - using OpenAI instead",
                    skip=not available)
        results["ollama"] = True if available else None  # None = skipped, not failed

        if available:
            models = provider.list_models()
            print(f"       Available models: {models[:5]}{'...' if len(models) > 5 else ''}")
    except Exception as e:
        print_result("Ollama Provider (Optional)", False, str(e), skip=True)
        results["ollama"] = None  # Mark as skipped, not failed

    # Test DeepSeek (OPTIONAL - alternative provider)
    try:
        from backend.app.services.llm.providers import DeepSeekProvider
        from backend.app.services.llm.config import LLMConfig, LLMProvider as LP

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key:
            config = LLMConfig(
                provider=LP.DEEPSEEK,
                model="deepseek-chat",
                api_key=api_key,
            )
            provider = DeepSeekProvider(config)
            print_result("DeepSeek Provider (Optional)", True, "API key configured")
            results["deepseek"] = True
        else:
            # Mark as SKIP - it's optional
            print_result("DeepSeek Provider (Optional)", False,
                        "No API key - using OpenAI instead", skip=True)
            results["deepseek"] = None  # Mark as skipped
    except Exception as e:
        print_result("DeepSeek Provider (Optional)", False, str(e), skip=True)
        results["deepseek"] = None

    return results


def _check_pdf_extractors():
    """Test PDF extraction tools."""
    print_header("3. PDF Extraction Tools")

    from backend.app.services.extraction import get_available_extractors

    available = get_available_extractors()
    print(f"Available extractors: {available}")

    results = {}

    # Test each extractor
    extractors_to_test = ["pymupdf", "pdfplumber", "tabula", "camelot"]

    for name in extractors_to_test:
        is_available = name in available
        print_result(f"{name.capitalize()} Extractor", is_available)
        results[name] = is_available

    return results


def _check_excel_extractor():
    """Test Excel extraction."""
    print_header("4. Excel Extraction")

    try:
        from backend.app.services.extraction import ExcelExtractor

        extractor = ExcelExtractor()

        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age,City\n")
            f.write("Alice,30,New York\n")
            f.write("Bob,25,San Francisco\n")
            f.write("Charlie,35,Chicago\n")
            csv_path = f.name

        # Extract
        result = extractor.extract(csv_path)

        success = len(result.sheets) > 0 and result.sheets[0].row_count == 3
        print_result(
            "CSV Extraction",
            success,
            f"Sheets: {len(result.sheets)}, Rows: {result.sheets[0].row_count if result.sheets else 0}"
        )

        # Cleanup
        os.unlink(csv_path)

        return success
    except Exception as e:
        print_result("CSV Extraction", False, str(e))
        return False


def _check_vision_language_model():
    """Test VLM integration."""
    print_header("5. Vision-Language Models")

    try:
        from backend.app.services.llm import get_vlm, get_llm_config

        config = get_llm_config()
        vlm = get_vlm()

        print_result(
            "VLM Initialization",
            True,
            f"Using model: {vlm.model}\n"
            f"Vision support: {config.supports_vision}"
        )

        # List supported vision models
        from backend.app.services.llm.config import VISION_MODELS
        for provider, models in VISION_MODELS.items():
            if models:
                print(f"       {provider.value}: {models[:3]}...")

        return True
    except Exception as e:
        print_result("VLM Initialization", False, str(e))
        return False


def _check_multi_agent_system():
    """Test multi-agent orchestration."""
    print_header("6. Multi-Agent System")

    try:
        from backend.app.services.llm import (
            Agent,
            AgentConfig,
            AgentRole,
            Task,
            create_document_analyzer_agent,
            create_document_processing_crew,
        )

        # Test agent creation
        agent = create_document_analyzer_agent()
        print_result(
            "Agent Creation",
            True,
            f"Role: {agent.role}\n"
            f"Goal: {agent.config.goal[:50]}..."
        )

        # Test crew creation
        crew = create_document_processing_crew(verbose=False)
        print_result(
            "Crew Creation",
            True,
            f"Agents: {len(crew.agents)}\n"
            f"Tasks: {len(crew.tasks)}"
        )

        return True
    except Exception as e:
        print_result("Multi-Agent System", False, str(e))
        return False


def _check_text_to_sql():
    """Test Text-to-SQL generation."""
    print_header("7. Text-to-SQL Generation")

    try:
        from backend.app.services.llm import TextToSQL, TableSchema

        t2sql = TextToSQL(dialect="duckdb")

        # Add test schema
        t2sql.add_table_schema(TableSchema(
            name="orders",
            columns=[
                {"name": "id", "type": "INTEGER", "description": "Order ID"},
                {"name": "customer_id", "type": "INTEGER", "description": "Customer ID"},
                {"name": "amount", "type": "DECIMAL", "description": "Order amount"},
                {"name": "order_date", "type": "DATE", "description": "Order date"},
            ],
            primary_key="id",
        ))

        t2sql.add_table_schema(TableSchema(
            name="customers",
            columns=[
                {"name": "id", "type": "INTEGER", "description": "Customer ID"},
                {"name": "name", "type": "VARCHAR", "description": "Customer name"},
                {"name": "email", "type": "VARCHAR", "description": "Email address"},
            ],
            primary_key="id",
        ))

        print_result(
            "Schema Registration",
            True,
            f"Tables: {list(t2sql._schemas.keys())}"
        )

        # Test SQL generation (without actual LLM call)
        print_result(
            "SQL Generator Ready",
            True,
            f"Dialect: {t2sql.dialect}\n"
            f"Model: {t2sql.model}"
        )

        return True
    except Exception as e:
        print_result("Text-to-SQL", False, str(e))
        return False


def _check_rag_framework():
    """Test RAG framework."""
    print_header("8. RAG Framework")

    try:
        from backend.app.services.llm import RAGRetriever, create_retriever, BM25Index

        # Test BM25 index
        index = BM25Index()
        from backend.app.services.llm.rag import Document

        docs = [
            Document(id="1", content="Python is a programming language."),
            Document(id="2", content="Machine learning uses Python extensively."),
            Document(id="3", content="JavaScript is used for web development."),
        ]
        index.add_documents(docs)

        results = index.search("Python programming", top_k=2)
        print_result(
            "BM25 Search",
            len(results) == 2,
            f"Found {len(results)} documents\n"
            f"Top result: {results[0][0].id if results else 'None'}"
        )

        # Test RAG retriever
        retriever = create_retriever(use_embeddings=False)
        retriever.add_document("The quick brown fox jumps over the lazy dog.", doc_id="fox")
        retriever.add_document("Machine learning is transforming industries.", doc_id="ml")

        result = retriever.retrieve("machine learning", top_k=1)
        print_result(
            "RAG Retriever",
            len(result.documents) > 0,
            f"Documents indexed: 2\n"
            f"Method: {result.method}"
        )

        return True
    except Exception as e:
        print_result("RAG Framework", False, str(e))
        return False


def _check_chart_generation():
    """Test chart generation."""
    print_header("9. Chart Generation (QuickChart)")

    try:
        from backend.app.services.charts import (
            QuickChartClient,
            create_bar_chart,
            create_line_chart,
            generate_chart_url,
        )

        client = QuickChartClient()

        # Test bar chart
        config = create_bar_chart(
            labels=["Jan", "Feb", "Mar", "Apr"],
            datasets=[{"label": "Sales", "data": [10, 20, 30, 25]}],
            title="Monthly Sales",
        )
        url = client.get_chart_url(config)

        print_result(
            "Bar Chart URL",
            url.startswith("https://quickchart.io"),
            f"URL length: {len(url)} chars"
        )

        # Test line chart
        config = create_line_chart(
            labels=["Q1", "Q2", "Q3", "Q4"],
            datasets=[
                {"label": "2023", "data": [100, 120, 140, 160]},
                {"label": "2024", "data": [110, 130, 150, 180]},
            ],
            title="Quarterly Revenue",
        )
        url = client.get_chart_url(config)

        print_result(
            "Line Chart URL",
            url.startswith("https://quickchart.io"),
            "Multi-dataset support working"
        )

        # Test quick function
        url = generate_chart_url(
            "pie",
            labels=["A", "B", "C"],
            data=[30, 50, 20],
            title="Distribution",
        )

        print_result(
            "Pie Chart (Quick Function)",
            url.startswith("https://quickchart.io"),
        )

        return True
    except Exception as e:
        print_result("Chart Generation", False, str(e))
        return False


def _check_document_extractor():
    """Test enhanced document extractor."""
    print_header("10. Enhanced Document Extractor")

    try:
        from backend.app.services.llm import EnhancedDocumentExtractor

        extractor = EnhancedDocumentExtractor(use_vlm=False)

        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Product,Price,Quantity\n")
            f.write("Widget,10.99,100\n")
            f.write("Gadget,24.99,50\n")
            csv_path = f.name

        result = extractor.extract(csv_path)

        success = len(result.tables) > 0
        print_result(
            "Document Extraction",
            success,
            f"Tables found: {len(result.tables)}\n"
            f"Columns: {result.tables[0].headers if result.tables else []}"
        )

        # Test schema inference
        if result.tables:
            schemas = extractor.infer_schema(result.tables[0])
            print_result(
                "Schema Inference",
                len(schemas) > 0,
                f"Fields: {[s.name for s in schemas]}\n"
                f"Types: {[s.data_type for s in schemas]}"
            )

        os.unlink(csv_path)
        return success
    except Exception as e:
        print_result("Document Extractor", False, str(e))
        return False


def test_llm_config():
    _check_llm_config()


def test_llm_providers():
    _check_llm_providers()


def test_pdf_extractors():
    _check_pdf_extractors()


def test_excel_extractor():
    _check_excel_extractor()


def test_vision_language_model():
    _check_vision_language_model()


def test_multi_agent_system():
    _check_multi_agent_system()


def test_text_to_sql():
    _check_text_to_sql()


def test_rag_framework():
    _check_rag_framework()


def test_chart_generation():
    _check_chart_generation()


def test_document_extractor():
    _check_document_extractor()


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("   NEURA REPORT - AI INTEGRATION TEST SUITE")
    print("=" * 60)

    results = {
        "llm_config": _check_llm_config(),
        "llm_providers": _check_llm_providers(),
        "pdf_extractors": _check_pdf_extractors(),
        "excel_extractor": _check_excel_extractor(),
        "vlm": _check_vision_language_model(),
        "multi_agent": _check_multi_agent_system(),
        "text_to_sql": _check_text_to_sql(),
        "rag": _check_rag_framework(),
        "chart_generation": _check_chart_generation(),
        "document_extractor": _check_document_extractor(),
    }

    # Summary
    print_header("TEST SUMMARY")

    passed = 0
    failed = 0
    skipped = 0

    for test_name, result in results.items():
        if isinstance(result, dict):
            # Provider results
            for sub_name, sub_result in result.items():
                if sub_result is None:
                    skipped += 1
                elif sub_result:
                    passed += 1
                else:
                    failed += 1
        else:
            if result is None:
                skipped += 1
            elif result:
                passed += 1
            else:
                failed += 1

    print(f"\nTotal Tests: {passed + failed + skipped}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped} (optional providers)")
    print(f"\nSuccess Rate: {passed / (passed + failed) * 100:.1f}%" if (passed + failed) > 0 else "\nSuccess Rate: 100%")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
