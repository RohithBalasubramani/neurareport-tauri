"""Comprehensive tests for backend.app.utils.result — Result monad.

Coverage layers:
  1. Unit tests        — ok/err construction, is_ok/is_err, unwrap, unwrap_err,
                         map, bind, map_err, unwrap_or, tap, frozen dataclass
  2. Integration tests — chained map().bind().tap(), bind_async, tap_async,
                         _maybe_await with sync and async values
  3. Property-based    — Hypothesis-driven: wrapping random values preserves
                         identity through unwrap, map preserves ok/err status
  4. Failure injection — exceptions raised inside map/bind/tap propagate
  5. Concurrency       — parallel bind_async / tap_async via asyncio.gather
  6. Security / abuse  — very large values, None as value, exception objects
                         as error payloads
  7. Usability         — realistic validate -> transform -> persist pipeline
                         with err short-circuit
"""
from __future__ import annotations

import asyncio
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.app.utils.result import Result, ok, err, _maybe_await


# ==========================================================================
# 1. UNIT TESTS
# ==========================================================================
class TestOkConstruction:
    """ok() creates a Result with is_ok=True and is_err=False."""

    def test_ok_is_ok(self):
        r = ok(42)
        assert r.is_ok is True

    def test_ok_is_not_err(self):
        r = ok(42)
        assert r.is_err is False

    def test_ok_value(self):
        r = ok("hello")
        assert r.value == "hello"

    def test_ok_error_is_none(self):
        r = ok(99)
        assert r.error is None


class TestErrConstruction:
    """err() creates a Result with is_err=True and is_ok=False."""

    def test_err_is_err(self):
        r = err("boom")
        assert r.is_err is True

    def test_err_is_not_ok(self):
        r = err("boom")
        assert r.is_ok is False

    def test_err_error(self):
        r = err("oops")
        assert r.error == "oops"

    def test_err_value_is_none(self):
        r = err("fail")
        assert r.value is None


class TestUnwrap:
    """unwrap on ok returns value; on err raises RuntimeError."""

    def test_unwrap_ok(self):
        assert ok(7).unwrap() == 7

    def test_unwrap_err_raises(self):
        with pytest.raises(RuntimeError, match="Tried to unwrap Err result"):
            err("bad").unwrap()

    def test_unwrap_err_includes_error_in_message(self):
        with pytest.raises(RuntimeError, match="bad"):
            err("bad").unwrap()


class TestUnwrapErr:
    """unwrap_err on err returns error; on ok raises RuntimeError."""

    def test_unwrap_err_on_err(self):
        assert err("fail").unwrap_err() == "fail"

    def test_unwrap_err_on_ok_raises(self):
        with pytest.raises(RuntimeError, match="Tried to unwrap_err on Ok result"):
            ok(1).unwrap_err()


class TestMap:
    """map applies fn when ok; propagates error when err."""

    def test_map_ok(self):
        r = ok(3).map(lambda x: x * 2)
        assert r.unwrap() == 6

    def test_map_err_propagates(self):
        r = err("nope").map(lambda x: x * 2)
        assert r.is_err
        assert r.unwrap_err() == "nope"

    def test_map_chained(self):
        r = ok(1).map(lambda x: x + 1).map(lambda x: x * 10)
        assert r.unwrap() == 20


class TestBind:
    """bind applies fn returning Result when ok; propagates on err."""

    def test_bind_ok(self):
        r = ok(5).bind(lambda x: ok(x + 10))
        assert r.unwrap() == 15

    def test_bind_ok_to_err(self):
        r = ok(5).bind(lambda _: err("nope"))
        assert r.is_err
        assert r.unwrap_err() == "nope"

    def test_bind_err_propagates(self):
        r = err("fail").bind(lambda x: ok(x + 10))
        assert r.is_err
        assert r.unwrap_err() == "fail"


