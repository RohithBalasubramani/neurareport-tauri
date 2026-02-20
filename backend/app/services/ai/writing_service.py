"""
AI Writing Service
Provides AI-powered writing assistance using the unified LLM client for grammar
checking, summarization, rewriting, expansion, and translation.

Uses the unified LLMClient which provides:
- Circuit breaker for fault tolerance
- Response caching (memory + disk)
- Token usage tracking
- Automatic retry with exponential backoff
- Multi-provider support (OpenAI, Claude, Gemini, DeepSeek, Ollama, Azure)
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Input limits
# ---------------------------------------------------------------------------
MAX_TEXT_CHARS = 100_000  # ~25K tokens — hard cap to prevent token overflow
MAX_TEXT_CHARS_EXPAND = 50_000  # Expansion needs output room
MIN_TEXT_CHARS = 1  # Minimum non-whitespace chars


class WritingTone(str, Enum):
    """Available writing tones for rewriting."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    CONCISE = "concise"


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------

class GrammarIssue(BaseModel):
    """Represents a grammar or style issue found in text."""
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    original: str = Field(..., description="Original text")
    suggestion: str = Field(..., description="Suggested correction")
    issue_type: str = Field(..., description="Type of issue (grammar, spelling, style, etc.)")
    explanation: str = Field(..., description="Explanation of the issue")
    severity: str = Field(default="warning", description="Severity: error, warning, suggestion")


class GrammarCheckResult(BaseModel):
    """Result of grammar check operation."""
    issues: List[GrammarIssue] = Field(default_factory=list)
    corrected_text: str = Field(..., description="Text with all corrections applied")
    issue_count: int = Field(..., description="Total number of issues found")
    score: float = Field(..., description="Quality score 0-100", ge=0, le=100)


class SummarizeResult(BaseModel):
    """Result of summarization operation."""
    summary: str = Field(..., description="Summarized text")
    key_points: List[str] = Field(default_factory=list, description="Key points extracted")
    word_count_original: int = Field(..., description="Original word count")
    word_count_summary: int = Field(..., description="Summary word count")
    compression_ratio: float = Field(..., description="Compression ratio")


class RewriteResult(BaseModel):
    """Result of rewrite operation."""
    rewritten_text: str = Field(..., description="Rewritten text")
    tone: str = Field(..., description="Applied tone")
    changes_made: List[str] = Field(default_factory=list, description="Summary of changes")


class ExpandResult(BaseModel):
    """Result of expansion operation."""
    expanded_text: str = Field(..., description="Expanded text")
    sections_added: List[str] = Field(default_factory=list, description="Sections or points added")
    word_count_original: int = Field(..., description="Original word count")
    word_count_expanded: int = Field(..., description="Expanded word count")


class TranslateResult(BaseModel):
    """Result of translation operation."""
    translated_text: str = Field(..., description="Translated text")
    source_language: str = Field(..., description="Detected or specified source language")
    target_language: str = Field(..., description="Target language")
    confidence: float = Field(default=1.0, description="Translation confidence 0-1", ge=0, le=1)


# ---------------------------------------------------------------------------
# Service errors
# ---------------------------------------------------------------------------

class WritingServiceError(Exception):
    """Base error for writing service."""


class InputValidationError(WritingServiceError):
    """Raised when input text fails validation."""


class LLMResponseError(WritingServiceError):
    """Raised when LLM returns an unparseable or invalid response."""


