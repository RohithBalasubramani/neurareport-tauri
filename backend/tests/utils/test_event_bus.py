"""Comprehensive tests for backend.app.utils.event_bus.

Coverage layers:
  1. Unit tests — Event construction, EventBus subscribe/publish, NullEventBus
  2. Integration tests — middleware chain, logging/metrics middleware
  3. Property-based — random event names/payloads never crash
  4. Failure injection — handler exceptions, middleware exceptions
  5. Concurrency — async handler execution order
  6. Security / abuse — large payloads, many handlers, many events
  7. Usability — realistic event patterns from the codebase
"""
from __future__ import annotations

import asyncio
import logging
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.app.utils.event_bus import (
    Event,
    EventBus,
    NullEventBus,
    logging_middleware,
    metrics_middleware,
)


# ==========================================================================
# 1. UNIT TESTS — Event dataclass
# ==========================================================================

class TestEvent:
    def test_basic_construction(self):
        ev = Event(name="test_event")
        assert ev.name == "test_event"
        assert ev.payload == {}
        assert ev.correlation_id is None
        assert ev.timestamp > 0

    def test_with_payload(self):
        ev = Event(name="data", payload={"key": "value"})
        assert ev.payload["key"] == "value"

    def test_with_correlation_id(self):
        ev = Event(name="tracked", correlation_id="corr-123")
        assert ev.correlation_id == "corr-123"

    def test_timestamp_auto_set(self):
        before = time.time()
        ev = Event(name="timed")
        after = time.time()
        assert before <= ev.timestamp <= after

    def test_custom_timestamp(self):
        ev = Event(name="custom", timestamp=1000.0)
        assert ev.timestamp == 1000.0

    def test_payload_is_mutable(self):
        ev = Event(name="mut")
        ev.payload["added"] = True
        assert ev.payload["added"] is True


# ==========================================================================
# 2. UNIT TESTS — EventBus subscribe/publish
# ==========================================================================

class TestEventBusBasic:
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []
        bus.subscribe("greet", lambda ev: received.append(ev.name))
        await bus.publish(Event(name="greet"))
        assert received == ["greet"]

    @pytest.mark.asyncio
    async def test_multiple_handlers(self):
        bus = EventBus()
        results = []
        bus.subscribe("evt", lambda ev: results.append("a"))
        bus.subscribe("evt", lambda ev: results.append("b"))
        await bus.publish(Event(name="evt"))
        assert results == ["a", "b"]

    @pytest.mark.asyncio
    async def test_no_handler_no_error(self):
        bus = EventBus()
        await bus.publish(Event(name="nobody_listening"))

    @pytest.mark.asyncio
    async def test_only_matching_handlers_called(self):
        bus = EventBus()
        results = []
        bus.subscribe("one", lambda ev: results.append("one"))
        bus.subscribe("two", lambda ev: results.append("two"))
        await bus.publish(Event(name="one"))
        assert results == ["one"]

    @pytest.mark.asyncio
    async def test_async_handler(self):
        bus = EventBus()
        received = []

        async def async_handler(ev: Event):
            received.append(ev.name)

        bus.subscribe("async_evt", async_handler)
        await bus.publish(Event(name="async_evt"))
        assert received == ["async_evt"]

    @pytest.mark.asyncio
    async def test_mixed_sync_async_handlers(self):
        bus = EventBus()
        results = []

        bus.subscribe("mix", lambda ev: results.append("sync"))

        async def async_handler(ev: Event):
            results.append("async")

        bus.subscribe("mix", async_handler)
        await bus.publish(Event(name="mix"))
        assert results == ["sync", "async"]


class TestNullEventBus:
    @pytest.mark.asyncio
    async def test_publish_is_noop(self):
        bus = NullEventBus()
        # Should not raise
        await bus.publish(Event(name="ignored"))

    def test_subscribe_is_noop(self):
        bus = NullEventBus()
        bus.subscribe("event", lambda ev: None)
        assert bus._handlers == {}

    @pytest.mark.asyncio
    async def test_handler_never_called(self):
        bus = NullEventBus()
        handler = MagicMock()
        bus.subscribe("evt", handler)
        await bus.publish(Event(name="evt"))
        handler.assert_not_called()


# ==========================================================================
# 3. INTEGRATION TESTS — Middleware chain
# ==========================================================================

