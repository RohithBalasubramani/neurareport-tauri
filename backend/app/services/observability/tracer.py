from __future__ import annotations

"""
Decorator-based span timing with Prometheus integration.

Provides a ``@trace`` decorator that measures execution time for both
sync and async functions, records ``SpanRecord`` objects into a bounded
in-memory collector, and optionally pushes latency observations to the
Prometheus ``LLM_INFERENCE_DURATION`` histogram and cost data to the
``CostTracker``.
"""

import functools
import inspect
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Dict, List, Optional, TypeVar, cast

from backend.app.services.observability.metrics import LLM_INFERENCE_DURATION
from backend.app.services.observability.cost_tracker import get_cost_tracker

logger = logging.getLogger("neura.observability.tracer")

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SpanRecord:
    """Timing record for a single traced invocation."""

    operation: str
    start_time: float
    end_time: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000.0


# ---------------------------------------------------------------------------
# SpanCollector
# ---------------------------------------------------------------------------

class SpanCollector:
    """
    Thread-safe, bounded in-memory store for ``SpanRecord`` objects.

    Keeps at most *maxlen* spans (default 1 000) in a ring buffer so
    memory usage stays predictable under sustained load.
    """

    def __init__(self, maxlen: int = 1000) -> None:
        self._spans: Deque[SpanRecord] = deque(maxlen=maxlen)
        self._lock = threading.Lock()

    def record(self, span: SpanRecord) -> None:
        """Append a span (thread-safe; oldest spans evicted when full)."""
        with self._lock:
            self._spans.append(span)

    def get_recent(self, n: int = 100) -> List[SpanRecord]:
        """Return the *n* most recent spans (newest last)."""
        with self._lock:
            items = list(self._spans)
        return items[-n:]

    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Compute latency percentiles, success rate, and count.

        If *operation* is given, only spans matching that name are
        considered; otherwise all recorded spans are used.
        """
        with self._lock:
            spans = [s for s in self._spans if operation is None or s.operation == operation]

        if not spans:
            return {
                "operation": operation or "__all__",
                "count": 0,
                "success_rate": 0.0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
            }

        durations = sorted(s.duration_ms for s in spans)
        successes = sum(1 for s in spans if s.success)
        count = len(spans)

        def _percentile(sorted_vals: List[float], pct: float) -> float:
            idx = int(pct / 100.0 * (len(sorted_vals) - 1))
            return round(sorted_vals[idx], 3)

        return {
            "operation": operation or "__all__",
            "count": count,
            "success_rate": round(successes / count, 4) if count else 0.0,
            "p50_ms": _percentile(durations, 50),
            "p95_ms": _percentile(durations, 95),
            "p99_ms": _percentile(durations, 99),
        }


# ---------------------------------------------------------------------------
# Module-level collector singleton
# ---------------------------------------------------------------------------

_collector = SpanCollector()


def get_span_collector() -> SpanCollector:
    """Return the module-level ``SpanCollector`` singleton."""
    return _collector


# ---------------------------------------------------------------------------
# @trace decorator
# ---------------------------------------------------------------------------

def trace(
    operation: Optional[str] = None,
    record_cost: bool = False,
) -> Callable[[F], F]:
    """
    Decorator factory that times function execution and records spans.

    Parameters
    ----------
    operation:
        Logical name for the span.  Defaults to the decorated function's
        qualified name (``module.func``).
    record_cost:
        If ``True`` **and** the decorated function returns a ``dict``
        containing a ``"usage"`` key, token counts are forwarded to the
        ``CostTracker`` singleton.

    The decorator transparently handles both synchronous and ``async``
    functions.
    """

    def decorator(fn: F) -> F:
        op_name = operation or f"{fn.__module__}.{fn.__qualname__}"

        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start = time.perf_counter()
                error_msg: Optional[str] = None
                success = True
                result: Any = None
                try:
                    result = await fn(*args, **kwargs)
                    return result
                except Exception as exc:
                    success = False
                    error_msg = f"{type(exc).__name__}: {exc}"
                    raise
                finally:
                    end = time.perf_counter()
                    _finish_span(
                        op_name=op_name,
                        start=start,
                        end=end,
                        success=success,
                        error_msg=error_msg,
                        result=result,
                        record_cost=record_cost,
                    )

            return cast(F, async_wrapper)

        else:
            @functools.wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                start = time.perf_counter()
                error_msg: Optional[str] = None
                success = True
                result: Any = None
                try:
                    result = fn(*args, **kwargs)
                    return result
                except Exception as exc:
                    success = False
                    error_msg = f"{type(exc).__name__}: {exc}"
                    raise
                finally:
                    end = time.perf_counter()
                    _finish_span(
                        op_name=op_name,
                        start=start,
                        end=end,
                        success=success,
                        error_msg=error_msg,
                        result=result,
                        record_cost=record_cost,
                    )

            return cast(F, sync_wrapper)

    return decorator


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _finish_span(
    *,
    op_name: str,
    start: float,
    end: float,
    success: bool,
    error_msg: Optional[str],
    result: Any,
    record_cost: bool,
) -> None:
    """Post-processing shared by sync and async wrappers."""
    duration = end - start
    latency_ms = round(duration * 1000.0, 3)

    span = SpanRecord(
        operation=op_name,
        start_time=start,
        end_time=end,
        success=success,
        error=error_msg,
        metadata={"latency_ms": latency_ms},
    )
    _collector.record(span)

    # Prometheus histogram for LLM / agent operations
    if op_name.startswith(("llm_", "agent_")):
        try:
            LLM_INFERENCE_DURATION.labels(model="unknown", operation=op_name).observe(duration)
        except Exception:
            pass  # Prometheus not available or labels mismatch

    # Forward token usage to CostTracker when requested
    if record_cost and success and isinstance(result, dict):
        usage = result.get("usage")
        if isinstance(usage, dict):
            try:
                model = result.get("model", "unknown")
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                get_cost_tracker().record(
                    operation=op_name,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )
            except Exception as exc:
                logger.debug(
                    "trace_cost_record_failed",
                    extra={"event": "trace_cost_record_failed", "error": str(exc)},
                )

    logger.info(
        "span_complete",
        extra={
            "event": "span_complete",
            "operation": op_name,
            "latency_ms": latency_ms,
            "success": success,
            "error": error_msg,
        },
    )
