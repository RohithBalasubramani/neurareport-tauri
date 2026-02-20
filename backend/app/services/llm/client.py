# mypy: ignore-errors
"""
Unified LLM Client.

Provides a single interface for all LLM providers with:
- Automatic retry with exponential backoff
- Circuit breaker pattern for fault tolerance
- Fallback to secondary provider
- Response caching (memory and disk)
- Token counting and cost estimation
- Request/response validation
- Logging and monitoring
- Vision/multimodal support
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from pydantic import BaseModel

from .config import LLMConfig, LLMProvider, get_llm_config
from .providers import BaseProvider, LiteLLMProvider, _sanitize_error, get_provider
from backend.app.services.utils.llm import append_raw_llm_output as _append_raw_output

logger = logging.getLogger("neura.llm.client")

_MAX_LOG_PREVIEW = 2000  # max chars per message in log


def _summarize_messages(messages: List[Dict[str, Any]]) -> str:
    """Build a concise summary of messages for the LLM log."""
    parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "?")
        content = msg.get("content", "")
        if isinstance(content, list):
            # Multimodal: extract text parts
            text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
            content = " ".join(text_parts) or f"[{len(content)} content blocks]"
        text = str(content)
        if len(text) > _MAX_LOG_PREVIEW:
            text = text[:_MAX_LOG_PREVIEW] + f"... ({len(text)} chars total)"
        parts.append(f"  [{role}] {text}")
    return "\n".join(parts)


def _extract_response_text(response: Dict[str, Any]) -> str:
    """Extract the assistant text from an OpenAI-compatible response dict."""
    try:
        choices = response.get("choices") or []
        if choices:
            return choices[0].get("message", {}).get("content", "") or ""
    except (IndexError, KeyError, TypeError, AttributeError):
        pass
    return ""


# =============================================================================
# Circuit Breaker Pattern Implementation
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes in half-open before closing
    timeout_seconds: float = 60.0  # Time before moving from open to half-open
    failure_window_seconds: float = 120.0  # Window to count failures


class CircuitBreaker:
    """
    Circuit breaker for fault tolerance.

    Prevents cascading failures by stopping requests to failing services.
    Based on the pattern from resilience4j and Netflix Hystrix.
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._state_changed_at = time.time()
        self._failure_timestamps: deque = deque()
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, potentially transitioning from OPEN to HALF_OPEN."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._state_changed_at >= self.config.timeout_seconds:
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        self._state_changed_at = time.time()

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._failure_timestamps.clear()
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0

        logger.info(
            "circuit_breaker_state_change",
            extra={
                "event": "circuit_breaker_state_change",
                "breaker_name": self.name,
                "old_state": old_state.value,
                "new_state": new_state.value,
            }
        )

    def allow_request(self) -> bool:
        """Check if request should be allowed."""
        current_state = self.state  # This may trigger OPEN -> HALF_OPEN

        if current_state == CircuitState.CLOSED:
            return True
        elif current_state == CircuitState.OPEN:
            return False
        else:  # HALF_OPEN
            return True  # Allow test requests

    def record_success(self) -> None:
        """Record a successful request."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                # Clean old failures from window
                self._clean_old_failures()

    def record_failure(self) -> None:
        """Record a failed request."""
        with self._lock:
            now = time.time()
            self._last_failure_time = now

            if self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                self._failure_timestamps.append(now)
                self._clean_old_failures()

                if len(self._failure_timestamps) >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def _clean_old_failures(self) -> None:
        """Remove failures outside the failure window."""
        cutoff = time.time() - self.config.failure_window_seconds
        while self._failure_timestamps and self._failure_timestamps[0] < cutoff:
            self._failure_timestamps.popleft()

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                "breaker_name": self.name,
                "state": self._state.value,
                "failure_count": len(self._failure_timestamps),
                "success_count": self._success_count,
                "last_failure": self._last_failure_time,
                "state_changed_at": self._state_changed_at,
            }


# =============================================================================
# Response Cache Implementation
# =============================================================================

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    response: Dict[str, Any]
    created_at: float
    expires_at: float
    hit_count: int = 0
    request_hash: str = ""


class ResponseCache:
    """
    LRU cache for LLM responses with disk persistence.

    Features:
    - Memory cache with LRU eviction
    - Optional disk persistence for long-term caching
    - TTL-based expiration
    - Cache key based on request content hash
    """

    def __init__(
        self,
        max_memory_items: int = 100,
        max_disk_items: int = 1000,
        default_ttl_seconds: float = 3600.0,
        cache_dir: Optional[Path] = None,
    ):
        self.max_memory_items = max_memory_items
        self.max_disk_items = max_disk_items
        self.default_ttl_seconds = default_ttl_seconds
        self.cache_dir = cache_dir

        self._memory_cache: Dict[str, CacheEntry] = {}
        self._access_order: deque = deque()
        self._lock = threading.Lock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}

        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

    def _compute_key(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        **kwargs: Any,
    ) -> str:
        """Compute cache key from request parameters."""
        # Create deterministic hash of request
        key_data = {
            "messages": messages,
            "model": model,
            "kwargs": {k: v for k, v in sorted(kwargs.items()) if k not in ("stream",)},
        }
        key_json = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_json.encode()).hexdigest()[:32]

    def get(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Get cached response if available."""
        key = self._compute_key(messages, model, **kwargs)

        with self._lock:
            # Check memory cache
            entry = self._memory_cache.get(key)
            if entry:
                if time.time() < entry.expires_at:
                    entry.hit_count += 1
                    self._stats["hits"] += 1
                    # Move to end of access order (most recent)
                    if key in self._access_order:
                        self._access_order.remove(key)
                    self._access_order.append(key)
                    return entry.response
                else:
                    # Expired
                    del self._memory_cache[key]
                    if key in self._access_order:
                        self._access_order.remove(key)

            # Check disk cache
            if self.cache_dir:
                disk_response = self._read_from_disk(key)
                if disk_response:
                    self._stats["hits"] += 1
                    # Promote to memory cache
                    self._set_memory(key, disk_response)
                    return disk_response

            self._stats["misses"] += 1
            return None

    def set(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        response: Dict[str, Any],
        ttl_seconds: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """Cache a response."""
        key = self._compute_key(messages, model, **kwargs)
        ttl = ttl_seconds or self.default_ttl_seconds

        with self._lock:
            self._set_memory(key, response, ttl)

            # Also write to disk for persistence
            if self.cache_dir:
                self._write_to_disk(key, response, ttl)

    def _set_memory(
        self,
        key: str,
        response: Dict[str, Any],
        ttl_seconds: Optional[float] = None,
    ) -> None:
        """Set entry in memory cache."""
        ttl = ttl_seconds or self.default_ttl_seconds
        now = time.time()

        # Evict if at capacity
        while len(self._memory_cache) >= self.max_memory_items and self._access_order:
            oldest_key = self._access_order.popleft()
            if oldest_key in self._memory_cache:
                del self._memory_cache[oldest_key]
                self._stats["evictions"] += 1

        self._memory_cache[key] = CacheEntry(
            response=response,
            created_at=now,
            expires_at=now + ttl,
            request_hash=key,
        )
        self._access_order.append(key)

    def _read_from_disk(self, key: str) -> Optional[Dict[str, Any]]:
        """Read cached response from disk."""
        if not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None

        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            if time.time() < data.get("expires_at", 0):
                return data.get("response")
            else:
                # Expired, delete file
                cache_file.unlink(missing_ok=True)
                return None
        except Exception:
            return None

    def _write_to_disk(
        self,
        key: str,
        response: Dict[str, Any],
        ttl_seconds: float,
    ) -> None:
        """Write cached response to disk."""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / f"{key}.json"
        try:
            data = {
                "response": response,
                "created_at": time.time(),
                "expires_at": time.time() + ttl_seconds,
            }
            cache_file.write_text(json.dumps(data), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to write cache to disk: {e}")

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._memory_cache.clear()
            self._access_order.clear()
            self._stats = {"hits": 0, "misses": 0, "evictions": 0}

            if self.cache_dir:
                for f in self.cache_dir.glob("*.json"):
                    try:
                        f.unlink()
                    except Exception:
                        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total if total > 0 else 0
            return {
                **self._stats,
                "hit_rate": hit_rate,
                "memory_size": len(self._memory_cache),
            }


# =============================================================================
# Token Counter and Cost Estimator
# =============================================================================

# Approximate token costs per 1K tokens (Claude models)
TOKEN_COSTS: Dict[str, Dict[str, float]] = {
    "claude-sonnet": {"input": 0.003, "output": 0.015},
    "claude-opus": {"input": 0.015, "output": 0.075},
    "claude-haiku": {"input": 0.00025, "output": 0.00125},
    "sonnet": {"input": 0.003, "output": 0.015},
    "opus": {"input": 0.015, "output": 0.075},
    "haiku": {"input": 0.00025, "output": 0.00125},
}


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses a simple heuristic: ~4 characters per token for English text.
    For more accurate counting, use tiktoken library.
    """
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Fallback to heuristic
        return max(1, len(text) // 4)


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate cost for a completion."""
    costs = TOKEN_COSTS.get(model, TOKEN_COSTS.get("sonnet", {"input": 0.003, "output": 0.015}))
    input_cost = (input_tokens / 1000) * costs["input"]
    output_cost = (output_tokens / 1000) * costs["output"]
    return input_cost + output_cost


@dataclass
class UsageTracker:
    """Track token usage and costs."""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    request_count: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record(self, model: str, input_tokens: int, output_tokens: int) -> None:
        """Record token usage from a request."""
        with self._lock:
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += estimate_cost(model, input_tokens, output_tokens)
            self.request_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_tokens": self.total_input_tokens + self.total_output_tokens,
                "estimated_cost_usd": round(self.total_cost, 4),
                "request_count": self.request_count,
            }

    def reset(self) -> None:
        """Reset usage statistics."""
        with self._lock:
            self.total_input_tokens = 0
            self.total_output_tokens = 0
            self.total_cost = 0.0
            self.request_count = 0


# Global usage tracker
_usage_tracker = UsageTracker()

# Raw output logging is handled by backend.app.services.utils.llm


class LLMClient:
    """
    Unified LLM client supporting multiple providers.

    Features:
    - Circuit breaker for fault tolerance
    - Response caching (memory and disk)
    - Token usage tracking
    - Automatic retry with exponential backoff
    - Fallback to secondary provider

    Usage:
        client = LLMClient()
        response = client.complete(
            messages=[{"role": "user", "content": "Hello"}],
            description="greeting"
        )
    """

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        provider: Optional[BaseProvider] = None,
        enable_cache: bool = True,
        enable_circuit_breaker: bool = True,
        cache_dir: Optional[Path] = None,
    ):
        self.config = config or get_llm_config()
        self._provider = provider or get_provider(self.config)
        self._fallback_provider: Optional[BaseProvider] = None

        # Initialize circuit breaker
        self._circuit_breaker: Optional[CircuitBreaker] = None
        if enable_circuit_breaker:
            self._circuit_breaker = CircuitBreaker(
                name=f"llm_{self.config.provider.value}",
                config=CircuitBreakerConfig(
                    failure_threshold=self.config.max_retries + 2,
                    timeout_seconds=60.0,
                )
            )

        # Initialize response cache
        self._cache: Optional[ResponseCache] = None
        if isinstance(self._provider, LiteLLMProvider):
            enable_cache = os.getenv("LLM_CACHE_ENABLED", "false").lower() in {"1", "true", "yes"}

        if enable_cache:
            default_cache_dir = cache_dir
            if not default_cache_dir and os.getenv("LLM_CACHE_DIR"):
                _raw_dir = Path(os.getenv("LLM_CACHE_DIR", ""))
                # Reject paths with traversal components
                if ".." not in str(_raw_dir):
                    default_cache_dir = _raw_dir
                else:
                    logger.warning("llm_cache_dir_rejected", extra={"reason": "path contains '..'"})
            try:
                max_items = int(os.getenv("LLM_CACHE_MAX_ITEMS", "100"))
            except (ValueError, TypeError):
                max_items = 100
            try:
                ttl = float(os.getenv("LLM_CACHE_TTL_SECONDS", "3600"))
            except (ValueError, TypeError):
                ttl = 3600.0
            _max_items = min(max(1, max_items), 10000)
            self._cache = ResponseCache(
                max_memory_items=_max_items,
                default_ttl_seconds=ttl,
                cache_dir=default_cache_dir,
            )

        # Initialize usage tracker
        self._usage_tracker = UsageTracker()

        # Fallback provider (not used for Claude Code CLI - single provider only)
        self._fallback_provider = None

    @property
    def provider(self) -> BaseProvider:
        """Get the current provider."""
        return self._provider

    @property
    def model(self) -> str:
        """Get the current model name."""
        return self.config.model

    def complete(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        description: str = "llm_call",
        use_cache: bool = True,
        cache_ttl: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute a chat completion with retries, caching, and fallback.

        Args:
            messages: List of message dicts with role and content
            model: Optional model override
            description: Description for logging
            use_cache: Whether to use response caching
            cache_ttl: Optional cache TTL override in seconds
            **kwargs: Additional provider-specific options

        Returns:
            OpenAI-compatible response dict
        """
        model = model or self.config.model
        delay = self.config.retry_delay
        last_exc: Optional[Exception] = None

        # Check cache first
        if use_cache and self._cache and not kwargs.get("stream"):
            cached = self._cache.get(messages, model, **kwargs)
            if cached:
                logger.debug(
                    "llm_cache_hit",
                    extra={
                        "event": "llm_cache_hit",
                        "description": description,
                        "model": model,
                    }
                )
                return cached

        # Check circuit breaker
        if self._circuit_breaker and not self._circuit_breaker.allow_request():
            logger.warning(
                "llm_circuit_open",
                extra={
                    "event": "llm_circuit_open",
                    "description": description,
                    "provider": self.config.provider.value,
                }
            )
            # Try fallback immediately if circuit is open
            if self._fallback_provider:
                return self._try_fallback(messages, model, description, **kwargs)
            raise RuntimeError(
                "AI service is temporarily unavailable due to repeated failures. "
                "Please try again in a few minutes. If the problem persists, check your API configuration."
            )

        _llm_logger = logging.getLogger("neura.llm")

        for attempt in range(1, self.config.max_retries + 1):
            try:
                logger.info(
                    "llm_call_start",
                    extra={
                        "event": "llm_call_start",
                        "description": description,
                        "attempt": attempt,
                        "model": model,
                        "provider": self.config.provider.value,
                    }
                )

                # Log the input prompt/messages
                _llm_logger.info(
                    "LLM_INPUT [%s] model=%s messages=%d\n%s",
                    description,
                    model,
                    len(messages),
                    _summarize_messages(messages),
                )

                start_time = time.time()
                response = self._provider.chat_completion(
                    messages=messages,
                    model=model,
                    **kwargs
                )
                latency_ms = (time.time() - start_time) * 1000

                _append_raw_output(description, response)

                # Record success with circuit breaker
                if self._circuit_breaker:
                    self._circuit_breaker.record_success()

                # Track usage
                usage = response.get("usage", {})
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                self._usage_tracker.record(model, input_tokens, output_tokens)
                _usage_tracker.record(model, input_tokens, output_tokens)

                # Log the output response content
                output_text = _extract_response_text(response)
                _llm_logger.info(
                    "LLM_OUTPUT [%s] model=%s latency=%.0fms tokens=%d/%d\n%s",
                    description,
                    model,
                    latency_ms,
                    input_tokens,
                    output_tokens,
                    output_text[:4000] if output_text else "(empty)",
                )

                logger.info(
                    "llm_call_success",
                    extra={
                        "event": "llm_call_success",
                        "description": description,
                        "attempt": attempt,
                        "model": model,
                        "provider": self.config.provider.value,
                        "latency_ms": round(latency_ms, 2),
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                    }
                )

                # Cache successful response
                if use_cache and self._cache and not kwargs.get("stream"):
                    self._cache.set(messages, model, response, cache_ttl, **kwargs)

                return response

            except Exception as exc:
                last_exc = exc

                _llm_logger.error(
                    "LLM_ERROR [%s] model=%s attempt=%d error=%s",
                    description,
                    model,
                    attempt,
                    _sanitize_error(exc),
                )

                # Record failure with circuit breaker
                if self._circuit_breaker:
                    self._circuit_breaker.record_failure()

                # Check for quota/rate limit errors
                if _is_quota_exceeded_error(exc):
                    logger.warning(
                        "llm_quota_exceeded",
                        extra={
                            "event": "llm_quota_exceeded",
                            "description": description,
                            "provider": self.config.provider.value,
                        }
                    )
                    break

                # Check for temperature errors (some models don't support it)
                if "temperature" in kwargs and _is_temperature_unsupported_error(exc):
                    logger.info(
                        "llm_temperature_override_removed",
                        extra={
                            "event": "llm_temperature_override_removed",
                            "description": description,
                            "model": model,
                        }
                    )
                    kwargs.pop("temperature", None)
                    continue

                # Check for context length errors
                if _is_context_length_error(exc):
                    logger.warning(
                        "llm_context_length_exceeded",
                        extra={
                            "event": "llm_context_length_exceeded",
                            "description": description,
                            "model": model,
                        }
                    )
                    break  # Don't retry, won't help

                logger.warning(
                    "llm_call_retry",
                    extra={
                        "event": "llm_call_retry",
                        "description": description,
                        "attempt": attempt,
                        "max_attempts": self.config.max_retries,
                        "retry_in": delay if attempt < self.config.max_retries else None,
                        "error": _sanitize_error(exc),
                        "error_type": type(exc).__name__,
                    }
                )

                if attempt >= self.config.max_retries:
                    break

                time.sleep(delay)
                delay *= self.config.retry_multiplier

        # Try fallback provider if available
        fallback_exc: Optional[Exception] = None
        if self._fallback_provider and last_exc:
            try:
                return self._try_fallback(messages, model, description, **kwargs)
            except Exception as fb_exc:
                fallback_exc = fb_exc
                logger.warning(
                    "llm_fallback_also_failed",
                    extra={
                        "event": "llm_fallback_also_failed",
                        "description": description,
                        "primary_error": _sanitize_error(last_exc),
                        "fallback_error": _sanitize_error(fb_exc),
                    }
                )

        # All attempts failed
        assert last_exc is not None
        fallback_attempted = self._fallback_provider is not None
        logger.error(
            "llm_call_failed",
            extra={
                "event": "llm_call_failed",
                "description": description,
                "attempts": self.config.max_retries,
                "model": model,
                "error_type": type(last_exc).__name__,
                "fallback_attempted": fallback_attempted,
                "fallback_error": _sanitize_error(fallback_exc) if fallback_exc else None,
            },
            exc_info=last_exc,
        )

        if _is_quota_exceeded_error(last_exc):
            raise RuntimeError(
                "AI service quota exceeded. Please check your API plan and billing details, "
                "or wait for the rate limit to reset."
            ) from last_exc

        if _is_context_length_error(last_exc):
            raise RuntimeError(
                "The document is too large for the AI to process. "
                "Please try with a smaller document or fewer pages."
            ) from last_exc

        # Include fallback info in error message if fallback was attempted
        error_msg = "AI processing failed. Please try again. If the problem persists, check your API configuration or contact support."
        if fallback_exc:
            error_msg = f"AI processing failed (primary and fallback providers both failed). Please try again. If the problem persists, check your API configuration or contact support."

        raise RuntimeError(error_msg) from last_exc

    def complete_structured(
        self,
        messages: List[Dict[str, Any]],
        response_model: type[BaseModel],
        model: Optional[str] = None,
        description: str = "llm_structured",
        **kwargs: Any,
    ) -> BaseModel:
        """Execute a structured completion using Instructor-compatible models."""
        try:
            import instructor
        except ImportError as exc:
            raise RuntimeError("instructor package is required. Install with: pip install instructor") from exc

        model = model or self.config.model
        try:
            if isinstance(self._provider, LiteLLMProvider):
                litellm = self._provider.get_client()
                instructor_client = instructor.from_litellm(litellm.completion)
                return instructor_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_model=response_model,
                    **kwargs,
                )

            base_client = self._provider.get_client()
            instructor_client = instructor.from_openai(base_client)
            return instructor_client.chat.completions.create(
                model=model,
                messages=messages,
                response_model=response_model,
                **kwargs,
            )
        except Exception:
            # Fallback to manual parsing of JSON output.
            response = self.complete(
                messages=messages,
                model=model,
                description=description,
                **kwargs,
            )
            content = (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            try:
                return response_model.model_validate_json(content)
            except AttributeError:
                return response_model.parse_raw(content)

    def _try_fallback(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        description: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Try fallback provider."""
        logger.info(
            "llm_fallback_attempt",
            extra={
                "event": "llm_fallback_attempt",
                "description": description,
                "fallback_provider": self.config.fallback_provider.value if self.config.fallback_provider else None,
            }
        )
        try:
            response = self._fallback_provider.chat_completion(
                messages=messages,
                model=self.config.fallback_model,
                **kwargs
            )
            _append_raw_output(f"{description}_fallback", response)

            # Track usage for fallback
            usage = response.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            fallback_model = self.config.fallback_model or model
            self._usage_tracker.record(fallback_model, input_tokens, output_tokens)
            _usage_tracker.record(fallback_model, input_tokens, output_tokens)

            return response
        except Exception as fallback_exc:
            logger.error(
                "llm_fallback_failed",
                extra={
                    "event": "llm_fallback_failed",
                    "description": description,
                    "error": _sanitize_error(fallback_exc),
                }
            )
            raise

    def complete_with_vision(
        self,
        text: str,
        images: List[Union[str, bytes, Path]],
        description: str = "vision_call",
        model: Optional[str] = None,
        detail: str = "auto",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute a chat completion with vision/image inputs.

        Args:
            text: Text prompt
            images: List of images (paths, bytes, base64 strings, or URLs)
            description: Description for logging
            model: Optional model override (uses vision model by default)
            detail: Image detail level (auto, low, high)
            **kwargs: Additional options

        Returns:
            OpenAI-compatible response dict
        """
        model = model or self.config.get_vision_model()

        vision_message = self._provider.prepare_vision_message(
            text=text,
            images=images,
            detail=detail,
        )

        return self.complete(
            messages=[vision_message],
            model=model,
            description=description,
            **kwargs
        )

    def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        description: str = "llm_stream",
        **kwargs: Any,
    ) -> Iterator[Dict[str, Any]]:
        """
        Execute a streaming chat completion.

        Yields:
            OpenAI-compatible chunk dicts
        """
        model = model or self.config.model

        logger.info(
            "llm_stream_start",
            extra={
                "event": "llm_stream_start",
                "description": description,
                "model": model,
                "provider": self.config.provider.value,
            }
        )

        try:
            for chunk in self._provider.chat_completion_stream(
                messages=messages,
                model=model,
                **kwargs
            ):
                yield chunk

            logger.info(
                "llm_stream_complete",
                extra={
                    "event": "llm_stream_complete",
                    "description": description,
                    "model": model,
                }
            )
        except Exception as exc:
            logger.error(
                "llm_stream_failed",
                extra={
                    "event": "llm_stream_failed",
                    "description": description,
                    "error": _sanitize_error(exc),
                }
            )
            raise

    def list_models(self) -> List[str]:
        """List available models from the current provider."""
        return self._provider.list_models()

    def health_check(self) -> bool:
        """Check if the provider is available."""
        return self._provider.health_check()


# Global client instance
_client: Optional[LLMClient] = None
_client_lock = threading.Lock()


def get_llm_client(force_new: bool = False) -> LLMClient:
    """Get the global LLM client instance."""
    global _client
    with _client_lock:
        if _client is None or force_new:
            _client = LLMClient()
    return _client


def call_completion(
    client: Any,  # Can be LLMClient or OpenAI client for backwards compatibility
    *,
    model: str,
    messages: List[Dict[str, Any]],
    description: str,
    timeout: Optional[float] = None,
    **kwargs: Any,
) -> Any:
    """
    Execute a chat completion - backwards compatible with existing code.

    This function provides compatibility with the existing call_chat_completion
    interface while supporting the new multi-provider system.

    Args:
        client: LLMClient or OpenAI client
        model: Model name
        messages: Message payload
        description: Description for logging
        timeout: Optional timeout (handled by provider config)
        **kwargs: Additional options

    Returns:
        Response object (dict or OpenAI response)
    """
    if isinstance(client, LLMClient):
        return client.complete(
            messages=messages,
            model=model,
            description=description,
            **kwargs
        )

    # Backwards compatibility: use existing OpenAI client
    # Import the old implementation
    from ..utils.llm import call_chat_completion as legacy_call
    return legacy_call(
        client,
        model=model,
        messages=messages,
        description=description,
        timeout=timeout,
        **kwargs
    )


def call_completion_with_vision(
    client: Any,
    *,
    text: str,
    images: List[Union[str, bytes, Path]],
    model: str,
    description: str,
    detail: str = "auto",
    **kwargs: Any,
) -> Any:
    """
    Execute a chat completion with vision inputs.

    Args:
        client: LLMClient or OpenAI client
        text: Text prompt
        images: List of images
        model: Model name
        description: Description for logging
        detail: Image detail level
        **kwargs: Additional options

    Returns:
        Response object
    """
    if isinstance(client, LLMClient):
        return client.complete_with_vision(
            text=text,
            images=images,
            model=model,
            description=description,
            detail=detail,
            **kwargs
        )

    # Backwards compatibility: build vision message manually
    import base64

    content: List[Dict[str, Any]] = [{"type": "text", "text": text}]

    for image in images:
        if isinstance(image, Path):
            image_data = base64.b64encode(image.read_bytes()).decode("utf-8")
            media_type = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"
            image_url = f"data:{media_type};base64,{image_data}"
        elif isinstance(image, bytes):
            image_data = base64.b64encode(image).decode("utf-8")
            image_url = f"data:image/png;base64,{image_data}"
        else:
            image_url = image if image.startswith(("data:", "http")) else f"data:image/png;base64,{image}"

        content.append({
            "type": "image_url",
            "image_url": {"url": image_url, "detail": detail}
        })

    messages = [{"role": "user", "content": content}]

    from ..utils.llm import call_chat_completion as legacy_call
    return legacy_call(
        client,
        model=model,
        messages=messages,
        description=description,
        **kwargs
    )


def get_available_models() -> List[str]:
    """Get list of available models from the current provider."""
    client = get_llm_client()
    return client.list_models()


def health_check() -> Dict[str, Any]:
    """Check health of the LLM provider."""
    client = get_llm_client()
    config = client.config

    result = {
        "provider": config.provider.value,
        "model": config.model,
        "healthy": False,
        "fallback_available": config.fallback_provider is not None,
    }

    try:
        result["healthy"] = client.health_check()
        if result["healthy"]:
            result["available_models"] = client.list_models()[:5]  # First 5 models
    except Exception as e:
        logger.warning("llm_health_check_failed", extra={"error": str(e)})
        result["error"] = "Health check failed"

    return result


# Helper functions
# NOTE: _append_raw_output is imported from backend.app.services.utils.llm


def _is_quota_exceeded_error(exc: BaseException) -> bool:
    """Check if exception represents a quota/rate limit error."""
    detail = str(exc).lower()

    if "insufficient_quota" in detail:
        return True
    if "quota" in detail and ("exceeded" in detail or "insufficient" in detail):
        return True
    if "rate_limit" in detail or "ratelimit" in detail:
        return True

    # Check for OpenAI-specific error structure
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        error = body.get("error", {})
        if isinstance(error, dict):
            code = str(error.get("code", "")).lower()
            if code in ("insufficient_quota", "rate_limit_exceeded"):
                return True

    return False


def _is_temperature_unsupported_error(exc: BaseException) -> bool:
    """Check if exception is about unsupported temperature."""
    detail = str(exc).lower()
    return "temperature" in detail and "unsupported" in detail


def _is_context_length_error(exc: BaseException) -> bool:
    """Check if exception is about context length exceeded."""
    detail = str(exc).lower()

    context_indicators = [
        "context_length_exceeded",
        "maximum context length",
        "token limit",
        "too many tokens",
        "context window",
        "max_tokens",
        "input too long",
    ]

    return any(indicator in detail for indicator in context_indicators)


def _is_invalid_request_error(exc: BaseException) -> bool:
    """Check if exception is an invalid request error."""
    detail = str(exc).lower()

    invalid_indicators = [
        "invalid_request",
        "invalid request",
        "bad request",
        "malformed",
        "invalid_api_key",
        "invalid api key",
    ]

    return any(indicator in detail for indicator in invalid_indicators)


def get_global_usage_stats() -> Dict[str, Any]:
    """Get global token usage statistics."""
    return _usage_tracker.get_stats()


def reset_global_usage_stats() -> None:
    """Reset global token usage statistics."""
    _usage_tracker.reset()