class TestMiddleware:
    @pytest.mark.asyncio
    async def test_single_middleware(self):
        order = []

        async def mw(event, call_next):
            order.append("mw_before")
            await call_next(event)
            order.append("mw_after")

        bus = EventBus(middlewares=[mw])
        bus.subscribe("evt", lambda ev: order.append("handler"))
        await bus.publish(Event(name="evt"))
        assert order == ["mw_before", "handler", "mw_after"]

    @pytest.mark.asyncio
    async def test_middleware_chain_order(self):
        order = []

        async def mw1(event, call_next):
            order.append("mw1_in")
            await call_next(event)
            order.append("mw1_out")

        async def mw2(event, call_next):
            order.append("mw2_in")
            await call_next(event)
            order.append("mw2_out")

        bus = EventBus(middlewares=[mw1, mw2])
        bus.subscribe("evt", lambda ev: order.append("handler"))
        await bus.publish(Event(name="evt"))
        assert order == ["mw1_in", "mw2_in", "handler", "mw2_out", "mw1_out"]

    @pytest.mark.asyncio
    async def test_middleware_can_modify_event(self):
        async def enricher(event, call_next):
            event.payload["enriched"] = True
            await call_next(event)

        bus = EventBus(middlewares=[enricher])
        captured = []
        bus.subscribe("evt", lambda ev: captured.append(ev.payload.get("enriched")))
        await bus.publish(Event(name="evt"))
        assert captured == [True]

    @pytest.mark.asyncio
    async def test_middleware_can_short_circuit(self):
        async def blocker(event, call_next):
            # Don't call call_next — block the event
            pass

        bus = EventBus(middlewares=[blocker])
        handler_called = []
        bus.subscribe("evt", lambda ev: handler_called.append(True))
        await bus.publish(Event(name="evt"))
        assert handler_called == []  # Handler never reached


class TestBuiltinMiddleware:
    @pytest.mark.asyncio
    async def test_logging_middleware(self, caplog):
        logger = logging.getLogger("test_event_bus")
        bus = EventBus(middlewares=[logging_middleware(logger)])
        bus.subscribe("test_log", lambda ev: None)

        with caplog.at_level(logging.INFO, logger="test_event_bus"):
            await bus.publish(Event(name="test_log", payload={"k": "v"}, correlation_id="c-1"))

        assert any("event_bus_publish" in rec.message for rec in caplog.records)

    @pytest.mark.asyncio
    async def test_metrics_middleware(self, caplog):
        logger = logging.getLogger("test_event_bus_metrics")
        bus = EventBus(middlewares=[metrics_middleware(logger)])
        bus.subscribe("test_metric", lambda ev: None)

        with caplog.at_level(logging.INFO, logger="test_event_bus_metrics"):
            await bus.publish(Event(name="test_metric"))

        assert any("event_bus_metric" in rec.message for rec in caplog.records)

    @pytest.mark.asyncio
    async def test_metrics_captures_elapsed_ms(self, caplog):
        logger = logging.getLogger("test_metrics_elapsed")

        async def slow_handler(ev):
            await asyncio.sleep(0.01)

        bus = EventBus(middlewares=[metrics_middleware(logger)])
        bus.subscribe("slow", slow_handler)

        with caplog.at_level(logging.INFO, logger="test_metrics_elapsed"):
            await bus.publish(Event(name="slow"))

        metric_record = [r for r in caplog.records if "event_bus_metric" in r.message]
        assert len(metric_record) == 1
        assert metric_record[0].elapsed_ms >= 0  # type: ignore[attr-defined]


# ==========================================================================
# 4. PROPERTY-BASED / FUZZ TESTS
# ==========================================================================

class TestPropertyBased:
    @given(
        name=st.text(min_size=1, max_size=100),
        payload=st.dictionaries(
            keys=st.text(min_size=1, max_size=30),
            values=st.one_of(st.integers(), st.text(max_size=50), st.booleans()),
            max_size=10,
        ),
    )
    @settings(max_examples=100)
    def test_event_construction_never_crashes(self, name, payload):
        ev = Event(name=name, payload=payload)
        assert ev.name == name
        assert ev.payload == payload


# ==========================================================================
# 5. FAILURE INJECTION TESTS
# ==========================================================================

