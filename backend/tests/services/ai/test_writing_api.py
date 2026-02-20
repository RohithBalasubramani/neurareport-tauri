"""
Writing API Routes Tests
Comprehensive tests for AI writing API endpoints.
"""
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.services.ai.writing_service import (
    WritingTone,
    GrammarCheckResult,
    SummarizeResult,
    RewriteResult,
    ExpandResult,
    TranslateResult,
    GrammarIssue,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def app():
    """Create test FastAPI app with AI routes."""
    from backend.app.api.routes.ai import router
    from backend.app.api.middleware import limiter

    test_app = FastAPI()
    test_app.include_router(router, prefix="/api")
    limiter.enabled = False
    yield test_app
    limiter.enabled = True


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_writing_service():
    """Mock writing service."""
    with patch('backend.app.api.routes.ai.writing_service') as mock:
        yield mock


# =============================================================================
# GRAMMAR CHECK ENDPOINT TESTS
# =============================================================================


class TestGrammarCheckEndpoint:
    """Tests for POST /documents/{document_id}/ai/grammar."""

    def test_grammar_check_success(self, client, mock_writing_service):
        """Successful grammar check returns result."""
        mock_result = GrammarCheckResult(
            issues=[],
            corrected_text="Hello world.",
            issue_count=0,
            score=100.0,
        )
        mock_writing_service.check_grammar = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/grammar",
            json={"text": "Hello world."}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 100.0
        assert data["issue_count"] == 0

    def test_grammar_check_with_issues(self, client, mock_writing_service):
        """Grammar check returns issues."""
        issue = GrammarIssue(
            start=0, end=3, original="teh", suggestion="the",
            issue_type="spelling", explanation="Typo",
        )
        mock_result = GrammarCheckResult(
            issues=[issue],
            corrected_text="the quick fox",
            issue_count=1,
            score=85.0,
        )
        mock_writing_service.check_grammar = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/grammar",
            json={"text": "teh quick fox"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["issues"]) == 1
        assert data["issues"][0]["original"] == "teh"

    def test_grammar_check_with_language(self, client, mock_writing_service):
        """Grammar check with language parameter."""
        mock_result = GrammarCheckResult(
            issues=[], corrected_text="Bonjour", issue_count=0, score=100.0,
        )
        mock_writing_service.check_grammar = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/grammar",
            json={"text": "Bonjour", "language": "fr"}
        )

        assert response.status_code == 200
        mock_writing_service.check_grammar.assert_called_once()
        call_kwargs = mock_writing_service.check_grammar.call_args[1]
        assert call_kwargs["language"] == "fr"

    def test_grammar_check_with_strict_mode(self, client, mock_writing_service):
        """Grammar check with strict mode."""
        mock_result = GrammarCheckResult(
            issues=[], corrected_text="text", issue_count=0, score=100.0,
        )
        mock_writing_service.check_grammar = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/grammar",
            json={"text": "text", "strict": True}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.check_grammar.call_args[1]
        assert call_kwargs["strict"] is True

    def test_grammar_check_missing_text(self, client, mock_writing_service):
        """Grammar check without text returns error."""
        response = client.post(
            "/api/documents/doc-123/ai/grammar",
            json={}
        )

        assert response.status_code == 422  # Validation error

    def test_grammar_check_service_error(self, client, mock_writing_service):
        """Grammar check service error returns 500."""
        mock_writing_service.check_grammar = AsyncMock(
            side_effect=Exception("Service error")
        )

        response = client.post(
            "/api/documents/doc-123/ai/grammar",
            json={"text": "text"}
        )

        assert response.status_code == 500


# =============================================================================
# SUMMARIZE ENDPOINT TESTS
# =============================================================================


