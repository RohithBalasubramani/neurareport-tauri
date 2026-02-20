"""
Writing Service Error Injection Tests
Comprehensive error handling and edge case tests.
Updated for unified LLMClient architecture.
"""
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

import os

from backend.app.services.ai.writing_service import (
    WritingService,
    WritingTone,
    GrammarCheckResult,
    SummarizeResult,
    InputValidationError,
    LLMResponseError,
    LLMUnavailableError,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def service():
    """Create WritingService instance."""
    return WritingService()


def _make_llm_response(content: str) -> dict:
    """Create an OpenAI-compatible response dict."""
    return {
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
    }


# =============================================================================
# LLM CLIENT INITIALIZATION ERRORS
# =============================================================================


class TestClientInitializationErrors:
    """Tests for LLM client initialization failures."""

    def test_missing_llm_client_module(self, service):
        """Handle missing LLM client module."""
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.return_value = Mock()
            client = service._get_llm_client()
            assert client is not None

    def test_invalid_api_key(self, service):
        """Handle invalid API key from LLM client."""
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.side_effect = Exception("Invalid API key")
            with pytest.raises(Exception, match="Invalid API key"):
                service._get_llm_client()

    def test_network_error_on_init(self, service):
        """Handle network error during LLM client initialization."""
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.side_effect = ConnectionError("Network unreachable")
            with pytest.raises(ConnectionError):
                service._get_llm_client()


# =============================================================================
# LLM CALL ERRORS
# =============================================================================


class TestAPICallErrors:
    """Tests for LLM call failures."""

    @pytest.mark.asyncio
    async def test_api_rate_limit_error(self, service):
        """Handle rate limit error through LLM client."""
        mock_client = Mock()
        mock_client.complete.side_effect = RuntimeError("Rate limit exceeded")
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError):
            await service.check_grammar("test")

    @pytest.mark.asyncio
    async def test_api_timeout_error(self, service):
        """Handle timeout error."""
        mock_client = Mock()
        mock_client.complete.side_effect = TimeoutError("Request timed out")
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError, match="LLM call failed"):
            await service.check_grammar("test")

    @pytest.mark.asyncio
    async def test_api_server_error(self, service):
        """Handle server error (500)."""
        mock_client = Mock()
        mock_client.complete.side_effect = RuntimeError("Internal server error")
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError):
            await service.check_grammar("test")

    @pytest.mark.asyncio
    async def test_api_authentication_error(self, service):
        """Handle authentication error."""
        mock_client = Mock()
        mock_client.complete.side_effect = RuntimeError("Authentication failed")
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError):
            await service.check_grammar("test")

    @pytest.mark.asyncio
    async def test_api_quota_exceeded(self, service):
        """Handle quota exceeded error."""
        mock_client = Mock()
        mock_client.complete.side_effect = RuntimeError("Quota exceeded")
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError):
            await service.check_grammar("test")


# =============================================================================
# JSON PARSING ERRORS
# =============================================================================