class TestMapErr:
    """map_err transforms error when err; passes through when ok."""

    def test_map_err_on_err(self):
        r = err("low").map_err(lambda e: e.upper())
        assert r.unwrap_err() == "LOW"

    def test_map_err_on_ok(self):
        r = ok(42).map_err(lambda e: e.upper())
        assert r.is_ok
        assert r.unwrap() == 42


class TestUnwrapOr:
    """unwrap_or returns value on ok, default on err."""

    def test_unwrap_or_ok(self):
        assert ok(10).unwrap_or(99) == 10

    def test_unwrap_or_err(self):
        assert err("x").unwrap_or(99) == 99


class TestTap:
    """tap calls fn on ok (side-effect), skips on err, returns self."""

    def test_tap_ok_calls_fn(self):
        spy = MagicMock()
        r = ok(7).tap(spy)
        spy.assert_called_once_with(7)
        assert r.unwrap() == 7

    def test_tap_err_skips_fn(self):
        spy = MagicMock()
        r = err("e").tap(spy)
        spy.assert_not_called()
        assert r.is_err

    def test_tap_returns_same_result(self):
        original = ok("data")
        returned = original.tap(lambda _: None)
        assert returned is original


class TestFrozenDataclass:
    """Result is frozen: attribute assignment raises FrozenInstanceError."""

    def test_cannot_set_value(self):
        r = ok(1)
        with pytest.raises(FrozenInstanceError):
            r.value = 999

    def test_cannot_set_error(self):
        r = err("x")
        with pytest.raises(FrozenInstanceError):
            r.error = "y"


# ==========================================================================
# 2. INTEGRATION TESTS
# ==========================================================================
class TestChainingIntegration:
    """Chain map, bind, and tap in a realistic sequence."""

    def test_map_bind_tap_chain(self):
        log = []
        result = (
            ok(2)
            .map(lambda x: x * 3)           # 6
            .bind(lambda x: ok(x + 4))       # 10
            .tap(lambda x: log.append(x))    # side-effect
            .map(lambda x: str(x))           # "10"
        )
        assert result.unwrap() == "10"
        assert log == [10]

    def test_chain_short_circuits_on_err(self):
        spy = MagicMock()
        result = (
            ok(1)
            .bind(lambda _: err("stop"))
            .map(lambda x: x + 100)
            .tap(spy)
        )
        assert result.is_err
        assert result.unwrap_err() == "stop"
        spy.assert_not_called()


class TestBindAsync:
    """bind_async with an async callback."""

    @pytest.mark.asyncio
    async def test_bind_async_ok(self):
        async def double(x):
            return ok(x * 2)

        r = await ok(5).bind_async(double)
        assert r.unwrap() == 10

    @pytest.mark.asyncio
    async def test_bind_async_err_propagates(self):
        async def double(x):
            return ok(x * 2)

        r = await err("fail").bind_async(double)
        assert r.is_err
        assert r.unwrap_err() == "fail"

    @pytest.mark.asyncio
    async def test_bind_async_returns_err(self):
        async def always_fail(_x):
            return err("async fail")

        r = await ok(1).bind_async(always_fail)
        assert r.is_err
        assert r.unwrap_err() == "async fail"


class TestTapAsync:
    """tap_async with async and sync callbacks."""

    @pytest.mark.asyncio
    async def test_tap_async_ok_with_async_fn(self):
        log = []

        async def record(x):
            log.append(x)

        r = await ok("hi").tap_async(record)
        assert r.unwrap() == "hi"
        assert log == ["hi"]

    @pytest.mark.asyncio
    async def test_tap_async_err_skips(self):
        spy = MagicMock()

        async def record(x):
            spy(x)

        r = await err("e").tap_async(record)
        assert r.is_err
        spy.assert_not_called()

    @pytest.mark.asyncio
    async def test_tap_async_with_sync_fn(self):
        """_maybe_await wraps sync return so tap_async still works."""
        log = []

        def sync_record(x):
            log.append(x)

        r = await ok("val").tap_async(sync_record)
        assert r.unwrap() == "val"
        assert log == ["val"]


