"""
Proofreading Agent - Production-grade implementation.

Comprehensive grammar, style, and clarity checking with support for
style guides (AP, Chicago, APA, MLA), configurable focus areas,
and optional voice preservation.  Returns structured issues with
categories, original text, corrections, and explanations.

Design Principles:
- Structured issue reporting with categorisation
- Readability scoring (local calculation, not LLM-guessed)
- Voice preservation option
- Style guide enforcement
- Progress callbacks + cost tracking
"""
from __future__ import annotations

import asyncio
import logging
import math
import re
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from backend.app.services.agents.base_agent import (
    AgentError,
    BaseAgentV2,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMContentFilterError,
    ProgressCallback,
    ProgressUpdate,
    ValidationError,
)

logger = logging.getLogger("neura.agents.proofreading")

VALID_STYLE_GUIDES = {"ap", "chicago", "apa", "mla", "none"}
VALID_FOCUS_AREAS = {
    "grammar", "spelling", "punctuation", "clarity", "conciseness",
    "tone", "consistency", "formatting", "word_choice", "structure",
}
MAX_TEXT_LENGTH = 50000
MAX_FOCUS_AREAS = 5


# =============================================================================
# INPUT VALIDATION
# =============================================================================

class ProofreadingInput(BaseModel):
    """Validated input for proofreading agent."""
    text: str = Field(..., min_length=10, max_length=MAX_TEXT_LENGTH)
    style_guide: Optional[str] = Field(default=None, max_length=20)
    focus_areas: Optional[List[str]] = Field(default=None)
    preserve_voice: bool = Field(default=True)

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty or whitespace")
        if len(v.split()) < 3:
            raise ValueError("Text must contain at least 3 words for proofreading")
        return v

    @field_validator("style_guide")
    @classmethod
    def validate_style_guide(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if v not in VALID_STYLE_GUIDES:
            raise ValueError(
                f"Style guide must be one of: {', '.join(sorted(VALID_STYLE_GUIDES))}. Got: {v}"
            )
        if v == "none":
            return None
        return v

    @field_validator("focus_areas")
    @classmethod
    def validate_focus_areas(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if not v:
            return v
        cleaned = []
        seen: set[str] = set()
        for area in v:
            area = area.strip().lower()
            if area and area not in seen:
                if area not in VALID_FOCUS_AREAS:
                    raise ValueError(
                        f"Unknown focus area: '{area}'. "
                        f"Valid areas: {', '.join(sorted(VALID_FOCUS_AREAS))}"
                    )
                seen.add(area)
                cleaned.append(area)
        return cleaned[:MAX_FOCUS_AREAS]


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class ProofreadingIssue(BaseModel):
    """A single proofreading issue found in the text."""
    issue_type: str = Field(..., max_length=50)
    original: str = Field(default="", max_length=500)
    correction: str = Field(default="", max_length=500)
    explanation: str = Field(default="", max_length=500)
    severity: str = Field(default="suggestion", max_length=20)


class ProofreadingReport(BaseModel):
    """Complete proofreading output."""
    original_text: str
    corrected_text: str
    issues_found: List[ProofreadingIssue] = Field(default_factory=list)
    style_suggestions: List[str] = Field(default_factory=list)
    readability_score: float = Field(default=0.0, ge=0.0, le=100.0)
    reading_level: str = Field(default="")
    word_count: int = Field(default=0, ge=0)
    issue_count: int = Field(default=0, ge=0)
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def model_post_init(self, __context):
        if not self.word_count and self.original_text:
            self.word_count = len(self.original_text.split())
        if not self.issue_count:
            self.issue_count = len(self.issues_found)


# =============================================================================
# PROOFREADING AGENT
# =============================================================================
from backend.app.services.agents.agent_registry import register_agent


@register_agent(
    "proofreading",
    version="2.0",
    capabilities=["grammar_check", "style_enforcement", "readability_scoring"],
    timeout_seconds=120,
)
class ProofreadingAgentV2(BaseAgentV2):
    """
    Production-grade proofreading agent.

    Features:
    - Style guide support (AP, Chicago, APA, MLA)
    - Configurable focus areas (grammar, spelling, clarity, etc.)
    - Voice preservation option
    - Local readability scoring (Flesch-Kincaid)
    - Structured issue reporting with severity levels
    """

    async def execute(
        self,
        text: str,
        style_guide: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        preserve_voice: bool = True,
        *,
        progress_callback: Optional[ProgressCallback] = None,
        timeout_seconds: int = 120,
    ) -> tuple[ProofreadingReport, Dict[str, Any]]:
        """Execute proofreading.

        Returns:
            Tuple of (ProofreadingReport, metadata dict).
        """
        try:
            validated = ProofreadingInput(
                text=text,
                style_guide=style_guide,
                focus_areas=focus_areas,
                preserve_voice=preserve_voice,
            )
        except Exception as e:
            raise ValidationError(str(e), field="input")

        def report_progress(percent: int, message: str, step: str, step_num: int):
            if progress_callback:
                progress_callback(ProgressUpdate(
                    percent=percent,
                    message=message,
                    current_step=step,
                    total_steps=2,
                    current_step_num=step_num,
                ))

        try:
            # Step 1: Compute local readability metrics
            report_progress(10, "Computing readability metrics...", "readability", 1)
            readability_score = self._compute_readability(validated.text)
            reading_level = self._score_to_level(readability_score)

            report_progress(20, "Proofreading text...", "proofreading", 2)

            # Step 2: LLM proofreading
            style_context = (
                f"\nFollow {validated.style_guide.upper()} style guide."
                if validated.style_guide
                else ""
            )
            focus_context = (
                f"\nFocus especially on: {', '.join(validated.focus_areas)}"
                if validated.focus_areas
                else ""
            )
            voice_context = (
                "\nPreserve the author's unique voice while making corrections."
                if validated.preserve_voice
                else ""
            )

            system_prompt = f"""You are an expert editor and proofreader. Review the text for:
1. Grammar and spelling errors
2. Punctuation issues
3. Style and clarity improvements
4. Consistency issues
5. Readability enhancements
{style_context}{focus_context}{voice_context}

Provide your response as JSON:
{{
    "corrected_text": "<the improved text>",
    "issues_found": [
        {{
            "issue_type": "<grammar|spelling|punctuation|clarity|style|consistency>",
            "original": "<original text snippet>",
            "correction": "<corrected text>",
            "explanation": "<why this was changed>",
            "severity": "<error|warning|suggestion>"
        }}
    ],
    "style_suggestions": ["<suggestion 1>", ...]
}}"""

            result = await self._call_llm(
                system_prompt=system_prompt,
                user_prompt=validated.text,
                max_tokens=4000,
                timeout_seconds=timeout_seconds,
                temperature=0.3,
            )

            parsed = result["parsed"]

            report_progress(85, "Compiling report...", "proofreading", 2)

            issues = []
            for issue in parsed.get("issues_found", []):
                try:
                    issues.append(ProofreadingIssue(
                        issue_type=issue.get("issue_type", "general"),
                        original=issue.get("original", ""),
                        correction=issue.get("correction", ""),
                        explanation=issue.get("explanation", ""),
                        severity=issue.get("severity", "suggestion"),
                    ))
                except Exception:
                    pass  # Skip malformed issues

            report = ProofreadingReport(
                original_text=validated.text,
                corrected_text=parsed.get("corrected_text", validated.text),
                issues_found=issues,
                style_suggestions=parsed.get("style_suggestions", []),
                readability_score=round(readability_score, 1),
                reading_level=reading_level,
            )

            cost_cents = self._estimate_cost_cents(
                result["input_tokens"], result["output_tokens"]
            )
            metadata = {
                "tokens_input": result["input_tokens"],
                "tokens_output": result["output_tokens"],
                "estimated_cost_cents": cost_cents,
            }

            report_progress(100, "Proofreading complete", "done", 2)
            return report, metadata

        except (ValidationError, AgentError):
            raise
        except asyncio.TimeoutError:
            raise LLMTimeoutError(timeout_seconds)
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "rate_limit" in error_str:
                raise LLMRateLimitError()
            elif "timeout" in error_str:
                raise LLMTimeoutError(timeout_seconds)
            elif "content filter" in error_str:
                raise LLMContentFilterError(str(e))
            raise AgentError(str(e), code="PROOFREADING_FAILED", retryable=True)

    # ----- Local readability scoring (Flesch-Kincaid) -----

    @staticmethod
    def _count_syllables(word: str) -> int:
        """Estimate syllable count for an English word."""
        word = word.lower().strip()
        if not word:
            return 0
        # Simple heuristic: count vowel groups
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        # Adjust for silent e
        if word.endswith("e") and count > 1:
            count -= 1
        return max(1, count)

    @staticmethod
    def _compute_readability(text: str) -> float:
        """Compute Flesch Reading Ease score (0-100, higher = easier)."""
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 50.0

        words = re.findall(r"\b[a-zA-Z]+\b", text)
        if not words:
            return 50.0

        total_sentences = len(sentences)
        total_words = len(words)
        total_syllables = sum(
            ProofreadingAgentV2._count_syllables(w) for w in words
        )

        # Flesch Reading Ease formula
        score = (
            206.835
            - 1.015 * (total_words / total_sentences)
            - 84.6 * (total_syllables / total_words)
        )
        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_to_level(score: float) -> str:
        """Convert Flesch score to reading level description."""
        if score >= 90:
            return "5th grade (very easy)"
        elif score >= 80:
            return "6th grade (easy)"
        elif score >= 70:
            return "7th grade (fairly easy)"
        elif score >= 60:
            return "8th-9th grade (standard)"
        elif score >= 50:
            return "10th-12th grade (fairly difficult)"
        elif score >= 30:
            return "College (difficult)"
        else:
            return "Professional (very difficult)"
