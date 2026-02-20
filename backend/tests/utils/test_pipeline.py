"""Comprehensive tests for backend.app.utils.pipeline.

Coverage layers:
  1. Unit tests        -- PipelineStep construction, PipelineRunner construction defaults
  2. Integration tests -- Full pipeline runs, step ordering, event emission, guards, err short-circuit
  3. Property-based    -- Random step counts that all succeed, pipeline.complete always emitted
  4. Failure injection -- Step raises exception, step returns err Result
  5. Concurrency       -- Multiple pipelines via asyncio.gather, no cross-talk
  6. Security / abuse  -- Long step names, special characters, huge context objects
  7. Usability         -- Realistic validate -> transform -> persist pipeline
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import List
from unittest.mock import MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.app.utils.event_bus import Event, EventBus, NullEventBus
from backend.app.utils.pipeline import PipelineRunner, PipelineStep
from backend.app.utils.result import Result, err, ok


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class CollectingEventBus(EventBus):
    """An EventBus that records every published event for assertions."""

    def __init__(self) -> None:
        super().__init__()
        self.events: List[Event] = []

    async def publish(self, event: Event) -> None:
        self.events.append(event)


@dataclass
class SimpleCtx:
    """Minimal mutable context used across most tests."""
    value: int = 0
    trace: List[str] = field(default_factory=list)


def _ok_step(name: str):
    """Create a PipelineStep that appends its name to ctx.trace and returns ok."""
    def fn(ctx: SimpleCtx) -> Result[SimpleCtx, str]:
        ctx.trace.append(name)
        return ok(ctx)
    return PipelineStep(name=name, fn=fn)


def _async_ok_step(name: str):
    """Create a PipelineStep whose fn is an async coroutine."""
    async def fn(ctx: SimpleCtx) -> Result[SimpleCtx, str]:
        ctx.trace.append(name)
        return ok(ctx)
    return PipelineStep(name=name, fn=fn)


def _err_step(name: str, error_msg: str = "fail"):
    """Create a PipelineStep that returns err()."""
    def fn(ctx: SimpleCtx) -> Result[SimpleCtx, str]:
        ctx.trace.append(name)
        return err(error_msg)
    return PipelineStep(name=name, fn=fn)


def _raise_step(name: str, exc: Exception | None = None):
    """Create a PipelineStep that raises an exception."""
    def fn(ctx: SimpleCtx) -> Result[SimpleCtx, str]:
        raise exc or RuntimeError(f"{name} exploded")
    return PipelineStep(name=name, fn=fn)


# ==========================================================================
# 1. UNIT TESTS -- PipelineStep & PipelineRunner construction
# ==========================================================================

class TestPipelineStepConstruction:
    def test_basic_construction(self):
        step = PipelineStep(name="step1", fn=lambda ctx: ok(ctx))
        assert step.name == "step1"
        assert step.fn is not None

    def test_default_guard_returns_true(self):
        step = PipelineStep(name="always", fn=lambda ctx: ok(ctx))
        assert step.guard("anything") is True
        assert step.guard(None) is True
        assert step.guard(42) is True

    def test_custom_guard(self):
        guard = lambda ctx: ctx > 5
        step = PipelineStep(name="guarded", fn=lambda ctx: ok(ctx), guard=guard)
        assert step.guard(10) is True
        assert step.guard(3) is False

    def test_name_is_preserved(self):
        step = PipelineStep(name="my-custom-name", fn=lambda ctx: ok(ctx))
        assert step.name == "my-custom-name"


class TestPipelineRunnerConstruction:
    def test_defaults(self):
        runner = PipelineRunner(steps=[])
        assert isinstance(runner.bus, NullEventBus)
        assert runner.logger.name == "neura.pipeline"
        assert runner.correlation_id is None
        assert runner.steps == []

    def test_custom_bus(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[], bus=bus)
        assert runner.bus is bus

    def test_custom_logger(self):
        logger = logging.getLogger("custom.pipeline")
        runner = PipelineRunner(steps=[], logger=logger)
        assert runner.logger is logger

    def test_custom_correlation_id(self):
        runner = PipelineRunner(steps=[], correlation_id="corr-abc")
        assert runner.correlation_id == "corr-abc"

    def test_steps_stored(self):
        steps = [_ok_step("a"), _ok_step("b")]
        runner = PipelineRunner(steps=steps)
        assert runner.steps is steps
        assert len(runner.steps) == 2


# ==========================================================================
# 2. INTEGRATION TESTS -- Full pipeline run
# ==========================================================================

class TestPipelineExecution:
    @pytest.mark.asyncio
    async def test_single_step_success(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[_ok_step("only")], bus=bus)
        ctx = SimpleCtx(value=1)
        result = await runner.run(ctx)

        assert result.is_ok
        assert result.unwrap().trace == ["only"]

    @pytest.mark.asyncio
    async def test_multiple_steps_execution_order(self):
        steps = [_ok_step("first"), _ok_step("second"), _ok_step("third")]
        runner = PipelineRunner(steps=steps)
        ctx = SimpleCtx()
        result = await runner.run(ctx)

        assert result.is_ok
        assert result.unwrap().trace == ["first", "second", "third"]

    @pytest.mark.asyncio
    async def test_async_step_functions(self):
        steps = [_async_ok_step("async_a"), _async_ok_step("async_b")]
        runner = PipelineRunner(steps=steps)
        ctx = SimpleCtx()
        result = await runner.run(ctx)

        assert result.is_ok
        assert result.unwrap().trace == ["async_a", "async_b"]

    @pytest.mark.asyncio
    async def test_mixed_sync_async_steps(self):
        steps = [_ok_step("sync_a"), _async_ok_step("async_b"), _ok_step("sync_c")]
        runner = PipelineRunner(steps=steps)
        ctx = SimpleCtx()
        result = await runner.run(ctx)

        assert result.is_ok
        assert result.unwrap().trace == ["sync_a", "async_b", "sync_c"]

    @pytest.mark.asyncio
    async def test_events_emitted_in_order(self):
        bus = CollectingEventBus()
        steps = [_ok_step("alpha"), _ok_step("beta")]
        runner = PipelineRunner(steps=steps, bus=bus)
        ctx = SimpleCtx()
        await runner.run(ctx)

        event_names = [e.name for e in bus.events]
        assert event_names == [
            "pipeline.alpha.start",
            "pipeline.alpha.ok",
            "pipeline.beta.start",
            "pipeline.beta.ok",
            "pipeline.complete",
        ]

    @pytest.mark.asyncio
    async def test_event_payloads_contain_ctx_type(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[_ok_step("s")], bus=bus)
        await runner.run(SimpleCtx())

        for ev in bus.events:
            assert ev.payload["ctx_type"] == "SimpleCtx"

    @pytest.mark.asyncio
    async def test_guard_skips_step(self):
        bus = CollectingEventBus()
        skip_guard = lambda ctx: False
        skipped = PipelineStep(name="skipped", fn=lambda ctx: ok(ctx), guard=skip_guard)
        steps = [_ok_step("before"), skipped, _ok_step("after")]
        runner = PipelineRunner(steps=steps, bus=bus)
        ctx = SimpleCtx()
        result = await runner.run(ctx)

        assert result.is_ok
        assert result.unwrap().trace == ["before", "after"]
        event_names = [e.name for e in bus.events]
        assert "pipeline.skipped.start" not in event_names
        assert "pipeline.skipped.ok" not in event_names

    @pytest.mark.asyncio
    async def test_guard_based_on_context(self):
        """Guard sees the *original* ctx passed to run()."""
        guard = lambda ctx: ctx.value > 5
        conditional = PipelineStep(
            name="conditional",
            fn=lambda ctx: ok(SimpleCtx(value=ctx.value, trace=ctx.trace + ["conditional"])),
            guard=guard,
        )

        # value = 10 -> guard passes
        runner = PipelineRunner(steps=[conditional])
        result = await runner.run(SimpleCtx(value=10))
        assert result.is_ok
        assert "conditional" in result.unwrap().trace

        # value = 2 -> guard skips
        runner2 = PipelineRunner(steps=[conditional])
        result2 = await runner2.run(SimpleCtx(value=2))
        assert result2.is_ok
        assert result2.unwrap().trace == []

    @pytest.mark.asyncio
    async def test_err_stops_pipeline_early(self):
        bus = CollectingEventBus()
        steps = [_ok_step("one"), _err_step("two", "bad"), _ok_step("three")]
        runner = PipelineRunner(steps=steps, bus=bus)
        ctx = SimpleCtx()
        result = await runner.run(ctx)

        assert result.is_err
        assert result.unwrap_err() == "bad"
        # "three" was never executed
        event_names = [e.name for e in bus.events]
        assert "pipeline.three.start" not in event_names
        # Error event was emitted for step "two"
        assert "pipeline.two.error" in event_names
        # pipeline.complete is NOT emitted on error
        assert "pipeline.complete" not in event_names

    @pytest.mark.asyncio
    async def test_err_event_payload_contains_error_string(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[_err_step("bad_step", "some_error")], bus=bus)
        await runner.run(SimpleCtx())

        error_events = [e for e in bus.events if e.name.endswith(".error")]
        assert len(error_events) == 1
        assert error_events[0].payload["error"] == "some_error"

    @pytest.mark.asyncio
    async def test_correlation_id_propagated_to_events(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(
            steps=[_ok_step("s")], bus=bus, correlation_id="trace-999"
        )
        await runner.run(SimpleCtx())

        for ev in bus.events:
            assert ev.correlation_id == "trace-999"

    @pytest.mark.asyncio
    async def test_empty_pipeline(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[], bus=bus)
        ctx = SimpleCtx(value=42)
        result = await runner.run(ctx)

        assert result.is_ok
        assert result.unwrap().value == 42
        event_names = [e.name for e in bus.events]
        assert event_names == ["pipeline.complete"]


# ==========================================================================
# 3. PROPERTY-BASED TESTS
# ==========================================================================

class TestPropertyBased:
    @given(step_count=st.integers(min_value=1, max_value=10))
    @settings(max_examples=30)
    @pytest.mark.asyncio
    async def test_all_succeeding_steps_emit_complete(self, step_count: int):
        bus = CollectingEventBus()
        steps = [_ok_step(f"step_{i}") for i in range(step_count)]
        runner = PipelineRunner(steps=steps, bus=bus)
        result = await runner.run(SimpleCtx())

        assert result.is_ok
        event_names = [e.name for e in bus.events]
        assert event_names[-1] == "pipeline.complete"
        # Each step should have start + ok = 2 events, plus 1 complete
        assert len(bus.events) == step_count * 2 + 1

    @given(step_count=st.integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_all_steps_appear_in_trace(self, step_count: int):
        steps = [_ok_step(f"s{i}") for i in range(step_count)]
        runner = PipelineRunner(steps=steps)
        result = await runner.run(SimpleCtx())

        assert result.is_ok
        assert result.unwrap().trace == [f"s{i}" for i in range(step_count)]

    @given(
        step_count=st.integers(min_value=2, max_value=8),
        fail_at=st.integers(min_value=0),
    )
    @settings(max_examples=30)
    @pytest.mark.asyncio
    async def test_err_at_any_position_stops_pipeline(self, step_count: int, fail_at: int):
        fail_at = fail_at % step_count
        steps = []
        for i in range(step_count):
            if i == fail_at:
                steps.append(_err_step(f"step_{i}", f"err_{i}"))
            else:
                steps.append(_ok_step(f"step_{i}"))

        bus = CollectingEventBus()
        runner = PipelineRunner(steps=steps, bus=bus)
        result = await runner.run(SimpleCtx())

        assert result.is_err
        assert "pipeline.complete" not in [e.name for e in bus.events]


# ==========================================================================
# 4. FAILURE INJECTION TESTS
# ==========================================================================

class TestFailureInjection:
    @pytest.mark.asyncio
    async def test_step_raises_exception_returns_err(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(
            steps=[_raise_step("boom")],
            bus=bus,
            correlation_id="corr-fail",
        )
        result = await runner.run(SimpleCtx())

        assert result.is_err
        assert isinstance(result.unwrap_err(), RuntimeError)
        assert "boom exploded" in str(result.unwrap_err())

    @pytest.mark.asyncio
    async def test_step_exception_logs_with_logger(self, caplog):
        logger = logging.getLogger("test.pipeline.fail")
        runner = PipelineRunner(
            steps=[_raise_step("kaboom", RuntimeError("kaboom!"))],
            logger=logger,
            correlation_id="corr-log",
        )
        with caplog.at_level(logging.ERROR, logger="test.pipeline.fail"):
            result = await runner.run(SimpleCtx())

        assert result.is_err
        assert any("pipeline_step_failed" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_step_exception_includes_step_name_and_correlation_in_log(self, caplog):
        logger = logging.getLogger("test.pipeline.extra")
        runner = PipelineRunner(
            steps=[_raise_step("exploder")],
            logger=logger,
            correlation_id="corr-xyz",
        )
        with caplog.at_level(logging.ERROR, logger="test.pipeline.extra"):
            await runner.run(SimpleCtx())

        fail_records = [r for r in caplog.records if "pipeline_step_failed" in r.message]
        assert len(fail_records) >= 1
        rec = fail_records[0]
        assert rec.step == "exploder"  # type: ignore[attr-defined]
        assert rec.correlation_id == "corr-xyz"  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_err_result_stops_early_no_exception(self):
        """Step fn returning err(Result) stops the pipeline without raising."""
        steps = [_ok_step("a"), _err_step("b", "validation_failed"), _ok_step("c")]
        runner = PipelineRunner(steps=steps)
        result = await runner.run(SimpleCtx())

        assert result.is_err
        assert result.unwrap_err() == "validation_failed"

    @pytest.mark.asyncio
    async def test_exception_after_successful_steps(self):
        """Exception in a later step still returns err and logs."""
        steps = [
            _ok_step("good1"),
            _ok_step("good2"),
            _raise_step("bad", ValueError("late_failure")),
        ]
        runner = PipelineRunner(steps=steps)
        result = await runner.run(SimpleCtx())

        assert result.is_err
        assert isinstance(result.unwrap_err(), ValueError)

    @pytest.mark.asyncio
    async def test_exception_does_not_emit_complete(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[_raise_step("fail")], bus=bus)
        await runner.run(SimpleCtx())

        event_names = [e.name for e in bus.events]
        assert "pipeline.complete" not in event_names


# ==========================================================================
# 5. CONCURRENCY TESTS
# ==========================================================================

class TestConcurrency:
    @pytest.mark.asyncio
    async def test_parallel_pipelines_no_crosstalk(self):
        """Run multiple pipelines concurrently; each has its own events and context."""
        results = {}

        async def run_pipeline(pipeline_id: int):
            bus = CollectingEventBus()

            def make_step(name: str):
                async def fn(ctx: SimpleCtx) -> Result[SimpleCtx, str]:
                    # Simulate small async work
                    await asyncio.sleep(0.001)
                    ctx.trace.append(f"p{pipeline_id}_{name}")
                    return ok(ctx)
                return PipelineStep(name=name, fn=fn)

            steps = [make_step("a"), make_step("b")]
            runner = PipelineRunner(
                steps=steps, bus=bus, correlation_id=f"pipeline-{pipeline_id}"
            )
            result = await runner.run(SimpleCtx(value=pipeline_id))
            results[pipeline_id] = {
                "result": result,
                "events": bus.events,
            }

        await asyncio.gather(*(run_pipeline(i) for i in range(5)))

        for i in range(5):
            entry = results[i]
            result = entry["result"]
            events = entry["events"]

            assert result.is_ok
            trace = result.unwrap().trace
            # Only this pipeline's steps
            assert trace == [f"p{i}_a", f"p{i}_b"]
            # Correlation id correct on all events
            for ev in events:
                assert ev.correlation_id == f"pipeline-{i}"

    @pytest.mark.asyncio
    async def test_concurrent_pipelines_different_step_counts(self):
        """Pipelines with different numbers of steps run correctly in parallel."""
        results = {}

        async def run_pipeline(n_steps: int, pid: int):
            steps = [_async_ok_step(f"s{j}") for j in range(n_steps)]
            bus = CollectingEventBus()
            runner = PipelineRunner(steps=steps, bus=bus)
            result = await runner.run(SimpleCtx(value=pid))
            results[pid] = {"result": result, "events": bus.events, "n_steps": n_steps}

        await asyncio.gather(
            run_pipeline(1, 0),
            run_pipeline(3, 1),
            run_pipeline(5, 2),
        )

        for pid in range(3):
            entry = results[pid]
            assert entry["result"].is_ok
            assert len(entry["events"]) == entry["n_steps"] * 2 + 1  # start+ok per step + complete

    @pytest.mark.asyncio
    async def test_concurrent_with_failures(self):
        """Some pipelines fail, others succeed; no interference."""

        async def run_ok():
            runner = PipelineRunner(steps=[_ok_step("fine")])
            return await runner.run(SimpleCtx())

        async def run_fail():
            runner = PipelineRunner(steps=[_err_step("bad", "err")])
            return await runner.run(SimpleCtx())

        r_ok, r_fail, r_ok2 = await asyncio.gather(run_ok(), run_fail(), run_ok())
        assert r_ok.is_ok
        assert r_fail.is_err
        assert r_ok2.is_ok


# ==========================================================================
# 6. SECURITY / ABUSE TESTS
# ==========================================================================

class TestSecurityAbuse:
    @pytest.mark.asyncio
    async def test_very_long_step_name(self):
        long_name = "x" * 10_000
        step = PipelineStep(name=long_name, fn=lambda ctx: ok(ctx))
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[step], bus=bus)
        result = await runner.run(SimpleCtx())

        assert result.is_ok
        assert bus.events[0].name == f"pipeline.{long_name}.start"

    @pytest.mark.asyncio
    async def test_special_characters_in_step_name(self):
        special_names = [
            "step with spaces",
            "step/with/slashes",
            "step.with.dots",
            'step"with"quotes',
            "step\nwith\nnewlines",
            "step<script>alert(1)</script>",
            "step\x00null",
        ]
        for name in special_names:
            bus = CollectingEventBus()
            step = PipelineStep(name=name, fn=lambda ctx: ok(ctx))
            runner = PipelineRunner(steps=[step], bus=bus)
            result = await runner.run(SimpleCtx())
            assert result.is_ok, f"Failed for step name: {name!r}"

    @pytest.mark.asyncio
    async def test_empty_step_name(self):
        step = PipelineStep(name="", fn=lambda ctx: ok(ctx))
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[step], bus=bus)
        result = await runner.run(SimpleCtx())

        assert result.is_ok
        assert bus.events[0].name == "pipeline..start"

    @pytest.mark.asyncio
    async def test_huge_context_object(self):
        @dataclass
        class HugeCtx:
            data: List[int] = field(default_factory=list)

        ctx = HugeCtx(data=list(range(100_000)))

        def fn(c: HugeCtx) -> Result[HugeCtx, str]:
            return ok(c)

        step = PipelineStep(name="heavy", fn=fn)
        runner = PipelineRunner(steps=[step])
        result = await runner.run(ctx)

        assert result.is_ok
        assert len(result.unwrap().data) == 100_000

    @pytest.mark.asyncio
    async def test_unicode_step_names(self):
        names = ["etape", "schritt", "shaggy_dog"]
        steps = [PipelineStep(name=n, fn=lambda ctx: ok(ctx)) for n in names]
        runner = PipelineRunner(steps=steps)
        result = await runner.run(SimpleCtx())
        assert result.is_ok

    @pytest.mark.asyncio
    async def test_none_correlation_id_in_events(self):
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=[_ok_step("s")], bus=bus, correlation_id=None)
        await runner.run(SimpleCtx())

        for ev in bus.events:
            assert ev.correlation_id is None


# ==========================================================================
# 7. USABILITY TESTS -- Realistic pipelines
# ==========================================================================

class TestRealisticPipelines:
    @pytest.mark.asyncio
    async def test_validate_transform_persist_pattern(self):
        """Simulates a real-world validate -> transform -> persist pipeline."""

        @dataclass
        class ReportCtx:
            raw_data: str = ""
            validated: bool = False
            transformed_data: str = ""
            persisted: bool = False
            audit: List[str] = field(default_factory=list)

        def validate(ctx: ReportCtx) -> Result[ReportCtx, str]:
            if not ctx.raw_data:
                return err("empty_input")
            ctx.validated = True
            ctx.audit.append("validated")
            return ok(ctx)

        def transform(ctx: ReportCtx) -> Result[ReportCtx, str]:
            ctx.transformed_data = ctx.raw_data.upper()
            ctx.audit.append("transformed")
            return ok(ctx)

        def persist(ctx: ReportCtx) -> Result[ReportCtx, str]:
            ctx.persisted = True
            ctx.audit.append("persisted")
            return ok(ctx)

        steps = [
            PipelineStep(name="validate", fn=validate),
            PipelineStep(name="transform", fn=transform),
            PipelineStep(name="persist", fn=persist),
        ]
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=steps, bus=bus, correlation_id="report-001")

        # Successful case
        ctx = ReportCtx(raw_data="hello world")
        result = await runner.run(ctx)

        assert result.is_ok
        final = result.unwrap()
        assert final.validated is True
        assert final.transformed_data == "HELLO WORLD"
        assert final.persisted is True
        assert final.audit == ["validated", "transformed", "persisted"]

        # pipeline.complete emitted
        event_names = [e.name for e in bus.events]
        assert "pipeline.complete" in event_names

    @pytest.mark.asyncio
    async def test_validate_transform_persist_validation_failure(self):
        """Validation failure stops the pipeline early."""

        @dataclass
        class ReportCtx:
            raw_data: str = ""
            validated: bool = False
            transformed_data: str = ""
            persisted: bool = False

        def validate(ctx: ReportCtx) -> Result[ReportCtx, str]:
            if not ctx.raw_data:
                return err("empty_input")
            ctx.validated = True
            return ok(ctx)

        def transform(ctx: ReportCtx) -> Result[ReportCtx, str]:
            ctx.transformed_data = ctx.raw_data.upper()
            return ok(ctx)

        def persist(ctx: ReportCtx) -> Result[ReportCtx, str]:
            ctx.persisted = True
            return ok(ctx)

        steps = [
            PipelineStep(name="validate", fn=validate),
            PipelineStep(name="transform", fn=transform),
            PipelineStep(name="persist", fn=persist),
        ]
        bus = CollectingEventBus()
        runner = PipelineRunner(steps=steps, bus=bus)

        result = await runner.run(ReportCtx(raw_data=""))

        assert result.is_err
        assert result.unwrap_err() == "empty_input"
        event_names = [e.name for e in bus.events]
        assert "pipeline.validate.error" in event_names
        assert "pipeline.transform.start" not in event_names
        assert "pipeline.complete" not in event_names

    @pytest.mark.asyncio
    async def test_conditional_step_with_guard(self):
        """Guard-based conditional step in a realistic pipeline."""

        @dataclass
        class IngestCtx:
            file_type: str = "pdf"
            content: str = ""
            ocr_done: bool = False
            parsed: bool = False

        def parse(ctx: IngestCtx) -> Result[IngestCtx, str]:
            ctx.parsed = True
            ctx.content = "parsed_content"
            return ok(ctx)

        def ocr(ctx: IngestCtx) -> Result[IngestCtx, str]:
            ctx.ocr_done = True
            ctx.content = "ocr_content"
            return ok(ctx)

        def finalize(ctx: IngestCtx) -> Result[IngestCtx, str]:
            return ok(ctx)

        steps = [
            PipelineStep(name="parse", fn=parse),
            PipelineStep(
                name="ocr",
                fn=ocr,
                guard=lambda ctx: ctx.file_type == "image",
            ),
            PipelineStep(name="finalize", fn=finalize),
        ]

        # PDF -> OCR is skipped
        runner = PipelineRunner(steps=steps)
        result = await runner.run(IngestCtx(file_type="pdf"))
        assert result.is_ok
        assert result.unwrap().parsed is True
        assert result.unwrap().ocr_done is False

        # Image -> OCR runs
        runner2 = PipelineRunner(steps=steps)
        result2 = await runner2.run(IngestCtx(file_type="image"))
        assert result2.is_ok
        assert result2.unwrap().ocr_done is True

    @pytest.mark.asyncio
    async def test_full_event_lifecycle_with_correlation(self):
        """Verify the complete event lifecycle from a realistic pipeline."""
        bus = CollectingEventBus()
        steps = [_ok_step("fetch"), _ok_step("process"), _ok_step("store")]
        runner = PipelineRunner(steps=steps, bus=bus, correlation_id="job-42")
        await runner.run(SimpleCtx())

        expected_event_names = [
            "pipeline.fetch.start",
            "pipeline.fetch.ok",
            "pipeline.process.start",
            "pipeline.process.ok",
            "pipeline.store.start",
            "pipeline.store.ok",
            "pipeline.complete",
        ]
        actual_names = [e.name for e in bus.events]
        assert actual_names == expected_event_names

        # All events carry correlation_id
        for ev in bus.events:
            assert ev.correlation_id == "job-42"
            assert "ctx_type" in ev.payload