class TestFailureInjection:
    @pytest.mark.asyncio
    async def test_handler_exception_propagates(self):
        """If a handler throws, the exception propagates to the publisher."""
        bus = EventBus()

        def bad_handler(ev):
            raise ValueError("Handler exploded")

        bus.subscribe("bad", bad_handler)
        with pytest.raises(ValueError, match="Handler exploded"):
            await bus.publish(Event(name="bad"))

    @pytest.mark.asyncio
    async def test_middleware_exception_propagates(self):
        async def bad_mw(event, call_next):
            raise RuntimeError("Middleware crash")

        bus = EventBus(middlewares=[bad_mw])
        bus.subscribe("evt", lambda ev: None)
        with pytest.raises(RuntimeError, match="Middleware crash"):
            await bus.publish(Event(name="evt"))

    @pytest.mark.asyncio
    async def test_first_handler_crash_stops_remaining(self):
        """Handler exceptions stop execution — later handlers don't run."""
        bus = EventBus()
        results = []
        bus.subscribe("evt", lambda ev: (_ for _ in ()).throw(ValueError("boom")))
        bus.subscribe("evt", lambda ev: results.append("second"))

        with pytest.raises(ValueError):
            await bus.publish(Event(name="evt"))
        assert results == []  # Second handler never ran


# ==========================================================================
# 6. CONCURRENCY / ASYNC TESTS
# ==========================================================================

class TestAsyncBehavior:
    @pytest.mark.asyncio
    async def test_publish_is_sequential(self):
        """Handlers execute in subscription order (not parallel)."""
        bus = EventBus()
        order = []

        async def handler_a(ev):
            order.append("a_start")
            await asyncio.sleep(0.01)
            order.append("a_end")

        async def handler_b(ev):
            order.append("b_start")
            await asyncio.sleep(0.01)
            order.append("b_end")

        bus.subscribe("seq", handler_a)
        bus.subscribe("seq", handler_b)
        await bus.publish(Event(name="seq"))
        assert order == ["a_start", "a_end", "b_start", "b_end"]

    @pytest.mark.asyncio
    async def test_multiple_publishes_independent(self):
        """Each publish gets its own handler invocations."""
        bus = EventBus()
        count = {"n": 0}
        bus.subscribe("inc", lambda ev: count.update(n=count["n"] + 1))
        await bus.publish(Event(name="inc"))
        await bus.publish(Event(name="inc"))
        await bus.publish(Event(name="inc"))
        assert count["n"] == 3


# ==========================================================================
# 7. SECURITY / ABUSE TESTS
# ==========================================================================

class TestAbuseResilience:
    @pytest.mark.asyncio
    async def test_large_payload(self):
        bus = EventBus()
        received = []
        bus.subscribe("big", lambda ev: received.append(len(ev.payload)))
        big_payload = {f"key_{i}": f"value_{i}" for i in range(1000)}
        await bus.publish(Event(name="big", payload=big_payload))
        assert received == [1000]

    @pytest.mark.asyncio
    async def test_many_handlers(self):
        bus = EventBus()
        count = {"n": 0}
        for _ in range(100):
            bus.subscribe("mass", lambda ev: count.update(n=count["n"] + 1))
        await bus.publish(Event(name="mass"))
        assert count["n"] == 100

    @pytest.mark.asyncio
    async def test_many_event_types(self):
        bus = EventBus()
        results = set()
        for i in range(50):
            name = f"type_{i}"
            bus.subscribe(name, lambda ev, n=name: results.add(n))
            await bus.publish(Event(name=name))
        assert len(results) == 50


# ==========================================================================
# 8. USABILITY — Realistic patterns
# ==========================================================================

class TestRealisticPatterns:
    @pytest.mark.asyncio
    async def test_report_generation_event_flow(self):
        """Simulate the real report generation event pattern."""
        bus = EventBus(middlewares=[
            logging_middleware(logging.getLogger("test")),
            metrics_middleware(logging.getLogger("test")),
        ])
        events_received = []

        bus.subscribe("report.started", lambda ev: events_received.append(("started", ev.payload)))
        bus.subscribe("report.completed", lambda ev: events_received.append(("completed", ev.payload)))
        bus.subscribe("report.failed", lambda ev: events_received.append(("failed", ev.payload)))

        await bus.publish(Event(name="report.started", payload={"job_id": "j1"}, correlation_id="corr-1"))
        await bus.publish(Event(name="report.completed", payload={"job_id": "j1", "path": "/out.pdf"}))

        assert len(events_received) == 2
        assert events_received[0][0] == "started"
        assert events_received[1][1]["path"] == "/out.pdf"

    @pytest.mark.asyncio
    async def test_null_bus_in_tests(self):
        """NullEventBus used in pipeline tests to suppress events."""
        bus = NullEventBus()
        # Subscribe and publish — nothing happens, no errors
        bus.subscribe("pipeline.step", lambda ev: None)
        await bus.publish(Event(name="pipeline.step", payload={"stage": "render"}))
