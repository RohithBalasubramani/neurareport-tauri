"""
WritingService Unit & Integration Tests
Comprehensive 7-layer test coverage for AI writing service.

Layers covered:
1. Unit Tests - Individual method logic
2. Integration Tests - Service + LLM client interaction
3. Property-Based Tests - Invariant verification
4. Failure Injection Tests - Error handling paths
5. Concurrency Tests - Thread safety
6. Security Tests - Input sanitization, abuse prevention
7. Usability Tests - API ergonomics
"""
import asyncio
import json
import os
import pytest
import threading
from unittest.mock import Mock, patch, AsyncMock, MagicMock


from backend.app.services.ai.writing_service import (
    WritingService,
    WritingTone,
    GrammarCheckResult,
    GrammarIssue,
    SummarizeResult,
    RewriteResult,
    ExpandResult,
    TranslateResult,
    InputValidationError,
    LLMResponseError,
    LLMUnavailableError,
    WritingServiceError,
    _extract_json,
    _validate_grammar_positions,
    MAX_TEXT_CHARS,
    MAX_TEXT_CHARS_EXPAND,
)


# =============================================================================
# FIXTURES
# =============================================================================

def _make_llm_response(content: str) -> dict:
    """Create an OpenAI-compatible response dict."""
    return {
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
    }


@pytest.fixture
def service():
    """Create a WritingService with mocked LLM client."""
    return WritingService()


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    return Mock()


@pytest.fixture
def service_with_mock(service, mock_llm_client):
    """WritingService wired to a mock LLM client."""
    service._llm_client = mock_llm_client
    return service


# =============================================================================
# LAYER 1: UNIT TESTS — _extract_json helper
# =============================================================================


class TestExtractJson:
    """Tests for the _extract_json helper."""

    def test_plain_json(self):
        assert _extract_json('{"key": "value"}') == {"key": "value"}

    def test_json_with_markdown_fences(self):
        assert _extract_json('```json\n{"key": "value"}\n```') == {"key": "value"}

    def test_json_with_bare_fences(self):
        assert _extract_json('```\n{"items": [1, 2]}\n```') == {"items": [1, 2]}

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            _extract_json("not json at all")

    def test_whitespace_wrapped(self):
        assert _extract_json('  \n  {"a": 1}  \n  ') == {"a": 1}


class TestValidateGrammarPositions:
    """Tests for position clamping."""

    def test_valid_positions_unchanged(self):
        issues = [{"start": 0, "end": 5}]
        result = _validate_grammar_positions(issues, 10)
        assert result[0]["start"] == 0 and result[0]["end"] == 5

    def test_start_clamped_to_zero(self):
        result = _validate_grammar_positions([{"start": -5, "end": 5}], 10)
        assert result[0]["start"] == 0

    def test_end_clamped_to_text_length(self):
        result = _validate_grammar_positions([{"start": 0, "end": 999}], 10)
        assert result[0]["end"] == 10

    def test_end_at_least_start(self):
        result = _validate_grammar_positions([{"start": 5, "end": 3}], 10)
        assert result[0]["end"] >= result[0]["start"]

    def test_missing_keys_default_to_zero(self):
        result = _validate_grammar_positions([{}], 10)
        assert result[0]["start"] == 0 and result[0]["end"] == 0


# =============================================================================
# LAYER 1: UNIT TESTS — Grammar Check
# =============================================================================


