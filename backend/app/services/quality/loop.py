"""Iterative quality loop with configurable break conditions."""
from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .evaluator import QualityEvaluator

logger = logging.getLogger("neura.quality.loop")


# ---------------------------------------------------------------------------
# Break-condition ABC and concrete implementations
# ---------------------------------------------------------------------------


class LoopBreaker(ABC):
    """Abstract base class for loop termination conditions."""

    @abstractmethod
    def should_break(
        self, iteration: int, score: float, history: List[float]
    ) -> bool:
        """Return ``True`` when the loop should stop."""

    @abstractmethod
    def reason(self) -> str:
        """Human-readable explanation of why the breaker fired."""


class MaxIterationBreaker(LoopBreaker):
    """Breaks when the iteration count reaches *max_iterations*."""

    def __init__(self, max_iterations: int = 3) -> None:
        self.max_iterations = max_iterations

    def should_break(
        self, iteration: int, score: float, history: List[float]
    ) -> bool:
        return iteration >= self.max_iterations

    def reason(self) -> str:
        return f"max_iterations_reached ({self.max_iterations})"


class QualityBreaker(LoopBreaker):
    """Breaks when the score meets or exceeds *threshold*."""

    def __init__(self, threshold: float = 0.85) -> None:
        self.threshold = threshold

    def should_break(
        self, iteration: int, score: float, history: List[float]
    ) -> bool:
        return score >= self.threshold

    def reason(self) -> str:
        return f"quality_threshold_met ({self.threshold})"


class TimeoutBreaker(LoopBreaker):
    """Breaks when elapsed wall-clock time exceeds *max_seconds*."""

    def __init__(self, max_seconds: float = 120) -> None:
        self.max_seconds = max_seconds
        self._start: Optional[float] = None

    def start(self) -> None:
        """Record the loop start time."""
        self._start = time.monotonic()

    def should_break(
        self, iteration: int, score: float, history: List[float]
    ) -> bool:
        if self._start is None:
            self._start = time.monotonic()
        return (time.monotonic() - self._start) > self.max_seconds

    def reason(self) -> str:
        return f"timeout_exceeded ({self.max_seconds}s)"


class PlateauBreaker(LoopBreaker):
    """Breaks when the last *patience* improvements are all below *epsilon*."""

    def __init__(self, epsilon: float = 0.02, patience: int = 2) -> None:
        self.epsilon = epsilon
        self.patience = patience

    def should_break(
        self, iteration: int, score: float, history: List[float]
    ) -> bool:
        if len(history) < self.patience + 1:
            return False
        recent = history[-(self.patience + 1) :]
        improvements = [
            recent[i + 1] - recent[i] for i in range(len(recent) - 1)
        ]
        return all(imp < self.epsilon for imp in improvements)

    def reason(self) -> str:
        return (
            f"score_plateau (epsilon={self.epsilon}, patience={self.patience})"
        )


# ---------------------------------------------------------------------------
# Loop result
# ---------------------------------------------------------------------------


@dataclass
class LoopResult:
    """Outcome of a :class:`QualityLoop` execution."""

    output: Any
    final_score: float
    iterations: int
    score_history: List[float] = field(default_factory=list)
    break_reason: str = ""
    total_time: float = 0.0


# ---------------------------------------------------------------------------
# Quality loop
# ---------------------------------------------------------------------------


