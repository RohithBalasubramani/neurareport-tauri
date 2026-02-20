"""
Writing Service Models Tests
Comprehensive tests for AI writing service data models and enums.
"""
import pytest
from pydantic import ValidationError

from backend.app.services.ai.writing_service import (
    WritingTone,
    GrammarIssue,
    GrammarCheckResult,
    SummarizeResult,
    RewriteResult,
    ExpandResult,
    TranslateResult,
)


# =============================================================================
# WRITINGTONE ENUM TESTS
# =============================================================================


class TestWritingToneEnum:
    """Tests for WritingTone enumeration."""

    def test_all_tones_exist(self):
        """All expected tones are defined."""
        expected_tones = [
            "professional", "casual", "formal", "friendly",
            "academic", "technical", "persuasive", "concise",
        ]
        actual_tones = [t.value for t in WritingTone]
        assert sorted(actual_tones) == sorted(expected_tones)

    def test_tone_count(self):
        """Correct number of tones defined."""
        assert len(WritingTone) == 8

    def test_tone_values_are_strings(self):
        """All tone values are strings."""
        for tone in WritingTone:
            assert isinstance(tone.value, str)

    @pytest.mark.parametrize("tone_value", [
        "professional", "casual", "formal", "friendly",
        "academic", "technical", "persuasive", "concise",
    ])
    def test_tone_from_value(self, tone_value: str):
        """Can create tone from string value."""
        tone = WritingTone(tone_value)
        assert tone.value == tone_value

    def test_invalid_tone_raises_error(self):
        """Invalid tone value raises ValueError."""
        with pytest.raises(ValueError):
            WritingTone("invalid_tone")

    def test_tone_is_str_subclass(self):
        """WritingTone is a string enum."""
        assert issubclass(WritingTone, str)
        assert WritingTone.PROFESSIONAL == "professional"


# =============================================================================
# GRAMMARISSUE MODEL TESTS
# =============================================================================


class TestGrammarIssueModel:
    """Tests for GrammarIssue data model."""

    def test_create_valid_issue(self):
        """Create valid grammar issue."""
        issue = GrammarIssue(
            start=0,
            end=5,
            original="teh",
            suggestion="the",
            issue_type="spelling",
            explanation="Common misspelling",
        )
        assert issue.start == 0
        assert issue.end == 5
        assert issue.original == "teh"
        assert issue.suggestion == "the"
        assert issue.severity == "warning"  # default

    def test_issue_with_custom_severity(self):
        """Issue with custom severity."""
        issue = GrammarIssue(
            start=10,
            end=15,
            original="their",
            suggestion="there",
            issue_type="grammar",
            explanation="Wrong word",
            severity="error",
        )
        assert issue.severity == "error"

    def test_issue_types(self):
        """Different issue types are accepted."""
        for issue_type in ["grammar", "spelling", "punctuation", "style"]:
            issue = GrammarIssue(
                start=0,
                end=10,
                original="test",
                suggestion="test",
                issue_type=issue_type,
                explanation="test",
            )
            assert issue.issue_type == issue_type

    def test_issue_missing_required_field(self):
        """Missing required field raises error."""
        with pytest.raises(ValidationError):
            GrammarIssue(
                start=0,
                end=5,
                # missing original
                suggestion="the",
                issue_type="spelling",
                explanation="test",
            )

    def test_issue_serialization(self):
        """Issue serializes correctly."""
        issue = GrammarIssue(
            start=0,
            end=5,
            original="teh",
            suggestion="the",
            issue_type="spelling",
            explanation="Typo",
        )
        data = issue.model_dump()
        assert data["start"] == 0
        assert data["original"] == "teh"


# =============================================================================
# GRAMMARCHECKRESULT MODEL TESTS
# =============================================================================


class TestGrammarCheckResultModel:
    """Tests for GrammarCheckResult data model."""

    def test_create_result_with_issues(self):
        """Create result with grammar issues."""
        issue = GrammarIssue(
            start=0, end=3, original="teh", suggestion="the",
            issue_type="spelling", explanation="Typo",
        )
        result = GrammarCheckResult(
            issues=[issue],
            corrected_text="the quick brown fox",
            issue_count=1,
            score=95.0,
        )
        assert len(result.issues) == 1
        assert result.issue_count == 1
        assert result.score == 95.0

    def test_create_result_no_issues(self):
        """Create result with no issues."""
        result = GrammarCheckResult(
            issues=[],
            corrected_text="Perfect text.",
            issue_count=0,
            score=100.0,
        )
        assert len(result.issues) == 0
        assert result.score == 100.0

    def test_result_score_range(self):
        """Score can be any float value."""
        for score in [0.0, 50.0, 100.0, 99.5]:
            result = GrammarCheckResult(
                issues=[],
                corrected_text="text",
                issue_count=0,
                score=score,
            )
            assert result.score == score

    def test_result_serialization(self):
        """Result serializes correctly."""
        result = GrammarCheckResult(
            issues=[],
            corrected_text="text",
            issue_count=0,
            score=100.0,
        )
        data = result.model_dump()
        assert "issues" in data
        assert "corrected_text" in data
        assert "score" in data


