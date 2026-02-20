"""
Email Draft Agent - Production-grade implementation.

Composes email responses based on context, purpose, tone, recipient info,
and previous email thread context.  Produces structured drafts with subject
lines, follow-up actions, and attachment suggestions.

Design Principles:
- Structured I/O with Pydantic validation
- Thread context is truncated to last 3 emails to stay within token budget
- Tone enforcement via explicit system prompt
- Progress callbacks + cost tracking
"""
from __future__ import annotations

import asyncio
import logging
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

logger = logging.getLogger("neura.agents.email_draft")

VALID_TONES = {"professional", "friendly", "formal", "casual", "empathetic", "assertive"}
MAX_THREAD_EMAILS = 3
MAX_THREAD_CHARS = 6000


# =============================================================================
# INPUT VALIDATION
# =============================================================================

class EmailDraftInput(BaseModel):
    """Validated input for email draft agent."""
    context: str = Field(..., min_length=5, max_length=5000)
    purpose: str = Field(..., min_length=3, max_length=1000)
    tone: str = Field(default="professional", max_length=30)
    recipient_info: Optional[str] = Field(default=None, max_length=2000)
    previous_emails: Optional[List[str]] = Field(default=None)
    include_subject: bool = Field(default=True)

    @field_validator("context")
    @classmethod
    def validate_context(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Context cannot be empty or whitespace")
        return v

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Purpose cannot be empty or whitespace")
        return v

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_TONES:
            raise ValueError(
                f"Tone must be one of: {', '.join(sorted(VALID_TONES))}. Got: {v}"
            )
        return v

    @field_validator("previous_emails")
    @classmethod
    def validate_previous_emails(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if not v:
            return v
        # Keep only last N emails and truncate total chars
        truncated = v[-MAX_THREAD_EMAILS:]
        total = 0
        result: List[str] = []
        for email in reversed(truncated):
            if total + len(email) > MAX_THREAD_CHARS:
                break
            result.insert(0, email)
            total += len(email)
        return result


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class EmailDraftResult(BaseModel):
    """Complete email draft output."""
    subject: str = Field(default="", max_length=200)
    body: str = Field(..., min_length=1)
    tone: str = Field(default="professional")
    suggested_recipients: List[str] = Field(default_factory=list)
    attachments_suggested: List[str] = Field(default_factory=list)
    follow_up_actions: List[str] = Field(default_factory=list)
    word_count: int = Field(default=0, ge=0)
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def model_post_init(self, __context):
        if not self.word_count:
            self.word_count = len(self.body.split())


# =============================================================================
# EMAIL DRAFT AGENT
# =============================================================================
from backend.app.services.agents.agent_registry import register_agent


@register_agent(
    "email_draft",
    version="2.0",
    capabilities=["email_composition", "tone_control", "thread_context"],
    timeout_seconds=120,
)
class EmailDraftAgentV2(BaseAgentV2):
    """
    Production-grade email draft agent.

    Features:
    - Tone enforcement (professional, friendly, formal, casual, empathetic, assertive)
    - Thread context with truncation (last 3 emails, max 6000 chars)
    - Recipient context support
    - Follow-up action extraction
    - Attachment suggestions
    """

    async def execute(
        self,
        context: str,
        purpose: str,
        tone: str = "professional",
        recipient_info: Optional[str] = None,
        previous_emails: Optional[List[str]] = None,
        include_subject: bool = True,
        *,
        progress_callback: Optional[ProgressCallback] = None,
        timeout_seconds: int = 120,
    ) -> tuple[EmailDraftResult, Dict[str, Any]]:
        """Execute email drafting.

        Returns:
            Tuple of (EmailDraftResult, metadata dict).
        """
        try:
            validated = EmailDraftInput(
                context=context,
                purpose=purpose,
                tone=tone,
                recipient_info=recipient_info,
                previous_emails=previous_emails,
                include_subject=include_subject,
            )
        except Exception as e:
            raise ValidationError(str(e), field="input")

        def report_progress(percent: int, message: str, step: str, step_num: int):
            if progress_callback:
                progress_callback(ProgressUpdate(
                    percent=percent,
                    message=message,
                    current_step=step,
                    total_steps=1,
                    current_step_num=step_num,
                ))

        try:
            report_progress(10, "Composing email draft...", "drafting", 1)

            previous_context = ""
            if validated.previous_emails:
                previous_context = (
                    "\n\nPrevious emails in thread:\n"
                    + "\n---\n".join(validated.previous_emails)
                )

            recipient_context = ""
            if validated.recipient_info:
                recipient_context = f"\n\nRecipient information: {validated.recipient_info}"

            system_prompt = f"""You are an expert email writer. Draft an email based on the context and purpose provided.

Tone: {validated.tone}
{recipient_context}
{previous_context}

Provide your response as JSON:
{{
    "subject": "<email subject line>",
    "body": "<full email body>",
    "tone": "{validated.tone}",
    "suggested_recipients": ["<email if mentioned>"],
    "attachments_suggested": ["<suggested attachment if relevant>"],
    "follow_up_actions": ["<action items from this email>"]
}}"""

            result = await self._call_llm(
                system_prompt=system_prompt,
                user_prompt=f"Context: {validated.context}\n\nPurpose: {validated.purpose}",
                max_tokens=1500,
                timeout_seconds=timeout_seconds,
                temperature=0.7,
            )

            parsed = result["parsed"]

            report_progress(80, "Finalising draft...", "drafting", 1)

            draft = EmailDraftResult(
                subject=parsed.get("subject", "") if validated.include_subject else "",
                body=parsed.get("body", "Unable to generate email draft"),
                tone=parsed.get("tone", validated.tone),
                suggested_recipients=parsed.get("suggested_recipients", []),
                attachments_suggested=parsed.get("attachments_suggested", []),
                follow_up_actions=parsed.get("follow_up_actions", []),
            )

            cost_cents = self._estimate_cost_cents(
                result["input_tokens"], result["output_tokens"]
            )
            metadata = {
                "tokens_input": result["input_tokens"],
                "tokens_output": result["output_tokens"],
                "estimated_cost_cents": cost_cents,
            }

            report_progress(100, "Draft complete", "done", 1)
            return draft, metadata

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
            raise AgentError(str(e), code="EMAIL_DRAFT_FAILED", retryable=True)
