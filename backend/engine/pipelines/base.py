"""Base pipeline framework.

Inspired by Dagster and Prefect, but simplified for our use case.
Key concepts:
- Pipeline: A sequence of steps
- Step: An atomic unit of work
- Context: Shared state between steps
- Result: Success or failure with data
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
)

from backend.engine.core.errors import PipelineError
from backend.engine.core.events import Event, get_event_bus, publish_sync
from backend.engine.core.result import Result, Ok, Err

logger = logging.getLogger("neura.pipelines")

T = TypeVar("T")
C = TypeVar("C", bound="PipelineContext")


class StepStatus(str, Enum):
    """Status of a pipeline step."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult(Generic[T]):
    """Result of executing a step."""

    status: StepStatus
    data: Optional[T] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    skipped_reason: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.status == StepStatus.SUCCEEDED

    @classmethod
    def ok(cls, data: T, duration_ms: float = 0.0) -> StepResult[T]:
        return cls(status=StepStatus.SUCCEEDED, data=data, duration_ms=duration_ms)

    @classmethod
    def fail(cls, error: str, duration_ms: float = 0.0) -> StepResult[T]:
        return cls(status=StepStatus.FAILED, error=error, duration_ms=duration_ms)

    @classmethod
    def skip(cls, reason: str) -> StepResult[T]:
        return cls(status=StepStatus.SKIPPED, skipped_reason=reason)