class TestMaybeAwait:
    """_maybe_await with sync and async values."""

    @pytest.mark.asyncio
    async def test_sync_value(self):
        result = await _maybe_await(42)
        assert result == 42

    @pytest.mark.asyncio
    async def test_async_coroutine(self):
        async def get_val():
            return "async_val"

        result = await _maybe_await(get_val())
        assert result == "async_val"

    @pytest.mark.asyncio
    async def test_sync_none(self):
        result = await _maybe_await(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_sync_string(self):
        result = await _maybe_await("hello")
        assert result == "hello"


# ==========================================================================
# 3. PROPERTY-BASED TESTS
# ==========================================================================
class TestPropertyBased:
    """Hypothesis-driven invariant checks."""

    @given(value=st.integers())
    @settings(max_examples=100)
    def test_ok_unwrap_identity_int(self, value):
        assert ok(value).unwrap() == value

    @given(value=st.text())
    @settings(max_examples=100)
    def test_ok_unwrap_identity_text(self, value):
        assert ok(value).unwrap() == value

    @given(error=st.text(min_size=1))
    @settings(max_examples=100)
    def test_err_unwrap_err_identity(self, error):
        assert err(error).unwrap_err() == error

    @given(value=st.integers())
    @settings(max_examples=100)
    def test_map_preserves_ok_status(self, value):
        r = ok(value).map(lambda x: x + 1)
        assert r.is_ok is True
        assert r.is_err is False

    @given(error=st.text(min_size=1))
    @settings(max_examples=100)
    def test_map_preserves_err_status(self, error):
        r = err(error).map(lambda x: x + 1)
        assert r.is_err is True
        assert r.is_ok is False

    @given(value=st.integers())
    @settings(max_examples=100)
    def test_unwrap_or_returns_value_for_ok(self, value):
        assert ok(value).unwrap_or(-1) == value

    @given(error=st.text(min_size=1))
    @settings(max_examples=100)
    def test_unwrap_or_returns_default_for_err(self, error):
        assert err(error).unwrap_or("default") == "default"

    @given(value=st.integers(), factor=st.integers(min_value=-1000, max_value=1000))
    @settings(max_examples=100)
    def test_map_then_unwrap_equals_fn_of_value(self, value, factor):
        r = ok(value).map(lambda x: x * factor)
        assert r.unwrap() == value * factor


# ==========================================================================
# 4. FAILURE INJECTION
# ==========================================================================
class TestFailureInjection:
    """Exceptions raised inside map/bind/tap propagate to the caller."""

    def test_map_fn_raises(self):
        def boom(_x):
            raise ValueError("map exploded")

        with pytest.raises(ValueError, match="map exploded"):
            ok(1).map(boom)

    def test_bind_fn_raises(self):
        def boom(_x):
            raise TypeError("bind exploded")

        with pytest.raises(TypeError, match="bind exploded"):
            ok(1).bind(boom)

    def test_tap_fn_raises(self):
        def boom(_x):
            raise IOError("tap exploded")

        with pytest.raises(IOError, match="tap exploded"):
            ok(1).tap(boom)

    @pytest.mark.asyncio
    async def test_bind_async_fn_raises(self):
        async def boom(_x):
            raise RuntimeError("async bind exploded")

        with pytest.raises(RuntimeError, match="async bind exploded"):
            await ok(1).bind_async(boom)

    @pytest.mark.asyncio
    async def test_tap_async_fn_raises(self):
        async def boom(_x):
            raise RuntimeError("async tap exploded")

        with pytest.raises(RuntimeError, match="async tap exploded"):
            await ok(1).tap_async(boom)

    def test_map_on_err_does_not_call_fn(self):
        """Even a fn that would raise is never invoked on err path."""
        def bomb(_x):
            raise AssertionError("should never be called")

        r = err("problem").map(bomb)
        assert r.is_err

    def test_bind_on_err_does_not_call_fn(self):
        def bomb(_x):
            raise AssertionError("should never be called")

        r = err("problem").bind(bomb)
        assert r.is_err


# ==========================================================================
# 5. CONCURRENCY
# ==========================================================================
class TestConcurrency:
    """Parallel async operations via asyncio.gather."""

    @pytest.mark.asyncio
    async def test_parallel_bind_async(self):
        async def add_ten(x):
            await asyncio.sleep(0.01)
            return ok(x + 10)

        results_coros = [ok(i).bind_async(add_ten) for i in range(10)]
        results = await asyncio.gather(*results_coros)

        for i, r in enumerate(results):
            assert r.unwrap() == i + 10

    @pytest.mark.asyncio
    async def test_parallel_tap_async(self):
        collected = []

        async def record(x):
            await asyncio.sleep(0.01)
            collected.append(x)

        coros = [ok(i).tap_async(record) for i in range(10)]
        results = await asyncio.gather(*coros)

        assert sorted(collected) == list(range(10))
        for i, r in enumerate(results):
            assert r.unwrap() == i

    @pytest.mark.asyncio
    async def test_mixed_ok_err_parallel_bind_async(self):
        """A mix of ok/err values processed in parallel."""

        async def try_double(x):
            return ok(x * 2)

        inputs = [ok(1), err("e1"), ok(3), err("e2"), ok(5)]
        coros = [inp.bind_async(try_double) for inp in inputs]
        results = await asyncio.gather(*coros)

        assert results[0].unwrap() == 2
        assert results[1].is_err and results[1].unwrap_err() == "e1"
        assert results[2].unwrap() == 6
        assert results[3].is_err and results[3].unwrap_err() == "e2"
        assert results[4].unwrap() == 10

    @pytest.mark.asyncio
    async def test_parallel_bind_async_some_raise(self):
        """One failing coroutine does not poison the others when handled."""

        async def maybe_fail(x):
            if x == 3:
                raise ValueError("three is bad")
            return ok(x)

        coros = []
        for i in range(5):
            coros.append(ok(i).bind_async(maybe_fail))

        # Gather with return_exceptions so the ValueError doesn't crash the test
        results = await asyncio.gather(*coros, return_exceptions=True)

        assert results[0].unwrap() == 0
        assert results[1].unwrap() == 1
        assert results[2].unwrap() == 2
        assert isinstance(results[3], ValueError)
        assert results[4].unwrap() == 4


# ==========================================================================
# 6. SECURITY / ABUSE
# ==========================================================================
class TestSecurityAbuse:
    """Edge-case and adversarial payloads."""

    def test_very_large_value(self):
        big = "x" * 10_000_000
        r = ok(big)
        assert r.unwrap() == big
        assert len(r.unwrap()) == 10_000_000

    def test_very_large_error(self):
        big = "e" * 10_000_000
        r = err(big)
        assert r.unwrap_err() == big

    def test_none_as_ok_value(self):
        """ok(None) is technically ok -- error is None, value is None."""
        r = ok(None)
        assert r.is_ok is True
        assert r.unwrap() is None

    def test_exception_object_as_error(self):
        exc = ValueError("inner error")
        r = err(exc)
        assert r.is_err
        assert r.unwrap_err() is exc
        assert str(r.unwrap_err()) == "inner error"

    def test_nested_result_as_value(self):
        inner = ok(42)
        outer = ok(inner)
        assert outer.unwrap().unwrap() == 42

    def test_result_with_dict_value(self):
        data = {"key": "value", "nested": {"a": 1}}
        r = ok(data)
        assert r.unwrap()["key"] == "value"

    def test_result_with_list_value(self):
        r = ok([1, 2, 3])
        assert r.unwrap() == [1, 2, 3]

    def test_err_with_zero(self):
        """0 is falsy but is a valid error value (error is not None)."""
        r = err(0)
        assert r.is_err is True
        assert r.unwrap_err() == 0

    def test_err_with_empty_string(self):
        """Empty string is falsy but is a valid error value."""
        r = err("")
        assert r.is_err is True
        assert r.unwrap_err() == ""

    def test_unwrap_err_message_contains_error_repr(self):
        """RuntimeError message when unwrapping err includes the error."""
        r = err({"code": 404, "msg": "not found"})
        with pytest.raises(RuntimeError) as exc_info:
            r.unwrap()
        assert "not found" in str(exc_info.value)


# ==========================================================================
# 7. USABILITY — realistic pipeline
# ==========================================================================
class TestUsabilityPipeline:
    """
    Realistic error-handling chain: validate -> transform -> persist.
    Errors at any stage short-circuit the pipeline.
    """

    @staticmethod
    def _validate_age(age: int) -> Result[int, str]:
        if age < 0:
            return err("Age cannot be negative")
        if age > 150:
            return err("Age exceeds maximum")
        return ok(age)

    @staticmethod
    def _categorize(age: int) -> str:
        if age < 18:
            return "minor"
        if age < 65:
            return "adult"
        return "senior"

    def test_valid_adult(self):
        result = (
            self._validate_age(30)
            .map(self._categorize)
        )
        assert result.unwrap() == "adult"

    def test_valid_minor(self):
        result = self._validate_age(10).map(self._categorize)
        assert result.unwrap() == "minor"

    def test_valid_senior(self):
        result = self._validate_age(70).map(self._categorize)
        assert result.unwrap() == "senior"

    def test_negative_age_short_circuits(self):
        persisted = []
        result = (
            self._validate_age(-5)
            .map(self._categorize)
            .tap(lambda cat: persisted.append(cat))
        )
        assert result.is_err
        assert result.unwrap_err() == "Age cannot be negative"
        assert persisted == []

    def test_excessive_age_short_circuits(self):
        result = self._validate_age(200).map(self._categorize)
        assert result.is_err
        assert result.unwrap_err() == "Age exceeds maximum"

    def test_error_recovery_with_map_err(self):
        """map_err converts a string error to a structured error dict."""
        result = (
            self._validate_age(-1)
            .map_err(lambda e: {"field": "age", "message": e})
        )
        assert result.is_err
        error = result.unwrap_err()
        assert error["field"] == "age"
        assert error["message"] == "Age cannot be negative"

    def test_unwrap_or_provides_fallback(self):
        category = (
            self._validate_age(-1)
            .map(self._categorize)
            .unwrap_or("unknown")
        )
        assert category == "unknown"

    @pytest.mark.asyncio
    async def test_async_pipeline(self):
        """Full async pipeline: validate -> async transform -> async persist."""
        store = []

        async def async_categorize(age: int) -> Result[str, str]:
            await asyncio.sleep(0.01)
            return ok(self._categorize(age))

        async def async_persist(category: str):
            await asyncio.sleep(0.01)
            store.append(category)

        r = await (
            await self._validate_age(25)
            .bind_async(async_categorize)
        ).tap_async(async_persist)

        assert r.unwrap() == "adult"
        assert store == ["adult"]

    @pytest.mark.asyncio
    async def test_async_pipeline_short_circuits(self):
        """Err skips all async steps."""
        store = []

        async def async_categorize(age: int) -> Result[str, str]:
            return ok(self._categorize(age))

        async def async_persist(category: str):
            store.append(category)

        r = await (
            await self._validate_age(-5)
            .bind_async(async_categorize)
        ).tap_async(async_persist)

        assert r.is_err
        assert store == []

    def test_multi_step_bind_chain(self):
        """A multi-step pipeline using bind at each stage."""

        def parse_int(s: str) -> Result[int, str]:
            try:
                return ok(int(s))
            except ValueError:
                return err(f"Cannot parse '{s}' as int")

        def validate_positive(n: int) -> Result[int, str]:
            if n <= 0:
                return err("Must be positive")
            return ok(n)

        # Happy path
        r = ok("42").bind(parse_int).bind(validate_positive)
        assert r.unwrap() == 42

        # Parse failure
        r = ok("abc").bind(parse_int).bind(validate_positive)
        assert r.unwrap_err() == "Cannot parse 'abc' as int"

        # Validation failure
        r = ok("-3").bind(parse_int).bind(validate_positive)
        assert r.unwrap_err() == "Must be positive"