class TestSummarizeEndpoint:
    """Tests for POST /documents/{document_id}/ai/summarize."""

    def test_summarize_success(self, client, mock_writing_service):
        """Successful summarization returns result."""
        mock_result = SummarizeResult(
            summary="Brief summary.",
            key_points=["Point 1", "Point 2"],
            word_count_original=100,
            word_count_summary=10,
            compression_ratio=0.1,
        )
        mock_writing_service.summarize = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/summarize",
            json={"text": "Long text " * 50}
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "key_points" in data

    def test_summarize_with_max_length(self, client, mock_writing_service):
        """Summarize with max_length parameter."""
        mock_result = SummarizeResult(
            summary="Short", key_points=[], word_count_original=100,
            word_count_summary=1, compression_ratio=0.01,
        )
        mock_writing_service.summarize = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/summarize",
            json={"text": "text", "max_length": 50}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.summarize.call_args[1]
        assert call_kwargs["max_length"] == 50

    def test_summarize_with_style(self, client, mock_writing_service):
        """Summarize with style parameter."""
        mock_result = SummarizeResult(
            summary="• Point", key_points=["Point"], word_count_original=100,
            word_count_summary=2, compression_ratio=0.02,
        )
        mock_writing_service.summarize = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/summarize",
            json={"text": "text", "style": "bullet_points"}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.summarize.call_args[1]
        assert call_kwargs["style"] == "bullet_points"

    def test_summarize_missing_text(self, client, mock_writing_service):
        """Summarize without text returns error."""
        response = client.post(
            "/api/documents/doc-123/ai/summarize",
            json={}
        )

        assert response.status_code == 422

    def test_summarize_service_error(self, client, mock_writing_service):
        """Summarize service error returns 500."""
        mock_writing_service.summarize = AsyncMock(
            side_effect=Exception("Service error")
        )

        response = client.post(
            "/api/documents/doc-123/ai/summarize",
            json={"text": "text"}
        )

        assert response.status_code == 500


# =============================================================================
# REWRITE ENDPOINT TESTS
# =============================================================================


class TestRewriteEndpoint:
    """Tests for POST /documents/{document_id}/ai/rewrite."""

    def test_rewrite_success(self, client, mock_writing_service):
        """Successful rewrite returns result."""
        mock_result = RewriteResult(
            rewritten_text="Professionally written text.",
            tone="professional",
            changes_made=["Improved clarity"],
        )
        mock_writing_service.rewrite = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/rewrite",
            json={"text": "some text"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "rewritten_text" in data
        assert data["tone"] == "professional"

    @pytest.mark.parametrize("tone", [t.value for t in WritingTone])
    def test_rewrite_all_tones(self, client, mock_writing_service, tone: str):
        """Rewrite endpoint accepts all tones."""
        mock_result = RewriteResult(
            rewritten_text="text", tone=tone, changes_made=[],
        )
        mock_writing_service.rewrite = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/rewrite",
            json={"text": "text", "tone": tone}
        )

        assert response.status_code == 200

    def test_rewrite_invalid_tone_defaults(self, client, mock_writing_service):
        """Invalid tone defaults to professional."""
        mock_result = RewriteResult(
            rewritten_text="text", tone="professional", changes_made=[],
        )
        mock_writing_service.rewrite = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/rewrite",
            json={"text": "text", "tone": "invalid_tone"}
        )

        # Invalid tones are now properly rejected at the validation layer
        assert response.status_code == 422

    def test_rewrite_with_preserve_meaning(self, client, mock_writing_service):
        """Rewrite with preserve_meaning parameter."""
        mock_result = RewriteResult(
            rewritten_text="text", tone="professional", changes_made=[],
        )
        mock_writing_service.rewrite = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/rewrite",
            json={"text": "text", "preserve_meaning": False}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.rewrite.call_args[1]
        assert call_kwargs["preserve_meaning"] is False

    def test_rewrite_missing_text(self, client, mock_writing_service):
        """Rewrite without text returns error."""
        response = client.post(
            "/api/documents/doc-123/ai/rewrite",
            json={}
        )

        assert response.status_code == 422

    def test_rewrite_service_error(self, client, mock_writing_service):
        """Rewrite service error returns 500."""
        mock_writing_service.rewrite = AsyncMock(
            side_effect=Exception("Service error")
        )

        response = client.post(
            "/api/documents/doc-123/ai/rewrite",
            json={"text": "text"}
        )

        assert response.status_code == 500


# =============================================================================
# EXPAND ENDPOINT TESTS
# =============================================================================


