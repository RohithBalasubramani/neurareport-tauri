"""
Base Agent V2 - Shared infrastructure for all production-grade agents.

Provides:
- Lazy-loaded OpenAI client with model-aware parameter handling
- Robust JSON parsing from LLM responses (handles code blocks, partial JSON)
- Token counting and cost estimation
- Timeout handling with proper error categorization
- Progress callback infrastructure

All production agents extend this base class.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("neura.agents.base")


# ---------------------------------------------------------------------------
# Error types (re-exported from research_agent for backward compat)
# ---------------------------------------------------------------------------
class AgentError(Exception):
    """Base class for agent errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        retryable: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.retryable = retryable
        self.details = details or {}
        super().__init__(message)


class ValidationError(AgentError):
    """Input validation error."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            retryable=False,
            details={"field": field} if field else {},
        )


class LLMTimeoutError(AgentError):
    """LLM request timed out."""

    def __init__(self, timeout_seconds: int):
        super().__init__(
            f"LLM request timed out after {timeout_seconds} seconds",
            code="LLM_TIMEOUT",
            retryable=True,
            details={"timeout_seconds": timeout_seconds},
        )


class LLMRateLimitError(AgentError):
    """LLM rate limit exceeded."""

    def __init__(self, retry_after: Optional[int] = None):
        super().__init__(
            "LLM rate limit exceeded",
            code="LLM_RATE_LIMITED",
            retryable=True,
            details={"retry_after": retry_after},
        )


class LLMResponseError(AgentError):
    """LLM returned invalid response."""

    def __init__(self, message: str):
        super().__init__(
            message,
            code="LLM_RESPONSE_ERROR",
            retryable=True,
        )


class LLMContentFilterError(AgentError):
    """LLM content was filtered."""

    def __init__(self, reason: str):
        super().__init__(
            f"Content was filtered: {reason}",
            code="LLM_CONTENT_FILTERED",
            retryable=False,
            details={"reason": reason},
        )


# ---------------------------------------------------------------------------
# Progress callback
# ---------------------------------------------------------------------------
@dataclass
class ProgressUpdate:
    """Progress update for long-running operations."""
    percent: int
    message: str
    current_step: str
    total_steps: int
    current_step_num: int


ProgressCallback = Callable[[ProgressUpdate], None]


# ---------------------------------------------------------------------------
# Base Agent
# ---------------------------------------------------------------------------
class BaseAgentV2(ABC):
    """
    Abstract base for all production-grade V2 agents.

    Subclasses implement execute() and define their input/output models.
    The base class provides shared LLM calling, JSON parsing, error
    categorization, and cost tracking infrastructure.

    Supports all LLM providers: OpenAI, Claude Code CLI, Anthropic, etc.
    """

    # Token cost estimates (per 1K tokens) — overridable per agent
    INPUT_COST_PER_1K: float = 0.003
    OUTPUT_COST_PER_1K: float = 0.015

    # Timeout settings
    DEFAULT_TIMEOUT_SECONDS: int = 120
    MAX_TIMEOUT_SECONDS: int = 300

    def __init__(self):
        self._llm_client = None
        self._model: Optional[str] = None

    def _get_llm_client(self):
        """Get unified LLM client lazily."""
        if self._llm_client is None:
            from backend.app.services.llm.client import get_llm_client
            self._llm_client = get_llm_client()
        return self._llm_client

    def _get_model(self) -> str:
        """Get model name from LLM config."""
        if self._model is None:
            from backend.app.services.llm.config import get_llm_config
            self._model = get_llm_config().model
        return self._model

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        timeout_seconds: Optional[int] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Make an LLM call with proper error handling and token tracking.

        Uses the unified LLM client which supports all providers:
        OpenAI, Claude Code CLI, Anthropic, etc.

        Args:
            system_prompt: System prompt for the LLM.
            user_prompt: User prompt for the LLM.
            max_tokens: Maximum tokens in the response.
            timeout_seconds: Timeout for the LLM call.
            temperature: Sampling temperature.

        Returns:
            Dict with keys: raw, parsed, input_tokens, output_tokens.

        Raises:
            LLMTimeoutError: If the call times out.
            LLMRateLimitError: If rate limited.
            LLMContentFilterError: If content was filtered.
            LLMResponseError: If response can't be parsed.
            AgentError: For other LLM errors.
        """
        timeout = timeout_seconds or self.DEFAULT_TIMEOUT_SECONDS
        client = self._get_llm_client()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            loop = asyncio.get_running_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: client.complete(
                        messages=messages,
                        description="agent_call_v2",
                        max_tokens=max_tokens,
                        temperature=temperature,
                    ),
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise LLMTimeoutError(timeout)
        except Exception as exc:
            self._categorize_and_raise(exc, timeout)

        # Extract content from OpenAI-compatible response
        content = (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        ) or ""

        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        # Parse JSON from response
        parsed = self._parse_json_response(content)

        return {
            "raw": content,
            "parsed": parsed,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }

    def _categorize_and_raise(self, exc: Exception, timeout: int) -> None:
        """Categorize an exception and raise the appropriate AgentError."""
        error_str = str(exc).lower()

        if "rate limit" in error_str or "rate_limit" in error_str:
            raise LLMRateLimitError()
        elif "timeout" in error_str:
            raise LLMTimeoutError(timeout)
        elif "content filter" in error_str or "content_filter" in error_str:
            raise LLMContentFilterError(str(exc))
        else:
            raise AgentError(
                str(exc),
                code="LLM_ERROR",
                retryable=True,
            )

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks.

        This method handles common LLM output patterns:
        - Raw JSON
        - JSON wrapped in ```json ... ``` code blocks
        - JSON embedded in natural language text
        - Partial/truncated JSON (returns empty dict)

        Raises:
            LLMResponseError: If no valid JSON can be extracted.
        """
        if not content or not content.strip():
            return {}

        cleaned = content.strip()

        # Handle ```json ... ``` blocks
        json_block_match = re.search(
            r"```(?:json)?\s*\n?(.*?)\n?```", cleaned, re.DOTALL
        )
        if json_block_match:
            cleaned = json_block_match.group(1).strip()
        elif cleaned.startswith("```"):
            parts = cleaned.split("```", 2)
            if len(parts) >= 2:
                cleaned = parts[1].strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object or array in the content
        for pattern in [r"\{.*\}", r"\[.*\]"]:
            match = re.search(pattern, cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        logger.warning(f"Failed to parse JSON from LLM output: {content[:200]}...")
        raise LLMResponseError("Failed to parse JSON from LLM response")

    def _estimate_cost_cents(
        self, input_tokens: int, output_tokens: int
    ) -> int:
        """Estimate cost in cents from token counts."""
        return int(
            (input_tokens / 1000 * self.INPUT_COST_PER_1K * 100)
            + (output_tokens / 1000 * self.OUTPUT_COST_PER_1K * 100)
        )

    @abstractmethod
    async def execute(
        self,
        *,
        progress_callback: Optional[ProgressCallback] = None,
        timeout_seconds: int = 120,
        **kwargs: Any,
    ) -> tuple[Any, Dict[str, Any]]:
        """Execute the agent.

        All agents return a tuple of (result_model, metadata_dict).
        The metadata dict must contain: tokens_input, tokens_output,
        estimated_cost_cents.
        """
        ...
