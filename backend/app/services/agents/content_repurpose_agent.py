"""
Content Repurposing Agent - Production-grade implementation.

Transforms content from one format (article, report, transcript, etc.)
into multiple target formats (tweet thread, LinkedIn post, blog summary,
slides, newsletter, video script, infographic, podcast notes, press
release, executive summary).

Design Principles:
- Each target format is processed as a separate LLM call (isolation)
- Per-format progress tracking
- Partial results returned if some formats fail (no all-or-nothing)
- Token/cost tracking aggregated across all formats
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from backend.app.services.agents.base_agent import (
    AgentError,
    BaseAgentV2,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMContentFilterError,
    LLMResponseError,
    ProgressCallback,
    ProgressUpdate,
    ValidationError,
)

logger = logging.getLogger("neura.agents.content_repurpose")


# Supported target formats with generation guidelines
FORMAT_GUIDELINES = {
    "tweet_thread": "Create a Twitter thread (max 280 chars per tweet, 5-10 tweets)",
    "linkedin_post": "Create a LinkedIn post (professional tone, 1300 chars max)",
    "blog_summary": "Create a blog-style summary (300-500 words)",
    "slides": "Create slide content (title + 3-5 bullet points per slide, max 10 slides)",
    "email_newsletter": "Create newsletter content (catchy subject, scannable body)",
    "video_script": "Create a video script (conversational, 2-3 minutes)",
    "infographic": "Create infographic copy (headline, key stats, takeaways)",
    "podcast_notes": "Create podcast show notes (summary, timestamps, links)",
    "press_release": "Create press release format (headline, lead, quotes)",
    "executive_summary": "Create executive summary (1 page, key decisions)",
}

VALID_FORMATS = set(FORMAT_GUIDELINES.keys())
MAX_TARGET_FORMATS = 10


# =============================================================================
# INPUT VALIDATION
# =============================================================================

class ContentRepurposeInput(BaseModel):
    """Validated input for content repurposing agent."""
    content: str = Field(..., min_length=20, max_length=50000)
    source_format: str = Field(..., min_length=1, max_length=50)
    target_formats: List[str] = Field(..., min_length=1, max_length=MAX_TARGET_FORMATS)
    preserve_key_points: bool = Field(default=True)
    adapt_length: bool = Field(default=True)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Content cannot be empty or whitespace")
        if len(v.split()) < 5:
            raise ValueError("Content must contain at least 5 words to repurpose")
        return v

    @field_validator("source_format")
    @classmethod
    def validate_source_format(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("target_formats")
    @classmethod
    def validate_target_formats(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one target format is required")
        cleaned = []
        seen: set[str] = set()
        for fmt in v:
            fmt = fmt.strip().lower()
            if fmt and fmt not in seen:
                if fmt not in VALID_FORMATS:
                    raise ValueError(
                        f"Unknown target format: '{fmt}'. "
                        f"Valid formats: {', '.join(sorted(VALID_FORMATS))}"
                    )
                seen.add(fmt)
                cleaned.append(fmt)
        if not cleaned:
            raise ValueError("At least one valid target format is required")
        return cleaned[:MAX_TARGET_FORMATS]


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class RepurposedOutput(BaseModel):
    """A single repurposed content version."""
    format: str
    content: str
    word_count: int = Field(default=0, ge=0)
    char_count: int = Field(default=0, ge=0)
    error: Optional[str] = None

    def model_post_init(self, __context):
        if not self.word_count and self.content:
            self.word_count = len(self.content.split())
        if not self.char_count and self.content:
            self.char_count = len(self.content)


class ContentRepurposeReport(BaseModel):
    """Complete content repurposing output."""
    original_format: str
    outputs: List[RepurposedOutput] = Field(default_factory=list)
    adaptations_made: List[str] = Field(default_factory=list)
    formats_requested: int = Field(default=0, ge=0)
    formats_succeeded: int = Field(default=0, ge=0)
    formats_failed: int = Field(default=0, ge=0)
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# =============================================================================
# CONTENT REPURPOSE AGENT
# =============================================================================
from backend.app.services.agents.agent_registry import register_agent


@register_agent(
    "content_repurpose",
    version="2.0",
    capabilities=["content_adaptation", "multi_format", "summarization"],
    timeout_seconds=180,
)
class ContentRepurposeAgentV2(BaseAgentV2):
    """
    Production-grade content repurposing agent.

    Features:
    - 10 output formats supported
    - Per-format LLM calls (isolation, no cascading failure)
    - Partial success: if some formats fail, others are still returned
    - Per-format progress tracking
    - Aggregated cost tracking
    """

    async def execute(
        self,
        content: str,
        source_format: str,
        target_formats: List[str],
        preserve_key_points: bool = True,
        adapt_length: bool = True,
        *,
        progress_callback: Optional[ProgressCallback] = None,
        timeout_seconds: int = 120,
    ) -> tuple[ContentRepurposeReport, Dict[str, Any]]:
        """Execute content repurposing.

        Returns:
            Tuple of (ContentRepurposeReport, metadata dict).
        """
        try:
            validated = ContentRepurposeInput(
                content=content,
                source_format=source_format,
                target_formats=target_formats,
                preserve_key_points=preserve_key_points,
                adapt_length=adapt_length,
            )
        except Exception as e:
            raise ValidationError(str(e), field="input")

        total_formats = len(validated.target_formats)
        total_input_tokens = 0
        total_output_tokens = 0
        outputs: List[RepurposedOutput] = []
        adaptations: List[str] = []
        succeeded = 0
        failed = 0

        def report_progress(percent: int, message: str, step: str, step_num: int):
            if progress_callback:
                progress_callback(ProgressUpdate(
                    percent=percent,
                    message=message,
                    current_step=step,
                    total_steps=total_formats,
                    current_step_num=step_num,
                ))

        try:
            for i, target_format in enumerate(validated.target_formats):
                step_num = i + 1
                progress_pct = int(10 + (80 * i / total_formats))
                report_progress(
                    progress_pct,
                    f"Converting to {target_format} ({step_num}/{total_formats})...",
                    target_format,
                    step_num,
                )

                guidelines = FORMAT_GUIDELINES.get(
                    target_format, f"Create {target_format} format content"
                )

                system_prompt = f"""You are a content repurposing expert. Transform the following {validated.source_format} into {target_format} format.

