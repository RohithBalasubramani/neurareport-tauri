from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, List, Optional, Protocol, TypeVar

from .event_bus import Event, EventBus, NullEventBus
from .result import Result, err, ok, _maybe_await

Ctx = TypeVar("Ctx")
ErrType = TypeVar("ErrType")


class PipelineStepFn(Protocol[Ctx, ErrType]):
    def __call__(self, ctx: Ctx) -> Result[Ctx, ErrType] | Awaitable[Result[Ctx, ErrType]]: ...


GuardFn = Callable[[Ctx], bool]


@dataclass
class PipelineStep(Generic[Ctx, ErrType]):
    name: str
    fn: PipelineStepFn[Ctx, ErrType]
    guard: GuardFn[Ctx] = lambda ctx: True


class PipelineRunner(Generic[Ctx, ErrType]):
    def __init__(
        self,
        steps: List[PipelineStep[Ctx, ErrType]],
        *,
        bus: Optional[EventBus] = None,
        logger: Optional[logging.Logger] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.steps = steps
        self.bus = bus or NullEventBus()
        self.logger = logger or logging.getLogger("neura.pipeline")
        self.correlation_id = correlation_id

    async def run(self, ctx: Ctx) -> Result[Ctx, ErrType]:
        current = ok(ctx)
        for step in self.steps:
            if not step.guard(ctx):
                continue
            await self._emit(f"pipeline.{step.name}.start", {"ctx_type": type(ctx).__name__})
            try:
                current = await _maybe_await(step.fn(current.unwrap()))
            except Exception as exc:  # guard against unexpected failures
                self.logger.exception(
                    "pipeline_step_failed",
                    extra={
                        "event": "pipeline_step_failed",
                        "step": step.name,
                        "correlation_id": self.correlation_id,
                    },
                )
                return err(exc)  # type: ignore[arg-type]

            if current.is_err:
                await self._emit(
                    f"pipeline.{step.name}.error",
                    {
                        "ctx_type": type(ctx).__name__,
                        "error": str(current.unwrap_err()),
                    },
                )
                return current

            ctx = current.unwrap()
            await self._emit(f"pipeline.{step.name}.ok", {"ctx_type": type(ctx).__name__})

        await self._emit("pipeline.complete", {"ctx_type": type(ctx).__name__})
        return current

    async def _emit(self, name: str, payload: dict) -> None:
        await self.bus.publish(Event(name=name, payload=payload, correlation_id=self.correlation_id))