# =============================================================================
# SUMMARIZERESULT MODEL TESTS
# =============================================================================


class TestSummarizeResultModel:
    """Tests for SummarizeResult data model."""

    def test_create_valid_result(self):
        """Create valid summarization result."""
        result = SummarizeResult(
            summary="Key points from the document.",
            key_points=["Point 1", "Point 2"],
            word_count_original=500,
            word_count_summary=50,
            compression_ratio=0.1,
        )
        assert result.word_count_original == 500
        assert result.compression_ratio == 0.1

    def test_result_with_empty_key_points(self):
        """Result with no key points."""
        result = SummarizeResult(
            summary="Brief summary.",
            key_points=[],
            word_count_original=100,
            word_count_summary=20,
            compression_ratio=0.2,
        )
        assert len(result.key_points) == 0

    def test_compression_ratio_calculation(self):
        """Compression ratio reflects size reduction."""
        result = SummarizeResult(
            summary="Short",
            key_points=[],
            word_count_original=1000,
            word_count_summary=100,
            compression_ratio=0.1,
        )
        assert result.compression_ratio == 0.1

    def test_result_default_key_points(self):
        """key_points defaults to empty list."""
        result = SummarizeResult(
            summary="test",
            word_count_original=100,
            word_count_summary=10,
            compression_ratio=0.1,
        )
        assert result.key_points == []


# =============================================================================
# REWRITERESULT MODEL TESTS
# =============================================================================


class TestRewriteResultModel:
    """Tests for RewriteResult data model."""

    def test_create_valid_result(self):
        """Create valid rewrite result."""
        result = RewriteResult(
            rewritten_text="The professionally written text.",
            tone="professional",
            changes_made=["Improved clarity", "Added formal tone"],
        )
        assert result.tone == "professional"
        assert len(result.changes_made) == 2

    def test_result_all_tones(self):
        """Result accepts all tone values."""
        for tone in WritingTone:
            result = RewriteResult(
                rewritten_text="text",
                tone=tone.value,
                changes_made=[],
            )
            assert result.tone == tone.value

    def test_result_empty_changes(self):
        """Result with no changes listed."""
        result = RewriteResult(
            rewritten_text="Same text",
            tone="casual",
            changes_made=[],
        )
        assert len(result.changes_made) == 0

    def test_result_default_changes_made(self):
        """changes_made defaults to empty list."""
        result = RewriteResult(
            rewritten_text="text",
            tone="professional",
        )
        assert result.changes_made == []


# =============================================================================
# EXPANDRESULT MODEL TESTS
# =============================================================================


class TestExpandResultModel:
    """Tests for ExpandResult data model."""

    def test_create_valid_result(self):
        """Create valid expand result."""
        result = ExpandResult(
            expanded_text="This is the expanded and more detailed text with examples.",
            sections_added=["Introduction", "Examples", "Conclusion"],
            word_count_original=10,
            word_count_expanded=100,
        )
        assert result.word_count_expanded == 100
        assert len(result.sections_added) == 3

    def test_result_expansion_ratio(self):
        """Track expansion ratio via word counts."""
        result = ExpandResult(
            expanded_text="Expanded content.",
            sections_added=[],
            word_count_original=50,
            word_count_expanded=250,
        )
        expansion_ratio = result.word_count_expanded / result.word_count_original
        assert expansion_ratio == 5.0

    def test_result_empty_sections(self):
        """Result with no sections added."""
        result = ExpandResult(
            expanded_text="text",
            sections_added=[],
            word_count_original=10,
            word_count_expanded=20,
        )
        assert result.sections_added == []


# =============================================================================
# TRANSLATERESULT MODEL TESTS
# =============================================================================


class TestTranslateResultModel:
    """Tests for TranslateResult data model."""

    def test_create_valid_result(self):
        """Create valid translation result."""
        result = TranslateResult(
            translated_text="Hola mundo",
            source_language="English",
            target_language="Spanish",
            confidence=0.95,
        )
        assert result.source_language == "English"
        assert result.target_language == "Spanish"
        assert result.confidence == 0.95

    def test_result_default_confidence(self):
        """Confidence defaults to 1.0."""
        result = TranslateResult(
            translated_text="Bonjour",
            source_language="English",
            target_language="French",
        )
        assert result.confidence == 1.0

    def test_result_various_languages(self):
        """Result supports various languages."""
        languages = [
            ("English", "Spanish"),
            ("English", "French"),
            ("English", "German"),
            ("English", "Chinese"),
            ("Japanese", "English"),
        ]
        for source, target in languages:
            result = TranslateResult(
                translated_text="text",
                source_language=source,
                target_language=target,
            )
            assert result.source_language == source
            assert result.target_language == target

    def test_result_low_confidence(self):
        """Result can have low confidence."""
        result = TranslateResult(
            translated_text="uncertain translation",
            source_language="unknown",
            target_language="English",
            confidence=0.3,
        )
        assert result.confidence == 0.3