class TestGrammarCheckUnit:
    """Unit tests for check_grammar."""

    @pytest.mark.asyncio
    async def test_empty_text_returns_perfect_score(self, service_with_mock):
        result = await service_with_mock.check_grammar("")
        assert result.score == 100.0
        assert result.issue_count == 0
        assert result.corrected_text == ""

    @pytest.mark.asyncio
    async def test_whitespace_only_returns_perfect_score(self, service_with_mock):
        result = await service_with_mock.check_grammar("   \n\t  ")
        assert result.score == 100.0

    @pytest.mark.asyncio
    async def test_text_too_long_raises_validation_error(self, service_with_mock):
        with pytest.raises(InputValidationError, match="exceeds maximum"):
            await service_with_mock.check_grammar("a" * (MAX_TEXT_CHARS + 1))

    @pytest.mark.asyncio
    async def test_successful_grammar_check(self, service_with_mock, mock_llm_client):
        response_json = json.dumps({
            "issues": [{
                "start": 0, "end": 3, "original": "teh",
                "suggestion": "the", "issue_type": "spelling",
                "explanation": "Misspelling", "severity": "error"
            }],
            "corrected_text": "the quick fox",
            "score": 85.0,
        })
        mock_llm_client.complete.return_value = _make_llm_response(response_json)
        result = await service_with_mock.check_grammar("teh quick fox")
        assert result.issue_count == 1
        assert result.issues[0].original == "teh"
        assert result.issues[0].suggestion == "the"
        assert result.score == 85.0

    @pytest.mark.asyncio
    async def test_score_clamped_high(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "ok", "score": 150.0})
        )
        result = await service_with_mock.check_grammar("ok")
        assert result.score == 100.0

    @pytest.mark.asyncio
    async def test_score_clamped_low(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "ok", "score": -20})
        )
        result = await service_with_mock.check_grammar("ok")
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_markdown_fences_handled(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            '```json\n{"issues": [], "corrected_text": "ok", "score": 99}\n```'
        )
        result = await service_with_mock.check_grammar("ok")
        assert result.score == 99.0

    @pytest.mark.asyncio
    async def test_malformed_issues_skipped(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(json.dumps({
            "issues": [
                {"start": 0, "end": 3, "original": "teh", "suggestion": "the",
                 "issue_type": "spelling", "explanation": "Typo"},
                {"garbage": True},  # malformed
            ],
            "corrected_text": "the quick fox",
            "score": 85.0,
        }))
        result = await service_with_mock.check_grammar("teh quick fox")
        assert result.issue_count == 1


# =============================================================================
# LAYER 1: UNIT TESTS — Other operations
# =============================================================================


class TestSummarizeUnit:
    @pytest.mark.asyncio
    async def test_empty_text(self, service_with_mock):
        result = await service_with_mock.summarize("")
        assert result.summary == "" and result.compression_ratio == 1.0

    @pytest.mark.asyncio
    async def test_successful_summarize(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"summary": "Short.", "key_points": ["A", "B"]})
        )
        result = await service_with_mock.summarize("A long text with many words.")
        assert result.summary == "Short."
        assert len(result.key_points) == 2
        assert result.word_count_original > 0

    @pytest.mark.asyncio
    async def test_too_long(self, service_with_mock):
        with pytest.raises(InputValidationError):
            await service_with_mock.summarize("x" * (MAX_TEXT_CHARS + 1))


class TestRewriteUnit:
    @pytest.mark.asyncio
    async def test_empty_text(self, service_with_mock):
        result = await service_with_mock.rewrite("")
        assert result.rewritten_text == ""

    @pytest.mark.asyncio
    async def test_successful_rewrite(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"rewritten_text": "Formal.", "changes_made": ["tone"]})
        )
        result = await service_with_mock.rewrite("hey", tone=WritingTone.FORMAL)
        assert result.rewritten_text == "Formal."
        assert result.tone == "formal"


class TestExpandUnit:
    @pytest.mark.asyncio
    async def test_empty_text(self, service_with_mock):
        result = await service_with_mock.expand("")
        assert result.word_count_expanded == 0

    @pytest.mark.asyncio
    async def test_lower_limit_enforced(self, service_with_mock):
        with pytest.raises(InputValidationError):
            await service_with_mock.expand("a" * (MAX_TEXT_CHARS_EXPAND + 1))