class LLMUnavailableError(WritingServiceError):
    """Raised when the LLM service is unavailable (circuit breaker open)."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_json(raw: str) -> dict:
    """Extract JSON from an LLM response that may contain markdown fences.

    Returns:
        Parsed dict from the JSON content.

    Raises:
        json.JSONDecodeError: If the response is not valid JSON.
        ValueError: If the parsed result is not a JSON object (dict).
    """
    text = raw.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        # Remove opening fence (optionally with language tag)
        text = re.sub(r"^```(?:json)?\s*\n?", "", text, count=1)
        text = re.sub(r"\n?```\s*$", "", text, count=1)
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object, got {type(parsed).__name__}")
    return parsed


def _validate_grammar_positions(issues: list[dict], text_length: int) -> list[dict]:
    """Validate and fix grammar issue positions to be within text bounds."""
    valid = []
    for issue in issues:
        start = issue.get("start", 0)
        end = issue.get("end", 0)

        # Clamp to valid range
        start = max(0, min(start, text_length))
        end = max(start, min(end, text_length))

        issue["start"] = start
        issue["end"] = end
        valid.append(issue)
    return valid


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class WritingService:
    """
    AI-powered writing assistance service.

    Uses the unified LLMClient for all LLM interactions, which provides
    circuit breaker, caching, retry, multi-provider support, and token tracking.
    """

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        """Get the unified LLM client (lazy-loaded, singleton)."""
        if self._llm_client is None:
            from backend.app.services.llm.client import get_llm_client
            self._llm_client = get_llm_client()
        return self._llm_client

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
        description: str = "writing_service",
    ) -> str:
        """
        Make an LLM call through the unified client.

        Runs the synchronous LLMClient.complete() in a thread pool
        to avoid blocking the async event loop.

        Raises:
            LLMUnavailableError: When circuit breaker is open / service down.
            LLMResponseError: When the LLM returns empty content.
        """
        client = self._get_llm_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await asyncio.to_thread(
                client.complete,
                messages=messages,
                description=description,
                max_tokens=max_tokens,
            )
        except RuntimeError as exc:
            # Circuit breaker open or provider unavailable
            if "temporarily unavailable" in str(exc).lower():
                raise LLMUnavailableError(str(exc)) from exc
            raise LLMResponseError(str(exc)) from exc
        except Exception as exc:
            raise LLMResponseError(f"LLM call failed: {exc}") from exc

        # Extract content from OpenAI-compatible response dict
        content = (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        if not content:
            raise LLMResponseError("LLM returned empty response")

        return content

    # ----- Grammar Check -----

    async def check_grammar(
        self,
        text: str,
        language: str = "en",
        strict: bool = False,
    ) -> GrammarCheckResult:
        """
        Check text for grammar, spelling, and style issues.

        Args:
            text: Text to check (1 to 100,000 chars)
            language: Language code (default: en)
            strict: Enable strict mode for additional style checks

        Returns:
            GrammarCheckResult with issues and corrected text

        Raises:
            InputValidationError: If text is empty or too long.
            LLMResponseError: If LLM returns unparseable result.
            LLMUnavailableError: If LLM service is down.
        """
        stripped = text.strip()
        if not stripped:
            return GrammarCheckResult(
                issues=[],
                corrected_text=text,
                issue_count=0,
                score=100.0,
            )

        if len(text) > MAX_TEXT_CHARS:
            raise InputValidationError(
                f"Text exceeds maximum length of {MAX_TEXT_CHARS:,} characters "
                f"(got {len(text):,}). Split into smaller chunks."
            )

        system_prompt = f"""You are an expert grammar and style checker for {language} text.
Analyze the text for:
1. Grammar errors
2. Spelling mistakes
3. Punctuation issues
4. Style improvements{' (be strict — flag all style issues including passive voice, wordiness, and informal language)' if strict else ''}

Respond ONLY with valid JSON (no markdown fences):
{{
    "issues": [
        {{
            "start": <character position>,
            "end": <character position>,
            "original": "<original text>",
            "suggestion": "<corrected text>",
            "issue_type": "<grammar|spelling|punctuation|style>",
            "explanation": "<brief explanation>",
            "severity": "<error|warning|suggestion>"
        }}
    ],
    "corrected_text": "<full text with all corrections applied>",
    "score": <0-100 quality score>
}}"""

        user_prompt = f"Check this text:\n\n{text}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            description="grammar_check",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(
                f"Grammar check returned invalid JSON: {exc}"
            ) from exc

        raw_issues = result.get("issues", [])
        if not isinstance(raw_issues, list):
            raw_issues = []
        validated_issues = _validate_grammar_positions(raw_issues, len(text))

        issues = []
        for issue_data in validated_issues:
            try:
                issues.append(GrammarIssue(**issue_data))
            except Exception:
                # Skip malformed individual issues but don't fail the whole check
                logger.warning("Skipping malformed grammar issue: %s", issue_data)

        score = result.get("score", 100.0)
        score = max(0.0, min(100.0, float(score)))

        return GrammarCheckResult(
            issues=issues,
            corrected_text=result.get("corrected_text", text),
            issue_count=len(issues),
            score=score,
        )

    # ----- Summarize -----

    async def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        style: str = "bullet_points",
    ) -> SummarizeResult:
        """
        Summarize text with optional length limit.

        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            style: Output style (bullet_points, paragraph, executive)

        Returns:
            SummarizeResult with summary and key points
        """
        stripped = text.strip()
        if not stripped:
            return SummarizeResult(
                summary="",
                key_points=[],
                word_count_original=0,
                word_count_summary=0,
                compression_ratio=1.0,
            )

        if len(text) > MAX_TEXT_CHARS:
            raise InputValidationError(
                f"Text exceeds maximum length of {MAX_TEXT_CHARS:,} characters."
            )

        word_count_original = len(text.split())
        length_instruction = f"Keep the summary under {max_length} words." if max_length else ""

        style_instructions = {
            "bullet_points": "Use bullet points for key takeaways.",
            "paragraph": "Write as a cohesive paragraph.",
            "executive": "Write an executive summary with overview and key conclusions.",
        }

        system_prompt = f"""You are an expert summarizer. Create a clear, concise summary.
{style_instructions.get(style, style_instructions['paragraph'])}
{length_instruction}

