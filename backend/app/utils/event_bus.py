from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol

from .result import _maybe_await


@dataclass
class Event:
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    timestamp: float = field(default_factory=lambda: time.time())


class EventHandler(Protocol):
    def __call__(self, event: Event) -> Awaitable[None] | None: ...


class EventMiddleware(Protocol):
    def __call__(self, event: Event, call_next: Callable[[Event], Awaitable[None]]) -> Awaitable[None]: ...


class EventBus:
    def __init__(self, *, middlewares: Optional[List[EventMiddleware]] = None) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._middlewares = list(middlewares or [])

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event_name, []).append(handler)

    async def publish(self, event: Event) -> None:
        async def _dispatch(ev: Event) -> None:
            handlers = list(self._handlers.get(ev.name, []))
            for handler in handlers:
                await _maybe_await(handler(ev))

        async def _run_middleware(index: int, ev: Event) -> None:
            if index >= len(self._middlewares):
                await _dispatch(ev)
                return
            middleware = self._middlewares[index]
            await middleware(ev, lambda e=ev: _run_middleware(index + 1, e))

        await _run_middleware(0, event)


class NullEventBus(EventBus):
    async def publish(self, event: Event) -> None:  # type: ignore[override]
        return None

    def subscribe(self, event_name: str, handler: EventHandler) -> None:  # type: ignore[override]
        return None


def logging_middleware(logger: logging.Logger) -> EventMiddleware:
    async def _middleware(event: Event, call_next: Callable[[Event], Awaitable[None]]) -> None:
        logger.info(
            "event_bus_publish",
            extra={
                "event": event.name,
                "payload_keys": list(event.payload.keys()),
                "correlation_id": event.correlation_id,
                "ts": event.timestamp,
            },
        )
        await call_next(event)

    return _middleware


def metrics_middleware(logger: logging.Logger) -> EventMiddleware:
    async def _middleware(event: Event, call_next: Callable[[Event], Awaitable[None]]) -> None:
        started = time.time()
        try:
            await call_next(event)
        finally:
            elapsed_ms = int((time.time() - started) * 1000)
            logger.info(
                "event_bus_metric",
                extra={
                    "event": event.name,
                    "elapsed_ms": elapsed_ms,
                    "correlation_id": event.correlation_id,
                },
            )

    return _middleware