# =============================================================================
# MODEL SERIALIZATION TESTS
# =============================================================================


class TestModelSerialization:
    """Tests for model serialization and deserialization."""

    def test_grammar_issue_roundtrip(self):
        """GrammarIssue survives serialization roundtrip."""
        original = GrammarIssue(
            start=0, end=5, original="teh", suggestion="the",
            issue_type="spelling", explanation="Typo", severity="warning",
        )
        data = original.model_dump()
        restored = GrammarIssue(**data)
        assert restored == original

    def test_grammar_result_roundtrip(self):
        """GrammarCheckResult survives serialization roundtrip."""
        original = GrammarCheckResult(
            issues=[],
            corrected_text="text",
            issue_count=0,
            score=100.0,
        )
        data = original.model_dump()
        restored = GrammarCheckResult(**data)
        assert restored == original

    def test_summarize_result_roundtrip(self):
        """SummarizeResult survives serialization roundtrip."""
        original = SummarizeResult(
            summary="summary",
            key_points=["point"],
            word_count_original=100,
            word_count_summary=10,
            compression_ratio=0.1,
        )
        data = original.model_dump()
        restored = SummarizeResult(**data)
        assert restored == original

    def test_rewrite_result_roundtrip(self):
        """RewriteResult survives serialization roundtrip."""
        original = RewriteResult(
            rewritten_text="text",
            tone="professional",
            changes_made=["change"],
        )
        data = original.model_dump()
        restored = RewriteResult(**data)
        assert restored == original

    def test_expand_result_roundtrip(self):
        """ExpandResult survives serialization roundtrip."""
        original = ExpandResult(
            expanded_text="expanded",
            sections_added=["intro"],
            word_count_original=10,
            word_count_expanded=50,
        )
        data = original.model_dump()
        restored = ExpandResult(**data)
        assert restored == original

    def test_translate_result_roundtrip(self):
        """TranslateResult survives serialization roundtrip."""
        original = TranslateResult(
            translated_text="hola",
            source_language="en",
            target_language="es",
            confidence=0.9,
        )
        data = original.model_dump()
        restored = TranslateResult(**data)
        assert restored == original


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestModelEdgeCases:
    """Edge case tests for models."""

    def test_grammar_issue_zero_positions(self):
        """Grammar issue at position 0."""
        issue = GrammarIssue(
            start=0, end=0, original="", suggestion="",
            issue_type="style", explanation="Empty",
        )
        assert issue.start == 0
        assert issue.end == 0

    def test_grammar_issue_large_positions(self):
        """Grammar issue at large positions."""
        issue = GrammarIssue(
            start=10000, end=10010, original="text",
            suggestion="better text", issue_type="style",
            explanation="Improvement",
        )
        assert issue.start == 10000

    def test_summarize_zero_words(self):
        """Summarize result with zero word counts."""
        result = SummarizeResult(
            summary="",
            key_points=[],
            word_count_original=0,
            word_count_summary=0,
            compression_ratio=1.0,
        )
        assert result.word_count_original == 0

    def test_expand_same_word_counts(self):
        """Expand result with same word counts (no expansion)."""
        result = ExpandResult(
            expanded_text="text",
            sections_added=[],
            word_count_original=100,
            word_count_expanded=100,
        )
        assert result.word_count_original == result.word_count_expanded

    def test_translate_unknown_language(self):
        """Translation with unknown source language."""
        result = TranslateResult(
            translated_text="text",
            source_language="unknown",
            target_language="English",
            confidence=0.5,
        )
        assert result.source_language == "unknown"

    def test_grammar_issue_unicode_content(self):
        """Grammar issue with unicode content."""
        issue = GrammarIssue(
            start=0, end=5,
            original="héllo",
            suggestion="hello",
            issue_type="spelling",
            explanation="Remove accent",
        )
        assert "é" in issue.original

    def test_translate_unicode_text(self):
        """Translation with unicode text."""
        result = TranslateResult(
            translated_text="你好世界",
            source_language="English",
            target_language="Chinese",
            confidence=0.9,
        )
        assert "你好" in result.translated_text

    def test_many_key_points(self):
        """Summarize with many key points."""
        key_points = [f"Point {i}" for i in range(50)]
        result = SummarizeResult(
            summary="Long document summary",
            key_points=key_points,
            word_count_original=5000,
            word_count_summary=100,
            compression_ratio=0.02,
        )
        assert len(result.key_points) == 50

    def test_many_changes_made(self):
        """Rewrite with many changes."""
        changes = [f"Change {i}" for i in range(20)]
        result = RewriteResult(
            rewritten_text="Rewritten content",
            tone="professional",
            changes_made=changes,
        )
        assert len(result.changes_made) == 20