class QualityLoop:
    """Run a callable iteratively until a break condition is met.

    Each iteration invokes ``fn(prev_output, iteration)`` and evaluates the
    result with a :class:`QualityEvaluator`.  The loop terminates when any
    configured :class:`LoopBreaker` fires.
    """

    def __init__(
        self,
        evaluator: Optional[QualityEvaluator] = None,
        breakers: Optional[List[LoopBreaker]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.evaluator = evaluator or QualityEvaluator(use_llm=False)
        self.breakers: List[LoopBreaker] = breakers or [
            MaxIterationBreaker(3),
            QualityBreaker(0.85),
            TimeoutBreaker(120),
        ]
        self.context = context or {}

    # ------------------------------------------------------------------
    # Synchronous execution
    # ------------------------------------------------------------------

    def run(
        self,
        fn: Callable[..., Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> LoopResult:
        """Execute the quality loop synchronously.

        Parameters
        ----------
        fn:
            A callable with signature ``fn(prev_output, iteration)``.
        context:
            Optional evaluation context merged with the instance context.
        """
        merged_ctx = {**self.context, **(context or {})}
        self._init_timeout_breakers()
        t_start = time.monotonic()

        score_history: List[float] = []
        output: Any = None
        break_reason = "completed"
        iteration = 0

        while True:
            output = fn(output, iteration)
            output_str = str(output) if not isinstance(output, str) else output
            quality = self.evaluator.evaluate(output_str, merged_ctx)
            score = quality.overall
            score_history.append(score)

            logger.info(
                "loop_iteration",
                extra={
                    "event": "loop_iteration",
                    "iteration": iteration,
                    "score": score,
                    "flags": quality.heuristic_flags,
                },
            )

            iteration += 1

            # Check breakers
            for breaker in self.breakers:
                if breaker.should_break(iteration, score, score_history):
                    break_reason = breaker.reason()
                    logger.info(
                        "loop_break",
                        extra={
                            "event": "loop_break",
                            "iteration": iteration,
                            "reason": break_reason,
                            "final_score": score,
                        },
                    )
                    return LoopResult(
                        output=output,
                        final_score=score,
                        iterations=iteration,
                        score_history=score_history,
                        break_reason=break_reason,
                        total_time=time.monotonic() - t_start,
                    )

        # Unreachable, but satisfies type checkers
        return LoopResult(  # pragma: no cover
            output=output,
            final_score=score_history[-1] if score_history else 0.0,
            iterations=iteration,
            score_history=score_history,
            break_reason=break_reason,
            total_time=time.monotonic() - t_start,
        )

    # ------------------------------------------------------------------
    # Async execution
    # ------------------------------------------------------------------

    async def run_async(
        self,
        fn: Callable[..., Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> LoopResult:
        """Execute the quality loop asynchronously.

        Parameters
        ----------
        fn:
            An async callable with signature ``await fn(prev_output, iteration)``.
        context:
            Optional evaluation context merged with the instance context.
        """
        merged_ctx = {**self.context, **(context or {})}
        self._init_timeout_breakers()
        t_start = time.monotonic()

        score_history: List[float] = []
        output: Any = None
        break_reason = "completed"
        iteration = 0

        while True:
            output = await fn(output, iteration)
            output_str = str(output) if not isinstance(output, str) else output
            quality = self.evaluator.evaluate(output_str, merged_ctx)
            score = quality.overall
            score_history.append(score)

            logger.info(
                "loop_iteration_async",
                extra={
                    "event": "loop_iteration_async",
                    "iteration": iteration,
                    "score": score,
                    "flags": quality.heuristic_flags,
                },
            )

            iteration += 1

            for breaker in self.breakers:
                if breaker.should_break(iteration, score, score_history):
                    break_reason = breaker.reason()
                    logger.info(
                        "loop_break_async",
                        extra={
                            "event": "loop_break_async",
                            "iteration": iteration,
                            "reason": break_reason,
                            "final_score": score,
                        },
                    )
                    return LoopResult(
                        output=output,
                        final_score=score,
                        iterations=iteration,
                        score_history=score_history,
                        break_reason=break_reason,
                        total_time=time.monotonic() - t_start,
                    )

        return LoopResult(  # pragma: no cover
            output=output,
            final_score=score_history[-1] if score_history else 0.0,
            iterations=iteration,
            score_history=score_history,
            break_reason=break_reason,
            total_time=time.monotonic() - t_start,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_timeout_breakers(self) -> None:
        """Initialise start time on any :class:`TimeoutBreaker` instances."""
        for breaker in self.breakers:
            if isinstance(breaker, TimeoutBreaker):
                breaker.start()