@dataclass
class PipelineContext:
    """Context shared between pipeline steps.

    Contains:
    - Input parameters
    - Intermediate results from previous steps
    - Shared resources (adapters, config)
    - Cancellation flag
    """

    correlation_id: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cancelled: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def set(self, key: str, value: Any) -> None:
        """Set a result value."""
        self.results[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a result value."""
        return self.results.get(key, default)

    def cancel(self) -> None:
        """Mark the context as cancelled."""
        self.cancelled = True

    def is_cancelled(self) -> bool:
        """Check if cancelled."""
        return self.cancelled

    def get_resource(self, name: str) -> Any:
        """Get a shared resource."""
        return self.resources.get(name)


StepFunction = Union[
    Callable[[PipelineContext], Any],
    Callable[[PipelineContext], Awaitable[Any]],
]
GuardFunction = Callable[[PipelineContext], bool]


@dataclass
class Step:
    """A single step in a pipeline.

    Steps have:
    - Name: Unique identifier
    - Function: The actual work to do
    - Guard: Optional condition to skip the step
    - Retry policy: How to handle failures
    """

    name: str
    fn: StepFunction
    label: Optional[str] = None
    guard: Optional[GuardFunction] = None
    retries: int = 0
    retry_delay_seconds: float = 1.0
    timeout_seconds: Optional[float] = None
    on_error: Optional[Callable[[Exception, PipelineContext], None]] = None

    @property
    def display_name(self) -> str:
        return self.label or self.name

    def should_run(self, ctx: PipelineContext) -> bool:
        """Check if this step should run."""
        if self.guard is None:
            return True
        try:
            return self.guard(ctx)
        except Exception:
            return True

    async def execute(self, ctx: PipelineContext) -> StepResult:
        """Execute this step with retries and timeout."""
        if ctx.is_cancelled():
            return StepResult.skip("Pipeline cancelled")

        if not self.should_run(ctx):
            return StepResult.skip(f"Guard returned false for {self.name}")

        last_error: Optional[Exception] = None
        attempts = self.retries + 1

        for attempt in range(attempts):
            if ctx.is_cancelled():
                return StepResult.skip("Pipeline cancelled")

            start = time.perf_counter()
            try:
                # Execute with optional timeout
                if asyncio.iscoroutinefunction(self.fn):
                    if self.timeout_seconds:
                        result = await asyncio.wait_for(
                            self.fn(ctx),
                            timeout=self.timeout_seconds,
                        )
                    else:
                        result = await self.fn(ctx)
                else:
                    if self.timeout_seconds:
                        result = await asyncio.wait_for(
                            asyncio.to_thread(self.fn, ctx),
                            timeout=self.timeout_seconds,
                        )
                    else:
                        result = self.fn(ctx)

                duration = (time.perf_counter() - start) * 1000
                return StepResult.ok(result, duration_ms=duration)

            except asyncio.TimeoutError:
                duration = (time.perf_counter() - start) * 1000
                return StepResult.fail(
                    f"Step {self.name} timed out after {self.timeout_seconds}s",
                    duration_ms=duration,
                )
            except Exception as e:
                last_error = e
                duration = (time.perf_counter() - start) * 1000

                if self.on_error:
                    try:
                        self.on_error(e, ctx)
                    except Exception:
                        logger.debug("callback_failed", exc_info=True)

                if attempt < attempts - 1:
                    logger.warning(
                        "step_retry",
                        extra={
                            "step": self.name,
                            "attempt": attempt + 1,
                            "max_attempts": attempts,
                            "error": str(e),
                        },
                    )
                    await asyncio.sleep(self.retry_delay_seconds)
                else:
                    return StepResult.fail(str(e), duration_ms=duration)

        return StepResult.fail(str(last_error) if last_error else "Unknown error")


@dataclass
class PipelineResult:
    """Result of executing a pipeline."""

    success: bool
    steps: Dict[str, StepResult]
    context: PipelineContext
    error: Optional[str] = None
    duration_ms: float = 0.0

    def get_step_result(self, name: str) -> Optional[StepResult]:
        return self.steps.get(name)


class Pipeline:
    """A sequence of steps that process data.

    Pipelines are:
    - Declarative: Define steps upfront
    - Observable: Emit events for each step
    - Cancellable: Can be stopped mid-execution
    - Composable: Can include sub-pipelines
    """

    def __init__(
        self,
        name: str,
        steps: List[Step],
        *,
        on_error: Optional[Callable[[str, Exception, PipelineContext], None]] = None,
        on_success: Optional[Callable[[PipelineContext], None]] = None,
        on_step_complete: Optional[Callable[[str, StepResult, PipelineContext], None]] = None,
    ) -> None:
        self.name = name
        self.steps = steps
        self._on_error = on_error
        self._on_success = on_success
        self._on_step_complete = on_step_complete

    async def execute(self, ctx: PipelineContext) -> PipelineResult:
        """Execute all steps in order."""
        ctx.started_at = datetime.now(timezone.utc)
        start = time.perf_counter()
        step_results: Dict[str, StepResult] = {}

        # Emit pipeline started event
        publish_sync(
            Event(
                name="pipeline.started",
                payload={"pipeline": self.name, "steps": [s.name for s in self.steps]},
                correlation_id=ctx.correlation_id,
            )
        )

        try:
            for step in self.steps:
                if ctx.is_cancelled():
                    step_results[step.name] = StepResult.skip("Pipeline cancelled")
                    continue

                logger.info(
                    "step_started",
                    extra={
                        "pipeline": self.name,
                        "step": step.name,
                        "correlation_id": ctx.correlation_id,
                    },
                )

                # Emit step started event
                publish_sync(
                    Event(
                        name="pipeline.step_started",
                        payload={"pipeline": self.name, "step": step.name},
                        correlation_id=ctx.correlation_id,
                    )
                )

                result = await step.execute(ctx)
                step_results[step.name] = result

                # Call step complete callback
                if self._on_step_complete:
                    try:
                        self._on_step_complete(step.name, result, ctx)
                    except Exception:
                        logger.debug("callback_failed", exc_info=True)

                logger.info(
                    "step_completed",
                    extra={
                        "pipeline": self.name,
                        "step": step.name,
                        "status": result.status.value,
                        "duration_ms": result.duration_ms,
                        "correlation_id": ctx.correlation_id,
                    },
                )

                # Emit step completed event
                publish_sync(
                    Event(
                        name="pipeline.step_completed",
                        payload={
                            "pipeline": self.name,
                            "step": step.name,
                            "status": result.status.value,
                        },
                        correlation_id=ctx.correlation_id,
                    )
                )

                # Stop on failure (unless skipped)
                if result.status == StepStatus.FAILED:
                    if self._on_error:
                        try:
                            self._on_error(
                                step.name,
                                PipelineError(
                                    message=result.error or "Step failed",
                                    step=step.name,
                                ),
                                ctx,
                            )
                        except Exception:
                            logger.debug("callback_failed", exc_info=True)

                    duration = (time.perf_counter() - start) * 1000
                    ctx.completed_at = datetime.now(timezone.utc)

                    publish_sync(
                        Event(
                            name="pipeline.failed",
                            payload={
                                "pipeline": self.name,
                                "failed_step": step.name,
                                "error": result.error,
                            },
                            correlation_id=ctx.correlation_id,
                        )
                    )

                    return PipelineResult(
                        success=False,
                        steps=step_results,
                        context=ctx,
                        error=f"Step {step.name} failed: {result.error}",
                        duration_ms=duration,
                    )

            # All steps completed
            duration = (time.perf_counter() - start) * 1000
            ctx.completed_at = datetime.now(timezone.utc)

            if self._on_success:
                try:
                    self._on_success(ctx)
                except Exception:
                    logger.debug("callback_failed", exc_info=True)

            publish_sync(
                Event(
                    name="pipeline.completed",
                    payload={"pipeline": self.name},
                    correlation_id=ctx.correlation_id,
                )
            )

            return PipelineResult(
                success=True,
                steps=step_results,
                context=ctx,
                duration_ms=duration,
            )

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            ctx.completed_at = datetime.now(timezone.utc)

            logger.exception(
                "pipeline_error",
                extra={
                    "pipeline": self.name,
                    "correlation_id": ctx.correlation_id,
                },
            )

            publish_sync(
                Event(
                    name="pipeline.error",
                    payload={"pipeline": self.name, "error": str(e)},
                    correlation_id=ctx.correlation_id,
                )
            )

            return PipelineResult(
                success=False,
                steps=step_results,
                context=ctx,
                error=str(e),
                duration_ms=duration,
            )

    def execute_sync(self, ctx: PipelineContext) -> PipelineResult:
        """Execute pipeline synchronously."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.execute(ctx)).result()
        return asyncio.run(self.execute(ctx))


def step(
    name: str,
    *,
    label: Optional[str] = None,
    guard: Optional[GuardFunction] = None,
    retries: int = 0,
    timeout: Optional[float] = None,
) -> Callable[[StepFunction], Step]:
    """Decorator to create a step from a function."""

    def decorator(fn: StepFunction) -> Step:
        return Step(
            name=name,
            fn=fn,
            label=label or name,
            guard=guard,
            retries=retries,
            timeout_seconds=timeout,
        )

    return decorator