class TestExpandEndpoint:
    """Tests for POST /documents/{document_id}/ai/expand."""

    def test_expand_success(self, client, mock_writing_service):
        """Successful expand returns result."""
        mock_result = ExpandResult(
            expanded_text="Much longer expanded text.",
            sections_added=["Introduction"],
            word_count_original=5,
            word_count_expanded=50,
        )
        mock_writing_service.expand = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/expand",
            json={"text": "short text"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "expanded_text" in data
        assert data["word_count_expanded"] > data["word_count_original"]

    def test_expand_with_target_length(self, client, mock_writing_service):
        """Expand with target_length parameter."""
        mock_result = ExpandResult(
            expanded_text="text " * 100, sections_added=[],
            word_count_original=10, word_count_expanded=100,
        )
        mock_writing_service.expand = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/expand",
            json={"text": "text", "target_length": 100}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.expand.call_args[1]
        assert call_kwargs["target_length"] == 100

    def test_expand_with_examples(self, client, mock_writing_service):
        """Expand with add_examples parameter."""
        mock_result = ExpandResult(
            expanded_text="text with examples", sections_added=["Examples"],
            word_count_original=10, word_count_expanded=50,
        )
        mock_writing_service.expand = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/expand",
            json={"text": "text", "add_examples": True}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.expand.call_args[1]
        assert call_kwargs["add_examples"] is True

    def test_expand_with_details(self, client, mock_writing_service):
        """Expand with add_details parameter."""
        mock_result = ExpandResult(
            expanded_text="text with details", sections_added=["Details"],
            word_count_original=10, word_count_expanded=50,
        )
        mock_writing_service.expand = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/expand",
            json={"text": "text", "add_details": True}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.expand.call_args[1]
        assert call_kwargs["add_details"] is True

    def test_expand_missing_text(self, client, mock_writing_service):
        """Expand without text returns error."""
        response = client.post(
            "/api/documents/doc-123/ai/expand",
            json={}
        )

        assert response.status_code == 422

    def test_expand_service_error(self, client, mock_writing_service):
        """Expand service error returns 500."""
        mock_writing_service.expand = AsyncMock(
            side_effect=Exception("Service error")
        )

        response = client.post(
            "/api/documents/doc-123/ai/expand",
            json={"text": "text"}
        )

        assert response.status_code == 500


# =============================================================================
# TRANSLATE ENDPOINT TESTS
# =============================================================================


class TestTranslateEndpoint:
    """Tests for POST /documents/{document_id}/ai/translate."""

    def test_translate_success(self, client, mock_writing_service):
        """Successful translation returns result."""
        mock_result = TranslateResult(
            translated_text="Hola mundo",
            source_language="English",
            target_language="Spanish",
            confidence=0.95,
        )
        mock_writing_service.translate = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/translate",
            json={"text": "Hello world", "target_language": "Spanish"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["translated_text"] == "Hola mundo"
        assert data["target_language"] == "Spanish"

    def test_translate_with_source_language(self, client, mock_writing_service):
        """Translate with source_language parameter."""
        mock_result = TranslateResult(
            translated_text="Hello", source_language="German",
            target_language="English", confidence=0.9,
        )
        mock_writing_service.translate = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/translate",
            json={
                "text": "Hallo",
                "target_language": "English",
                "source_language": "German"
            }
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.translate.call_args[1]
        assert call_kwargs["source_language"] == "German"

    def test_translate_preserve_formatting(self, client, mock_writing_service):
        """Translate with preserve_formatting parameter."""
        mock_result = TranslateResult(
            translated_text="• Point", source_language="English",
            target_language="Spanish", confidence=0.9,
        )
        mock_writing_service.translate = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc-123/ai/translate",
            json={
                "text": "• Item",
                "target_language": "Spanish",
                "preserve_formatting": True
            }
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.translate.call_args[1]
        assert call_kwargs["preserve_formatting"] is True

    def test_translate_missing_text(self, client, mock_writing_service):
        """Translate without text returns error."""
        response = client.post(
            "/api/documents/doc-123/ai/translate",
            json={"target_language": "Spanish"}
        )

        assert response.status_code == 422

    def test_translate_missing_target_language(self, client, mock_writing_service):
        """Translate without target_language returns error."""
        response = client.post(
            "/api/documents/doc-123/ai/translate",
            json={"text": "Hello"}
        )

        assert response.status_code == 422

    def test_translate_service_error(self, client, mock_writing_service):
        """Translate service error returns 500."""
        mock_writing_service.translate = AsyncMock(
            side_effect=Exception("Service error")
        )

        response = client.post(
            "/api/documents/doc-123/ai/translate",
            json={"text": "text", "target_language": "Spanish"}
        )

        assert response.status_code == 500


# =============================================================================
# GENERATE CONTENT ENDPOINT TESTS
# =============================================================================


class TestGenerateContentEndpoint:
    """Tests for POST /ai/generate."""

    def test_generate_success(self, client, mock_writing_service):
        """Successful generation returns content."""
        mock_writing_service.generate_content = AsyncMock(
            return_value="Generated content here."
        )

        response = client.post(
            "/api/ai/generate",
            json={"prompt": "Write about AI"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_generate_with_context(self, client, mock_writing_service):
        """Generate with context parameter."""
        mock_writing_service.generate_content = AsyncMock(
            return_value="Contextual content."
        )

        response = client.post(
            "/api/ai/generate",
            json={"prompt": "Continue", "context": "Previous text"}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.generate_content.call_args[1]
        assert call_kwargs["context"] == "Previous text"

    def test_generate_with_tone(self, client, mock_writing_service):
        """Generate with tone parameter."""
        mock_writing_service.generate_content = AsyncMock(
            return_value="Casual content."
        )

        response = client.post(
            "/api/ai/generate",
            json={"prompt": "Write", "tone": "casual"}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.generate_content.call_args[1]
        assert call_kwargs["tone"] == WritingTone.CASUAL

    def test_generate_with_max_length(self, client, mock_writing_service):
        """Generate with max_length parameter."""
        mock_writing_service.generate_content = AsyncMock(
            return_value="Short content."
        )

        response = client.post(
            "/api/ai/generate",
            json={"prompt": "Write", "max_length": 50}
        )

        assert response.status_code == 200
        call_kwargs = mock_writing_service.generate_content.call_args[1]
        assert call_kwargs["max_length"] == 50

    def test_generate_missing_prompt(self, client, mock_writing_service):
        """Generate without prompt returns error."""
        response = client.post(
            "/api/ai/generate",
            json={}
        )

        assert response.status_code == 422

    def test_generate_service_error(self, client, mock_writing_service):
        """Generate service error returns 500."""
        mock_writing_service.generate_content = AsyncMock(
            side_effect=Exception("Service error")
        )

        response = client.post(
            "/api/ai/generate",
            json={"prompt": "Write"}
        )

        assert response.status_code == 500


# =============================================================================
# UTILITY ENDPOINT TESTS
# =============================================================================


class TestUtilityEndpoints:
    """Tests for utility endpoints."""

    def test_get_tones(self, client):
        """GET /tones returns all available tones."""
        response = client.get("/api/tones")

        assert response.status_code == 200
        data = response.json()
        assert "tones" in data
        assert len(data["tones"]) == 8  # 8 WritingTone values

    def test_get_tones_format(self, client):
        """GET /tones returns correct format."""
        response = client.get("/api/tones")

        data = response.json()
        for tone in data["tones"]:
            assert "value" in tone
            assert "label" in tone

    def test_health_check(self, client):
        """GET /health returns AI service status."""
        # The health endpoint reads settings directly, just check it returns 200
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert "openai_configured" in data
        assert "services" in data

    def test_health_check_structure(self, client):
        """GET /health returns expected structure."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert "model" in data
        assert "services" in data
        assert "writing" in data["services"]
        assert "spreadsheet" in data["services"]


# =============================================================================
# DOCUMENT ID TESTS
# =============================================================================


class TestDocumentIdHandling:
    """Tests for document ID handling in endpoints."""

    def test_grammar_various_document_ids(self, client, mock_writing_service):
        """Grammar check accepts various document ID formats."""
        mock_result = GrammarCheckResult(
            issues=[], corrected_text="text", issue_count=0, score=100.0,
        )
        mock_writing_service.check_grammar = AsyncMock(return_value=mock_result)

        doc_ids = ["doc-123", "uuid-abc-def", "12345", "doc_with_underscore"]
        for doc_id in doc_ids:
            response = client.post(
                f"/api/documents/{doc_id}/ai/grammar",
                json={"text": "text"}
            )
            assert response.status_code == 200

    def test_summarize_various_document_ids(self, client, mock_writing_service):
        """Summarize accepts various document ID formats."""
        mock_result = SummarizeResult(
            summary="summary", key_points=[], word_count_original=10,
            word_count_summary=1, compression_ratio=0.1,
        )
        mock_writing_service.summarize = AsyncMock(return_value=mock_result)

        doc_ids = ["doc-456", "another-id", "99999"]
        for doc_id in doc_ids:
            response = client.post(
                f"/api/documents/{doc_id}/ai/summarize",
                json={"text": "text"}
            )
            assert response.status_code == 200


# =============================================================================
# REQUEST VALIDATION TESTS
# =============================================================================


class TestRequestValidation:
    """Tests for request body validation."""

    def test_grammar_empty_text_accepted(self, client, mock_writing_service):
        """Grammar check accepts empty text."""
        mock_result = GrammarCheckResult(
            issues=[], corrected_text="", issue_count=0, score=100.0,
        )
        mock_writing_service.check_grammar = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc/ai/grammar",
            json={"text": ""}
        )

        # Empty text is now rejected at validation layer (min_length=1)
        assert response.status_code == 422

    def test_rewrite_default_tone(self, client, mock_writing_service):
        """Rewrite uses default tone when not specified."""
        mock_result = RewriteResult(
            rewritten_text="text", tone="professional", changes_made=[],
        )
        mock_writing_service.rewrite = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc/ai/rewrite",
            json={"text": "text"}  # No tone specified
        )

        assert response.status_code == 200

    def test_summarize_default_style(self, client, mock_writing_service):
        """Summarize uses default style when not specified."""
        mock_result = SummarizeResult(
            summary="summary", key_points=[], word_count_original=10,
            word_count_summary=1, compression_ratio=0.1,
        )
        mock_writing_service.summarize = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc/ai/summarize",
            json={"text": "text"}  # No style specified
        )

        assert response.status_code == 200

    def test_expand_default_options(self, client, mock_writing_service):
        """Expand uses default options when not specified."""
        mock_result = ExpandResult(
            expanded_text="text", sections_added=[],
            word_count_original=1, word_count_expanded=1,
        )
        mock_writing_service.expand = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc/ai/expand",
            json={"text": "text"}  # No options specified
        )

        assert response.status_code == 200

    def test_translate_default_options(self, client, mock_writing_service):
        """Translate uses default options when not specified."""
        mock_result = TranslateResult(
            translated_text="hola", source_language="English",
            target_language="Spanish", confidence=0.9,
        )
        mock_writing_service.translate = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc/ai/translate",
            json={"text": "hello", "target_language": "Spanish"}
        )

        assert response.status_code == 200


# =============================================================================
# LARGE PAYLOAD TESTS
# =============================================================================


class TestLargePayloads:
    """Tests for handling large payloads."""

    def test_grammar_large_text(self, client, mock_writing_service):
        """Grammar check handles large text."""
        large_text = "word " * 10000
        mock_result = GrammarCheckResult(
            issues=[], corrected_text=large_text, issue_count=0, score=100.0,
        )
        mock_writing_service.check_grammar = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc/ai/grammar",
            json={"text": large_text}
        )

        assert response.status_code == 200

    def test_summarize_large_text(self, client, mock_writing_service):
        """Summarize handles large text."""
        large_text = "word " * 10000
        mock_result = SummarizeResult(
            summary="summary", key_points=[], word_count_original=10000,
            word_count_summary=10, compression_ratio=0.001,
        )
        mock_writing_service.summarize = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc/ai/summarize",
            json={"text": large_text}
        )

        assert response.status_code == 200

    def test_translate_large_text(self, client, mock_writing_service):
        """Translate handles large text."""
        large_text = "word " * 5000
        mock_result = TranslateResult(
            translated_text="palabra " * 5000, source_language="English",
            target_language="Spanish", confidence=0.9,
        )
        mock_writing_service.translate = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/documents/doc/ai/translate",
            json={"text": large_text, "target_language": "Spanish"}
        )

        assert response.status_code == 200