Respond ONLY with valid JSON (no markdown fences):
{{
    "summary": "<the summary>",
    "key_points": ["<point 1>", "<point 2>", ...]
}}"""

        user_prompt = f"Summarize this text:\n\n{text}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            description="summarize",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(
                f"Summarization returned invalid JSON: {exc}"
            ) from exc

        summary = result.get("summary", "")
        word_count_summary = len(summary.split()) if summary else 0

        return SummarizeResult(
            summary=summary,
            key_points=result.get("key_points", []),
            word_count_original=word_count_original,
            word_count_summary=word_count_summary,
            compression_ratio=word_count_summary / word_count_original if word_count_original > 0 else 1.0,
        )

    # ----- Rewrite -----

    async def rewrite(
        self,
        text: str,
        tone: WritingTone = WritingTone.PROFESSIONAL,
        preserve_meaning: bool = True,
    ) -> RewriteResult:
        """
        Rewrite text with specified tone.

        Args:
            text: Text to rewrite
            tone: Target tone for rewriting
            preserve_meaning: Whether to preserve original meaning

        Returns:
            RewriteResult with rewritten text
        """
        stripped = text.strip()
        if not stripped:
            return RewriteResult(
                rewritten_text=text,
                tone=tone.value,
                changes_made=[],
            )

        if len(text) > MAX_TEXT_CHARS:
            raise InputValidationError(
                f"Text exceeds maximum length of {MAX_TEXT_CHARS:,} characters."
            )

        tone_descriptions = {
            WritingTone.PROFESSIONAL: "professional and business-appropriate",
            WritingTone.CASUAL: "casual and conversational",
            WritingTone.FORMAL: "formal and official",
            WritingTone.FRIENDLY: "friendly and approachable",
            WritingTone.ACADEMIC: "academic and scholarly",
            WritingTone.TECHNICAL: "technical and precise",
            WritingTone.PERSUASIVE: "persuasive and compelling",
            WritingTone.CONCISE: "concise and direct",
        }

        system_prompt = f"""You are an expert writer. Rewrite the text to be {tone_descriptions.get(tone, 'professional')}.
{'Preserve the original meaning.' if preserve_meaning else 'You may adjust the meaning for clarity.'}

Respond ONLY with valid JSON (no markdown fences):
{{
    "rewritten_text": "<rewritten text>",
    "changes_made": ["<change 1>", "<change 2>", ...]
}}"""

        user_prompt = f"Rewrite this text:\n\n{text}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            description="rewrite",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(
                f"Rewrite returned invalid JSON: {exc}"
            ) from exc

        return RewriteResult(
            rewritten_text=result.get("rewritten_text", text),
            tone=tone.value,
            changes_made=result.get("changes_made", []),
        )

    # ----- Expand -----

    async def expand(
        self,
        text: str,
        target_length: Optional[int] = None,
        add_examples: bool = False,
        add_details: bool = True,
    ) -> ExpandResult:
        """
        Expand text with additional details and examples.

        Args:
            text: Text to expand
            target_length: Target word count
            add_examples: Whether to include examples
            add_details: Whether to add explanatory details

        Returns:
            ExpandResult with expanded text
        """
        stripped = text.strip()
        if not stripped:
            return ExpandResult(
                expanded_text=text,
                sections_added=[],
                word_count_original=0,
                word_count_expanded=0,
            )

        if len(text) > MAX_TEXT_CHARS_EXPAND:
            raise InputValidationError(
                f"Text exceeds maximum length of {MAX_TEXT_CHARS_EXPAND:,} characters for expansion."
            )

        word_count_original = len(text.split())

        instructions = []
        if add_examples:
            instructions.append("Include relevant examples")
        if add_details:
            instructions.append("Add explanatory details")
        if target_length:
            instructions.append(f"Aim for approximately {target_length} words")

        system_prompt = f"""You are an expert content writer. Expand the text with more depth.