Guidelines: {guidelines}
{'Preserve all key points and main ideas.' if validated.preserve_key_points else ''}
{'Adapt the length appropriately for the format.' if validated.adapt_length else ''}

Return ONLY the transformed content, no explanations."""

                try:
                    result = await self._call_llm(
                        system_prompt=system_prompt,
                        user_prompt=validated.content,
                        max_tokens=2000,
                        timeout_seconds=timeout_seconds,
                        temperature=0.7,
                    )

                    total_input_tokens += result["input_tokens"]
                    total_output_tokens += result["output_tokens"]

                    # For repurpose, we want the raw text output, not parsed JSON
                    transformed = result["raw"]
                    outputs.append(RepurposedOutput(
                        format=target_format,
                        content=transformed,
                    ))
                    adaptations.append(f"Converted to {target_format}")
                    succeeded += 1

                except AgentError as e:
                    # Log but don't abort — partial results are acceptable
                    logger.warning(f"Failed to repurpose to {target_format}: {e.message}")
                    outputs.append(RepurposedOutput(
                        format=target_format,
                        content="",
                        error=e.message,
                    ))
                    failed += 1

            report_progress(95, "Finalising results...", "finalise", total_formats)

            # If ALL formats failed, raise an error
            if failed == total_formats:
                raise AgentError(
                    f"All {total_formats} format conversions failed",
                    code="ALL_FORMATS_FAILED",
                    retryable=True,
                )

            report = ContentRepurposeReport(
                original_format=validated.source_format,
                outputs=outputs,
                adaptations_made=adaptations,
                formats_requested=total_formats,
                formats_succeeded=succeeded,
                formats_failed=failed,
            )

            cost_cents = self._estimate_cost_cents(total_input_tokens, total_output_tokens)
            metadata = {
                "tokens_input": total_input_tokens,
                "tokens_output": total_output_tokens,
                "estimated_cost_cents": cost_cents,
            }

            report_progress(100, "Repurposing complete", "done", total_formats)
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
            raise AgentError(str(e), code="CONTENT_REPURPOSE_FAILED", retryable=True)