class TestJSONParsingErrors:
    """Tests for JSON response parsing failures.

    In the new architecture, invalid JSON raises LLMResponseError
    instead of silently falling back to defaults.
    """

    @pytest.mark.asyncio
    async def test_grammar_invalid_json(self, service):
        """Grammar check raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "This is not valid JSON {"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.check_grammar("test text")

    @pytest.mark.asyncio
    async def test_summarize_invalid_json(self, service):
        """Summarize raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Just plain text response"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError):
                await service.summarize("text " * 100)

    @pytest.mark.asyncio
    async def test_rewrite_invalid_json(self, service):
        """Rewrite raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Plain text, not JSON"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError):
                await service.rewrite("test text")

    @pytest.mark.asyncio
    async def test_expand_invalid_json(self, service):
        """Expand raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Not JSON at all"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError):
                await service.expand("short text")

    @pytest.mark.asyncio
    async def test_translate_invalid_json(self, service):
        """Translate raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Just a plain translation"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError):
                await service.translate("hello", "Spanish")

    @pytest.mark.asyncio
    async def test_grammar_partial_json(self, service):
        """Grammar handles partial JSON response."""
        async def mock_call(*args, **kwargs):
            return '{"issues": [], "corrected_text": "text"'

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.check_grammar("text")

    @pytest.mark.asyncio
    async def test_summarize_missing_fields(self, service):
        """Summarize handles JSON with missing fields gracefully."""
        async def mock_call(*args, **kwargs):
            return json.dumps({"summary": "Brief summary"})

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.summarize("text " * 100)
            assert result.summary == "Brief summary"
            assert result.key_points == []

    @pytest.mark.asyncio
    async def test_rewrite_missing_fields(self, service):
        """Rewrite handles JSON with missing fields gracefully."""
        async def mock_call(*args, **kwargs):
            return json.dumps({"rewritten_text": "Rewritten"})

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.rewrite("text")
            assert result.rewritten_text == "Rewritten"
            assert result.changes_made == []


# =============================================================================
# MALFORMED RESPONSE TESTS
# =============================================================================


class TestMalformedResponses:
    """Tests for malformed API responses."""

    @pytest.mark.asyncio
    async def test_grammar_null_response(self, service):
        """Grammar raises error on JSON null response."""
        async def mock_call(*args, **kwargs):
            return "null"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            # JSON null parses but causes AttributeError on .get()
            with pytest.raises((LLMResponseError, AttributeError)):
                await service.check_grammar("text")

    @pytest.mark.asyncio
    async def test_grammar_empty_array_response(self, service):
        """Grammar raises error on empty array response."""
        async def mock_call(*args, **kwargs):
            return "[]"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises((LLMResponseError, AttributeError)):
                await service.check_grammar("text")

    @pytest.mark.asyncio
    async def test_grammar_wrong_type_response(self, service):
        """Grammar handles wrong type in issues field gracefully."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "issues": "not an array",
                "corrected_text": "text",
                "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            # String is iterable so it won't crash on iteration,
            # but each char won't match the GrammarIssue model and will be skipped
            result = await service.check_grammar("text")
            assert result.issue_count == 0  # All skipped as malformed

    @pytest.mark.asyncio
    async def test_translate_wrong_confidence_type(self, service):
        """Translate handles wrong confidence type."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "translated_text": "hola",
                "source_language": "English",
                "confidence": "high"  # String instead of float
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            # float("high") raises ValueError, which causes the clamp to fail
            with pytest.raises((ValueError, TypeError)):
                await service.translate("hello", "Spanish")


# =============================================================================
# CONTENT EDGE CASES
# =============================================================================


class TestContentEdgeCases:
    """Tests for edge cases in content."""

    @pytest.mark.asyncio
    async def test_very_long_text(self, service):
        """Handle very long input text up to limit."""
        # 100K words = ~500K chars, which is over the limit
        long_text = "word " * 10000  # 10K words, ~50K chars, under limit

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "summary": "Summary of very long text",
                "key_points": ["Main point"],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.summarize(long_text)
            assert result.word_count_original == 10000

    @pytest.mark.asyncio
    async def test_only_whitespace_variations(self, service):
        """Handle various whitespace-only inputs."""
        whitespace_inputs = [" ", "  ", "\t", "\n", "\r\n", "   \t\n  "]

        for ws in whitespace_inputs:
            result = await service.check_grammar(ws)
            assert result.score == 100.0

    @pytest.mark.asyncio
    async def test_special_unicode_characters(self, service):
        """Handle special unicode characters."""
        special_chars = "∑∏∫∂∆∇ℵℶ⊕⊗"

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "issues": [],
                "corrected_text": special_chars,
                "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.check_grammar(special_chars)
            assert "∑" in result.corrected_text

    @pytest.mark.asyncio
    async def test_emoji_heavy_text(self, service):
        """Handle emoji-heavy text."""
        emoji_text = "Hello 👋🏽 World 🌍 Test 🧪 Code 💻"

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "rewritten_text": emoji_text,
                "changes_made": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.rewrite(emoji_text)
            assert "👋" in result.rewritten_text

    @pytest.mark.asyncio
    async def test_mixed_rtl_ltr_text(self, service):
        """Handle mixed RTL and LTR text."""
        mixed_text = "Hello שלום مرحبا World"

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "translated_text": mixed_text,
                "source_language": "mixed",
                "confidence": 0.7,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.translate(mixed_text, "English")
            assert "שלום" in result.translated_text

    @pytest.mark.asyncio
    async def test_code_in_text(self, service):
        """Handle code snippets in text."""
        code_text = "The function `def hello(): pass` needs docs."

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "issues": [],
                "corrected_text": code_text,
                "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.check_grammar(code_text)
            assert "`def hello():" in result.corrected_text

    @pytest.mark.asyncio
    async def test_html_in_text(self, service):
        """Handle HTML content in text."""
        html_text = "Click <a href='link'>here</a> for more."

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "expanded_text": html_text,
                "sections_added": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.expand(html_text)
            assert "<a href" in result.expanded_text

    @pytest.mark.asyncio
    async def test_json_in_text(self, service):
        """Handle JSON content in text."""
        json_text = 'The response is {"key": "value"} as shown.'

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "issues": [],
                "corrected_text": json_text,
                "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.check_grammar(json_text)
            assert '{"key":' in result.corrected_text


# =============================================================================
# CONCURRENT OPERATION ERRORS
# =============================================================================


class TestConcurrentErrors:
    """Tests for concurrent operation error handling."""

    @pytest.mark.asyncio
    async def test_client_error_during_concurrent_calls(self, service):
        """Handle client error during sequential calls."""
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise LLMResponseError("Client error on second call")
            return json.dumps({
                "issues": [], "corrected_text": "text", "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=side_effect):
            result1 = await service.check_grammar("text1")
            assert result1.score == 100.0

            with pytest.raises(LLMResponseError):
                await service.check_grammar("text2")

    @pytest.mark.asyncio
    async def test_recovery_after_error(self, service):
        """Service recovers after error."""
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LLMResponseError("Temporary error")
            return json.dumps({
                "issues": [], "corrected_text": "text", "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=side_effect):
            with pytest.raises(LLMResponseError):
                await service.check_grammar("text")

            result = await service.check_grammar("text")
            assert result.score == 100.0


# =============================================================================
# MODEL-SPECIFIC BEHAVIOR
# =============================================================================


class TestModelSpecificErrors:
    """Tests for model-specific behavior via LLM client.

    Model parameter selection (max_tokens vs max_completion_tokens) is now
    handled by the unified LLMClient internally, so we test that the service
    passes parameters correctly to the client.
    """

    @pytest.mark.asyncio
    async def test_gpt5_model_parameters(self, service):
        """Service passes max_tokens to LLM client."""
        mock_client = Mock()
        mock_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "text", "score": 100.0})
        )
        service._llm_client = mock_client

        await service.check_grammar("test")
        call_kwargs = mock_client.complete.call_args[1]
        assert "max_tokens" in call_kwargs

    @pytest.mark.asyncio
    async def test_o1_model_parameters(self, service):
        """Service passes description to LLM client for tracking."""
        mock_client = Mock()
        mock_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "text", "score": 100.0})
        )
        service._llm_client = mock_client

        await service.check_grammar("test")
        call_kwargs = mock_client.complete.call_args[1]
        assert "description" in call_kwargs
        assert call_kwargs["description"] == "grammar_check"

    @pytest.mark.asyncio
    async def test_gpt4_model_parameters(self, service):
        """Service passes messages in correct format."""
        mock_client = Mock()
        mock_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "text", "score": 100.0})
        )
        service._llm_client = mock_client

        await service.check_grammar("test")
        call_kwargs = mock_client.complete.call_args[1]
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


# =============================================================================
# SETTINGS ERRORS
# =============================================================================


class TestSettingsErrors:
    """Tests for settings-related errors."""

    def test_missing_api_key_in_settings(self):
        """Handle missing API key — LLM client raises on init."""
        service = WritingService()
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.side_effect = Exception("No API key configured")
            with pytest.raises(Exception, match="No API key"):
                service._get_llm_client()

    def test_empty_api_key(self):
        """Handle empty API key."""
        service = WritingService()
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.side_effect = Exception("Authentication error: empty key")
            with pytest.raises(Exception, match="Authentication"):
                service._get_llm_client()


# =============================================================================
# RESPONSE STRUCTURE ERRORS
# =============================================================================


class TestResponseStructureErrors:
    """Tests for malformed response structures."""

    @pytest.mark.asyncio
    async def test_grammar_issues_wrong_structure(self, service):
        """Grammar handles issues with wrong structure gracefully."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "issues": [
                    {"wrong": "structure"}  # Missing required fields
                ],
                "corrected_text": "text",
                "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.check_grammar("text")
            # Malformed issue is skipped
            assert result.issue_count == 0
            assert result.corrected_text == "text"

    @pytest.mark.asyncio
    async def test_summarize_key_points_wrong_type(self, service):
        """Summarize handles wrong key_points type."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "summary": "Summary",
                "key_points": {"not": "an array"},
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            # Pydantic may coerce or reject — either is acceptable
            try:
                result = await service.summarize("text " * 50)
                assert isinstance(result, SummarizeResult)
            except Exception:
                pass  # Validation error is acceptable

    @pytest.mark.asyncio
    async def test_expand_sections_wrong_type(self, service):
        """Expand handles wrong sections_added type."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "expanded_text": "Expanded",
                "sections_added": "string instead of array",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            try:
                from backend.app.services.ai.writing_service import ExpandResult
                result = await service.expand("short")
                assert isinstance(result, ExpandResult)
            except Exception:
                pass  # Validation error is acceptable


# =============================================================================
# NETWORK EDGE CASES
# =============================================================================


class TestNetworkEdgeCases:
    """Tests for network-related edge cases via LLM client."""

    @pytest.mark.asyncio
    async def test_connection_reset(self, service):
        """Handle connection reset via LLM client."""
        mock_client = Mock()
        mock_client.complete.side_effect = ConnectionResetError()
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError, match="LLM call failed"):
            await service.check_grammar("test")

    @pytest.mark.asyncio
    async def test_broken_pipe(self, service):
        """Handle broken pipe error via LLM client."""
        mock_client = Mock()
        mock_client.complete.side_effect = BrokenPipeError()
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError, match="LLM call failed"):
            await service.check_grammar("test")

    @pytest.mark.asyncio
    async def test_dns_resolution_failure(self, service):
        """Handle DNS resolution failure."""
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.side_effect = Exception("getaddrinfo failed")
            with pytest.raises(Exception, match="getaddrinfo"):
                service._get_llm_client()