Instructions: {', '.join(instructions) if instructions else 'Expand naturally'}

Respond ONLY with valid JSON (no markdown fences):
{{
    "expanded_text": "<expanded text>",
    "sections_added": ["<section/topic added 1>", "<section/topic added 2>", ...]
}}"""

        user_prompt = f"Expand this text:\n\n{text}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            max_tokens=4000,
            description="expand",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(
                f"Expansion returned invalid JSON: {exc}"
            ) from exc

        expanded = result.get("expanded_text", text)

        return ExpandResult(
            expanded_text=expanded,
            sections_added=result.get("sections_added", []),
            word_count_original=word_count_original,
            word_count_expanded=len(expanded.split()),
        )

    # ----- Translate -----

    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        preserve_formatting: bool = True,
    ) -> TranslateResult:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language (e.g., "Spanish", "French", "es", "fr")
            source_language: Source language (auto-detect if None)
            preserve_formatting: Whether to preserve original formatting

        Returns:
            TranslateResult with translated text
        """
        stripped = text.strip()
        if not stripped:
            return TranslateResult(
                translated_text=text,
                source_language=source_language or "unknown",
                target_language=target_language,
                confidence=1.0,
            )

        if len(text) > MAX_TEXT_CHARS:
            raise InputValidationError(
                f"Text exceeds maximum length of {MAX_TEXT_CHARS:,} characters."
            )

        source_instruction = f"from {source_language}" if source_language else "(detect source language)"

        system_prompt = f"""You are an expert translator. Translate the text {source_instruction} to {target_language}.
{'Preserve the original formatting (line breaks, bullet points, etc.).' if preserve_formatting else ''}

Respond ONLY with valid JSON (no markdown fences):
{{
    "translated_text": "<translated text>",
    "source_language": "<detected or specified source language>",
    "confidence": <0.0-1.0 confidence score>
}}"""

        user_prompt = f"Translate:\n\n{text}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            max_tokens=4000,
            description="translate",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(
                f"Translation returned invalid JSON: {exc}"
            ) from exc

        confidence = result.get("confidence", 0.9)
        confidence = max(0.0, min(1.0, float(confidence)))

        return TranslateResult(
            translated_text=result.get("translated_text", text),
            source_language=result.get("source_language", source_language or "auto"),
            target_language=target_language,
            confidence=confidence,
        )

    # ----- Content Generation -----

    async def generate_content(
        self,
        prompt: str,
        context: Optional[str] = None,
        tone: WritingTone = WritingTone.PROFESSIONAL,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Generate new content based on a prompt.

        Args:
            prompt: Content generation prompt
            context: Additional context for generation
            tone: Target tone
            max_length: Maximum length in words

        Returns:
            Generated content string
        """
        if not prompt.strip():
            raise InputValidationError("Prompt cannot be empty.")

        if len(prompt) > MAX_TEXT_CHARS:
            raise InputValidationError(
                f"Prompt exceeds maximum length of {MAX_TEXT_CHARS:,} characters."
            )

        tone_desc = {
            WritingTone.PROFESSIONAL: "professional",
            WritingTone.CASUAL: "casual",
            WritingTone.FORMAL: "formal",
            WritingTone.FRIENDLY: "friendly",
            WritingTone.ACADEMIC: "academic",
            WritingTone.TECHNICAL: "technical",
            WritingTone.PERSUASIVE: "persuasive",
            WritingTone.CONCISE: "concise",
        }

        system_prompt = f"""You are an expert content writer.
Generate content that is {tone_desc.get(tone, 'professional')} in tone.
{f'Keep the response under {max_length} words.' if max_length else ''}
{f'Context: {context}' if context else ''}"""

        return await self._call_llm(
            system_prompt,
            prompt,
            max_tokens=4000,
            description="generate_content",
        )


# Singleton instance
writing_service = WritingService()
