"""Event bus for decoupled communication between components.

This is an improved version of the existing event_bus.py with:
- Type-safe events
- Async-first design
- Middleware support
- Event persistence capability
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol

logger = logging.getLogger("neura.events")


@dataclass(frozen=True)
class Event:
    """Immutable event with metadata."""

    name: str
    payload: Dict[str, Any]
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = field(default="backend")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "name": self.name,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


EventHandler = Callable[[Event], Awaitable[None]]
EventMiddleware = Callable[[Event, Callable[[Event], Awaitable[None]]], Awaitable[None]]


class EventPersistence(Protocol):
    """Protocol for event persistence backends."""

    async def persist(self, event: Event) -> None:
        """Persist an event for replay or audit."""
        ...

    async def get_events(
        self,
        *,
        name: Optional[str] = None,
        correlation_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Event]:
        """Retrieve persisted events."""
        ...


class EventBus:
    """Async event bus with middleware and persistence support."""

    def __init__(
        self,
        *,
        middlewares: Optional[List[EventMiddleware]] = None,
        persistence: Optional[EventPersistence] = None,
    ) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._middlewares = middlewares or []
        self._persistence = persistence
        self._wildcard_handlers: List[EventHandler] = []

    def subscribe(self, event_name: str, handler: EventHandler) -> Callable[[], None]:
        """Subscribe a handler to an event. Returns unsubscribe function."""
        if event_name == "*":
            self._wildcard_handlers.append(handler)
            return lambda: self._wildcard_handlers.remove(handler)

        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
        return lambda: self._handlers[event_name].remove(handler)

    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        async def dispatch(evt: Event) -> None:
            await self._dispatch(evt)

        # Apply middlewares in reverse order (outermost first)
        handler = dispatch
        for middleware in reversed(self._middlewares):
            prev_handler = handler

            async def make_handler(m: EventMiddleware, h: Callable) -> Callable:
                async def wrapped(e: Event) -> None:
                    await m(e, h)
                return wrapped

            handler = await make_handler(middleware, prev_handler)

        await handler(event)

        # Persist if configured
        if self._persistence:
            try:
                await self._persistence.persist(event)
            except Exception:
                logger.exception("event_persist_failed", extra={"event": event.name})

    async def _dispatch(self, event: Event) -> None:
        """Dispatch event to registered handlers."""
        handlers = list(self._handlers.get(event.name, []))
        handlers.extend(self._wildcard_handlers)

        if not handlers:
            return

        # Run all handlers concurrently
        results = await asyncio.gather(
            *[self._safe_call(handler, event) for handler in handlers],
            return_exceptions=True,
        )

        for result in results:
            if isinstance(result, Exception):
                logger.exception(
                    "event_handler_failed",
                    extra={"event": event.name, "error": str(result)},
                )

    async def _safe_call(self, handler: EventHandler, event: Event) -> None:
        """Safely call a handler, catching exceptions."""
        try:
            await handler(event)
        except Exception as e:
            logger.exception(
                "event_handler_error",
                extra={"event": event.name, "handler": handler.__name__},
            )
            raise


def logging_middleware(log: logging.Logger) -> EventMiddleware:
    """Middleware that logs all events."""

    async def middleware(event: Event, next_handler: Callable[[Event], Awaitable[None]]) -> None:
        start = time.perf_counter()
        log.info(
            "event_published",
            extra={
                "event": event.name,
                "event_id": event.event_id,
                "correlation_id": event.correlation_id,
            },
        )
        try:
            await next_handler(event)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            log.debug(
                "event_handled",
                extra={
                    "event": event.name,
                    "event_id": event.event_id,
                    "elapsed_ms": elapsed,
                },
            )

    return middleware


def metrics_middleware(log: logging.Logger) -> EventMiddleware:
    """Middleware that tracks event metrics."""

    _counts: Dict[str, int] = {}

    async def middleware(event: Event, next_handler: Callable[[Event], Awaitable[None]]) -> None:
        _counts[event.name] = _counts.get(event.name, 0) + 1
        await next_handler(event)

    return middleware


# Global event bus instance
_global_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus."""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus(
            middlewares=[
                logging_middleware(logger),
                metrics_middleware(logger),
            ]
        )
    return _global_bus


def publish_sync(event: Event) -> None:
    """Publish an event synchronously (for use in sync code)."""
    bus = get_event_bus()
    try:
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(bus.publish(event), loop)
    except RuntimeError:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(asyncio.run, bus.publish(event)).result()