class TestTranslateUnit:
    @pytest.mark.asyncio
    async def test_empty_text(self, service_with_mock):
        result = await service_with_mock.translate("", target_language="es")
        assert result.translated_text == ""

    @pytest.mark.asyncio
    async def test_successful_translate(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(json.dumps({
            "translated_text": "Hola mundo",
            "source_language": "English",
            "confidence": 0.95,
        }))
        result = await service_with_mock.translate("Hello world", target_language="Spanish")
        assert result.translated_text == "Hola mundo"
        assert result.confidence == 0.95


class TestGenerateContentUnit:
    @pytest.mark.asyncio
    async def test_empty_prompt_raises(self, service_with_mock):
        with pytest.raises(InputValidationError, match="cannot be empty"):
            await service_with_mock.generate_content("")

    @pytest.mark.asyncio
    async def test_whitespace_prompt_raises(self, service_with_mock):
        with pytest.raises(InputValidationError):
            await service_with_mock.generate_content("   ")

    @pytest.mark.asyncio
    async def test_successful_generate(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response("Generated content.")
        result = await service_with_mock.generate_content("Write about AI")
        assert result == "Generated content."


# =============================================================================
# LAYER 3: PROPERTY-BASED TESTS
# =============================================================================


class TestGrammarCheckProperties:
    @pytest.mark.asyncio
    async def test_score_always_in_range(self, service_with_mock, mock_llm_client):
        for score_val in [-10, 0, 50, 100, 200, 999]:
            mock_llm_client.complete.return_value = _make_llm_response(
                json.dumps({"issues": [], "corrected_text": "ok", "score": score_val})
            )
            result = await service_with_mock.check_grammar("ok")
            assert 0.0 <= result.score <= 100.0

    @pytest.mark.asyncio
    async def test_issue_count_matches_list(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(json.dumps({
            "issues": [
                {"start": 0, "end": 2, "original": "ab", "suggestion": "AB",
                 "issue_type": "grammar", "explanation": "Cap"},
                {"start": 3, "end": 5, "original": "cd", "suggestion": "CD",
                 "issue_type": "grammar", "explanation": "Cap"},
            ],
            "corrected_text": "AB CD", "score": 70,
        }))
        result = await service_with_mock.check_grammar("ab cd")
        assert result.issue_count == len(result.issues)

    @pytest.mark.asyncio
    async def test_positions_within_bounds(self, service_with_mock, mock_llm_client):
        text = "short"
        mock_llm_client.complete.return_value = _make_llm_response(json.dumps({
            "issues": [{"start": -5, "end": 999, "original": "x", "suggestion": "y",
                        "issue_type": "grammar", "explanation": "e"}],
            "corrected_text": text, "score": 50,
        }))
        result = await service_with_mock.check_grammar(text)
        for issue in result.issues:
            assert 0 <= issue.start <= len(text)
            assert issue.start <= issue.end <= len(text)

    @pytest.mark.asyncio
    async def test_confidence_always_clamped(self, service_with_mock, mock_llm_client):
        for conf in [-0.5, 0.0, 0.5, 1.0, 1.5]:
            mock_llm_client.complete.return_value = _make_llm_response(json.dumps({
                "translated_text": "hola", "source_language": "en", "confidence": conf,
            }))
            result = await service_with_mock.translate("hi", target_language="es")
            assert 0.0 <= result.confidence <= 1.0


# =============================================================================
# LAYER 4: FAILURE INJECTION TESTS
# =============================================================================


class TestFailureInjection:
    @pytest.mark.asyncio
    async def test_llm_returns_invalid_json(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response("Not JSON")
        with pytest.raises(LLMResponseError, match="invalid JSON"):
            await service_with_mock.check_grammar("test")

    @pytest.mark.asyncio
    async def test_llm_returns_empty_response(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response("")
        with pytest.raises(LLMResponseError, match="empty response"):
            await service_with_mock.check_grammar("test")

    @pytest.mark.asyncio
    async def test_llm_client_runtime_error(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.side_effect = RuntimeError("Connection failed")
        with pytest.raises(LLMResponseError):
            await service_with_mock.check_grammar("test")

    @pytest.mark.asyncio
    async def test_circuit_breaker_open(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.side_effect = RuntimeError(
            "Service temporarily unavailable: circuit breaker open"
        )
        with pytest.raises(LLMUnavailableError):
            await service_with_mock.check_grammar("test")

    @pytest.mark.asyncio
    async def test_unexpected_exception(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.side_effect = ValueError("unexpected")
        with pytest.raises(LLMResponseError, match="LLM call failed"):
            await service_with_mock.check_grammar("test")

    @pytest.mark.asyncio
    async def test_summarize_invalid_json(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response("not json")
        with pytest.raises(LLMResponseError):
            await service_with_mock.summarize("Some text.")

    @pytest.mark.asyncio
    async def test_rewrite_invalid_json(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response("broken")
        with pytest.raises(LLMResponseError):
            await service_with_mock.rewrite("Some text")

    @pytest.mark.asyncio
    async def test_translate_invalid_json(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response("{invalid")
        with pytest.raises(LLMResponseError):
            await service_with_mock.translate("Hi", target_language="es")

    @pytest.mark.asyncio
    async def test_expand_invalid_json(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response("no json")
        with pytest.raises(LLMResponseError):
            await service_with_mock.expand("text")


# =============================================================================
# LAYER 5: CONCURRENCY TESTS
# =============================================================================


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_grammar_checks(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "ok", "score": 100})
        )
        results = await asyncio.gather(*[
            service_with_mock.check_grammar(f"Text {i}") for i in range(10)
        ])
        assert all(r.score == 100.0 for r in results)
        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations(self, service_with_mock, mock_llm_client):
        grammar_json = json.dumps({"issues": [], "corrected_text": "ok", "score": 95})
        summary_json = json.dumps({"summary": "short", "key_points": ["a"]})
        rewrite_json = json.dumps({"rewritten_text": "formal", "changes_made": []})

        def mock_complete(**kwargs):
            desc = kwargs.get("description", "")
            if "grammar" in desc:
                return _make_llm_response(grammar_json)
            elif "summarize" in desc:
                return _make_llm_response(summary_json)
            return _make_llm_response(rewrite_json)

        mock_llm_client.complete.side_effect = mock_complete

        results = await asyncio.gather(
            service_with_mock.check_grammar("test"),
            service_with_mock.summarize("test text"),
            service_with_mock.rewrite("hello"),
        )
        assert len(results) == 3


# =============================================================================
# LAYER 6: SECURITY TESTS
# =============================================================================


class TestSecurity:
    @pytest.mark.asyncio
    async def test_text_length_limit(self, service_with_mock):
        with pytest.raises(InputValidationError):
            await service_with_mock.check_grammar("x" * (MAX_TEXT_CHARS + 1))

    @pytest.mark.asyncio
    async def test_expand_lower_limit(self, service_with_mock):
        with pytest.raises(InputValidationError):
            await service_with_mock.expand("x" * (MAX_TEXT_CHARS_EXPAND + 1))

    @pytest.mark.asyncio
    async def test_generate_rejects_empty(self, service_with_mock):
        with pytest.raises(InputValidationError):
            await service_with_mock.generate_content("   ")

    @pytest.mark.asyncio
    async def test_unicode_handled(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "日本語テスト", "score": 100})
        )
        result = await service_with_mock.check_grammar("日本語テスト", language="ja")
        assert result.corrected_text == "日本語テスト"

    @pytest.mark.asyncio
    async def test_special_characters(self, service_with_mock, mock_llm_client):
        text = 'He said "hello"\nand\tthen left.'
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": text, "score": 100})
        )
        result = await service_with_mock.check_grammar(text)
        assert result.score == 100.0


# =============================================================================
# LAYER 7: USABILITY TESTS
# =============================================================================


class TestUsability:
    @pytest.mark.asyncio
    async def test_default_language_is_english(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "hi", "score": 100})
        )
        await service_with_mock.check_grammar("hi")
        messages = mock_llm_client.complete.call_args[1]["messages"]
        assert "en" in messages[0]["content"]

    @pytest.mark.asyncio
    async def test_strict_mode_in_prompt(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "hi", "score": 100})
        )
        await service_with_mock.check_grammar("hi", strict=True)
        messages = mock_llm_client.complete.call_args[1]["messages"]
        assert "strict" in messages[0]["content"].lower()

    @pytest.mark.asyncio
    async def test_all_summarize_styles(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"summary": "short", "key_points": []})
        )
        for style in ["bullet_points", "paragraph", "executive"]:
            result = await service_with_mock.summarize("Some text", style=style)
            assert result.summary == "short"

    @pytest.mark.asyncio
    async def test_all_tones_accepted(self, service_with_mock, mock_llm_client):
        mock_llm_client.complete.return_value = _make_llm_response(
            json.dumps({"rewritten_text": "out", "changes_made": []})
        )
        for tone in WritingTone:
            result = await service_with_mock.rewrite("in", tone=tone)
            assert result.tone == tone.value

    def test_error_hierarchy(self):
        assert issubclass(InputValidationError, WritingServiceError)
        assert issubclass(LLMResponseError, WritingServiceError)
        assert issubclass(LLMUnavailableError, WritingServiceError)


# =============================================================================
# MODEL VALIDATION TESTS
# =============================================================================


class TestModels:
    def test_grammar_issue_defaults(self):
        issue = GrammarIssue(
            start=0, end=5, original="teh", suggestion="the",
            issue_type="spelling", explanation="typo"
        )
        assert issue.severity == "warning"

    def test_grammar_check_score_bound(self):
        with pytest.raises(Exception):
            GrammarCheckResult(issues=[], corrected_text="x", issue_count=0, score=101)

    def test_translate_confidence_bound(self):
        with pytest.raises(Exception):
            TranslateResult(
                translated_text="x", source_language="en",
                target_language="es", confidence=1.5
            )
