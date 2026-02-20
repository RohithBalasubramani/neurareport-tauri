"""Comprehensive tests for backend.app.utils.strategies.

Coverage layers:
  1. Unit tests          -- Construction, register, get, resolve basics
  2. Integration tests   -- Callable strategies, class instances, realistic patterns
  3. Property-based      -- Hypothesis: any name/strategy round-trips correctly
  4. Failure injection   -- Edge-case keys and values
  5. Concurrency         -- Thread-safe register + resolve
  6. Security / abuse    -- Long names, unicode, special chars, bulk registrations
  7. Usability           -- Realistic registry patterns from real code
"""
from __future__ import annotations

import string
import threading
from typing import Callable
from unittest.mock import MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.app.utils.strategies import StrategyRegistry


# ==========================================================================
# 1. UNIT TESTS
# ==========================================================================


class TestUnitConstruction:
    """Construction with and without default_factory."""

    def test_construction_no_default_factory(self):
        reg = StrategyRegistry()
        assert reg._registry == {}
        assert reg._default_factory is None

    def test_construction_with_default_factory(self):
        factory = lambda: "fallback"
        reg = StrategyRegistry(default_factory=factory)
        assert reg._default_factory is factory


class TestUnitRegister:
    """register() stores strategies and supports overwrite."""

    def test_register_stores_strategy(self):
        reg = StrategyRegistry()
        reg.register("a", 42)
        assert reg._registry["a"] == 42

    def test_register_overwrites_existing(self):
        reg = StrategyRegistry()
        reg.register("key", "old")
        reg.register("key", "new")
        assert reg._registry["key"] == "new"

    def test_multiple_strategies_registered_independently(self):
        reg = StrategyRegistry()
        reg.register("x", 1)
        reg.register("y", 2)
        reg.register("z", 3)
        assert reg._registry == {"x": 1, "y": 2, "z": 3}


class TestUnitGet:
    """get() returns registered values or None."""

    def test_get_returns_registered_strategy(self):
        reg = StrategyRegistry()
        reg.register("present", "value")
        assert reg.get("present") == "value"

    def test_get_returns_none_for_unknown(self):
        reg = StrategyRegistry()
        assert reg.get("missing") is None

    def test_get_returns_none_on_empty_registry(self):
        reg = StrategyRegistry()
        assert reg.get("anything") is None


class TestUnitResolve:
    """resolve() returns strategy, falls back to default_factory, or raises."""

    def test_resolve_returns_registered_strategy(self):
        reg = StrategyRegistry()
        reg.register("found", "result")
        assert reg.resolve("found") == "result"

    def test_resolve_with_default_factory_returns_default_for_unknown(self):
        reg = StrategyRegistry(default_factory=lambda: "default_value")
        result = reg.resolve("unknown")
        assert result == "default_value"

    def test_resolve_without_default_factory_raises_key_error(self):
        reg = StrategyRegistry()
        with pytest.raises(KeyError, match="No strategy registered for 'missing'"):
            reg.resolve("missing")

    def test_resolve_prefers_registered_over_default(self):
        reg = StrategyRegistry(default_factory=lambda: "default")
        reg.register("explicit", "registered")
        assert reg.resolve("explicit") == "registered"

    def test_resolve_calls_default_factory_each_time(self):
        counter = {"n": 0}

        def factory():
            counter["n"] += 1
            return counter["n"]

        reg = StrategyRegistry(default_factory=factory)
        first = reg.resolve("a")
        second = reg.resolve("b")
        assert first == 1
        assert second == 2

    def test_resolve_error_message_includes_name(self):
        reg = StrategyRegistry()
        with pytest.raises(KeyError) as exc_info:
            reg.resolve("my_strategy")
        assert "my_strategy" in str(exc_info.value)


# ==========================================================================
# 2. INTEGRATION TESTS
# ==========================================================================


class TestIntegrationCallableStrategies:
    """StrategyRegistry works with function/lambda strategies."""

    def test_register_and_call_lambda(self):
        reg: StrategyRegistry[Callable[[int], int]] = StrategyRegistry()
        reg.register("double", lambda x: x * 2)
        strategy = reg.resolve("double")
        assert strategy(5) == 10

    def test_register_and_call_function(self):
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        reg: StrategyRegistry[Callable[[str], str]] = StrategyRegistry()
        reg.register("greet", greet)
        assert reg.resolve("greet")("World") == "Hello, World!"

    def test_register_multiple_resolve_each(self):
        reg: StrategyRegistry[Callable[[int], int]] = StrategyRegistry()
        reg.register("add1", lambda x: x + 1)
        reg.register("mul3", lambda x: x * 3)
        reg.register("neg", lambda x: -x)

        assert reg.resolve("add1")(10) == 11
        assert reg.resolve("mul3")(10) == 30
        assert reg.resolve("neg")(10) == -10


class TestIntegrationClassInstances:
    """StrategyRegistry works with class instances as strategies."""

    def test_register_class_instance(self):
        class UpperFormatter:
            def format(self, text: str) -> str:
                return text.upper()

        reg: StrategyRegistry[UpperFormatter] = StrategyRegistry()
        fmt = UpperFormatter()
        reg.register("upper", fmt)
        assert reg.resolve("upper").format("hello") == "HELLO"

    def test_register_mock_as_strategy(self):
        mock = MagicMock(return_value="mocked")
        reg = StrategyRegistry()
        reg.register("mock_strategy", mock)
        resolved = reg.resolve("mock_strategy")
        assert resolved("arg") == "mocked"
        mock.assert_called_once_with("arg")


class TestIntegrationExportFormats:
    """Realistic pattern: strategy registry for different export formats."""

    def test_export_format_registry(self):
        def csv_export(data: list) -> str:
            return ",".join(str(d) for d in data)

        def json_export(data: list) -> str:
            import json
            return json.dumps(data)

        def excel_export(data: list) -> str:
            return f"<excel>{data}</excel>"

        reg: StrategyRegistry[Callable[[list], str]] = StrategyRegistry()
        reg.register("csv", csv_export)
        reg.register("json", json_export)
        reg.register("excel", excel_export)

        data = [1, 2, 3]
        assert reg.resolve("csv")(data) == "1,2,3"
        assert reg.resolve("json")(data) == "[1, 2, 3]"
        assert "excel" in reg.resolve("excel")(data)

    def test_export_with_default_fallback(self):
        def plain_export(data: list) -> str:
            return str(data)

        reg: StrategyRegistry[Callable[[list], str]] = StrategyRegistry(
            default_factory=lambda: plain_export
        )
        # No explicit registration -- falls back to default
        exporter = reg.resolve("unknown_format")
        assert exporter([1, 2]) == "[1, 2]"


# ==========================================================================
# 3. PROPERTY-BASED TESTS
# ==========================================================================


class TestPropertyBased:
    """Hypothesis-driven tests: any name+strategy round-trips correctly."""

    @given(
        name=st.text(min_size=1, max_size=200),
        value=st.integers(),
    )
    @settings(max_examples=100)
    def test_register_then_get_returns_same_object(self, name: str, value: int):
        reg = StrategyRegistry()
        reg.register(name, value)
        assert reg.get(name) == value

    @given(name=st.text(min_size=0, max_size=300))
    @settings(max_examples=100)
    def test_random_names_never_crash_get(self, name: str):
        reg = StrategyRegistry()
        result = reg.get(name)
        assert result is None

    @given(
        name=st.text(min_size=1, max_size=200),
        value=st.text(),
    )
    @settings(max_examples=100)
    def test_registered_name_always_resolves(self, name: str, value: str):
        reg = StrategyRegistry()
        reg.register(name, value)
        assert reg.resolve(name) == value

    @given(
        name=st.text(min_size=1, max_size=200),
        value=st.one_of(st.integers(), st.text(), st.floats(allow_nan=False), st.booleans()),
    )
    @settings(max_examples=100)
    def test_register_get_identity(self, name, value):
        reg = StrategyRegistry()
        reg.register(name, value)
        assert reg.get(name) is value


# ==========================================================================
# 4. FAILURE INJECTION
# ==========================================================================


class TestFailureInjection:
    """Edge-case keys and values that might trigger unexpected behavior."""

    def test_empty_string_name_registration(self):
        reg = StrategyRegistry()
        reg.register("", "empty_key")
        assert reg.get("") == "empty_key"
        assert reg.resolve("") == "empty_key"

    def test_none_as_strategy_value(self):
        reg = StrategyRegistry()
        reg.register("nullable", None)
        assert reg.get("nullable") is None
        # get returns None for both missing AND None-valued entries,
        # but resolve should return the registered None value.
        assert reg.resolve("nullable") is None

    def test_get_with_empty_string_key(self):
        reg = StrategyRegistry()
        assert reg.get("") is None

    def test_resolve_with_empty_string_raises_when_no_default(self):
        reg = StrategyRegistry()
        with pytest.raises(KeyError):
            reg.resolve("")

    def test_resolve_with_empty_string_uses_default(self):
        reg = StrategyRegistry(default_factory=lambda: "fallback")
        assert reg.resolve("") == "fallback"

    def test_register_none_then_resolve_returns_none(self):
        """Even though None is falsy, it is a valid registered strategy."""
        reg = StrategyRegistry(default_factory=lambda: "default")
        reg.register("nil", None)
        # Should return registered None, not the default
        assert reg.resolve("nil") is None

    def test_default_factory_returning_none(self):
        reg = StrategyRegistry(default_factory=lambda: None)
        result = reg.resolve("anything")
        assert result is None


# ==========================================================================
# 5. CONCURRENCY
# ==========================================================================


class TestConcurrency:
    """Thread-safety: multiple threads registering and resolving."""

    def test_concurrent_register_different_keys(self):
        reg = StrategyRegistry()
        errors: list[Exception] = []

        def register_range(start: int, end: int):
            try:
                for i in range(start, end):
                    reg.register(f"key_{i}", i)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=register_range, args=(0, 100)),
            threading.Thread(target=register_range, args=(100, 200)),
            threading.Thread(target=register_range, args=(200, 300)),
            threading.Thread(target=register_range, args=(300, 400)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        for i in range(400):
            assert reg.get(f"key_{i}") == i

    def test_concurrent_register_and_resolve(self):
        reg = StrategyRegistry(default_factory=lambda: -1)
        results: dict[str, int] = {}
        errors: list[Exception] = []

        def writer():
            try:
                for i in range(200):
                    reg.register(f"w_{i}", i)
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                for i in range(200):
                    val = reg.resolve(f"w_{i}")
                    results[f"w_{i}"] = val
            except Exception as e:
                errors.append(e)

        w = threading.Thread(target=writer)
        r = threading.Thread(target=reader)
        w.start()
        r.start()
        w.join()
        r.join()

        assert len(errors) == 0
        # Each resolved value is either the written value or the default (-1)
        for key, val in results.items():
            assert val == -1 or val == int(key.split("_")[1])

    def test_concurrent_resolve_same_key(self):
        reg = StrategyRegistry()
        reg.register("shared", "value")
        results: list[str] = []
        lock = threading.Lock()

        def resolver():
            for _ in range(100):
                val = reg.resolve("shared")
                with lock:
                    results.append(val)

        threads = [threading.Thread(target=resolver) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 800
        assert all(v == "value" for v in results)


# ==========================================================================
# 6. SECURITY / ABUSE
# ==========================================================================


class TestSecurityAbuse:
    """Stress tests with unusual or adversarial inputs."""

    def test_very_long_strategy_name(self):
        reg = StrategyRegistry()
        long_name = "a" * 10_000
        reg.register(long_name, "payload")
        assert reg.get(long_name) == "payload"
        assert reg.resolve(long_name) == "payload"

    def test_unicode_names(self):
        reg = StrategyRegistry()
        names = [
            "\u00e9\u00e0\u00fc\u00f6\u00e4",       # accented Latin
            "\u4f60\u597d\u4e16\u754c",               # Chinese
            "\u0410\u0411\u0412\u0413",               # Cyrillic
            "\U0001f600\U0001f4a5\U0001f525",         # emoji
            "\u0000\u0001\u0002",                     # null / control chars
        ]
        for i, name in enumerate(names):
            reg.register(name, i)
        for i, name in enumerate(names):
            assert reg.get(name) == i
            assert reg.resolve(name) == i

    def test_special_characters_in_names(self):
        reg = StrategyRegistry()
        specials = [
            "key with spaces",
            "key\twith\ttabs",
            "key\nwith\nnewlines",
            "key/with/slashes",
            'key"with"quotes',
            "key'with'apostrophes",
            "key\\with\\backslashes",
            "key<with>angle<brackets>",
            "key{with}braces",
        ]
        for i, name in enumerate(specials):
            reg.register(name, i)
        for i, name in enumerate(specials):
            assert reg.resolve(name) == i

    def test_large_number_of_registrations(self):
        reg = StrategyRegistry()
        n = 2_000
        for i in range(n):
            reg.register(f"strat_{i}", i)
        assert len(reg._registry) == n
        # Spot-check first, last, middle
        assert reg.get("strat_0") == 0
        assert reg.get(f"strat_{n - 1}") == n - 1
        assert reg.get(f"strat_{n // 2}") == n // 2

    def test_all_printable_ascii_chars_as_name(self):
        reg = StrategyRegistry()
        name = string.printable
        reg.register(name, "ascii_strategy")
        assert reg.resolve(name) == "ascii_strategy"


# ==========================================================================
# 7. USABILITY -- Realistic patterns
# ==========================================================================


class TestUsabilityFormatterRegistry:
    """Realistic use case: formatter registry with default fallback."""

    def test_formatter_registry_with_default(self):
        def plain_formatter(text: str) -> str:
            return text

        def html_formatter(text: str) -> str:
            return f"<p>{text}</p>"

        def markdown_formatter(text: str) -> str:
            return f"**{text}**"

        reg: StrategyRegistry[Callable[[str], str]] = StrategyRegistry(
            default_factory=lambda: plain_formatter
        )
        reg.register("html", html_formatter)
        reg.register("markdown", markdown_formatter)

        assert reg.resolve("html")("hi") == "<p>hi</p>"
        assert reg.resolve("markdown")("hi") == "**hi**"
        # Unknown format falls back to plain
        assert reg.resolve("pdf")("hi") == "hi"
        assert reg.resolve("docx")("hi") == "hi"


class TestUsabilityParserRegistry:
    """Realistic use case: parser registry without default (strict)."""

    def test_parser_registry_raises_for_unknown(self):
        def json_parser(raw: str) -> dict:
            import json
            return json.loads(raw)

        def csv_parser(raw: str) -> list:
            return raw.split(",")

        reg = StrategyRegistry()
        reg.register("json", json_parser)
        reg.register("csv", csv_parser)

        assert reg.resolve("json")('{"a":1}') == {"a": 1}
        assert reg.resolve("csv")("a,b,c") == ["a", "b", "c"]

        with pytest.raises(KeyError, match="No strategy registered for 'xml'"):
            reg.resolve("xml")


class TestUsabilityStrategySwap:
    """Realistic use case: re-registering to swap a strategy at runtime."""

    def test_strategy_swap_via_reregister(self):
        reg: StrategyRegistry[Callable[[int], int]] = StrategyRegistry()
        reg.register("transform", lambda x: x + 1)
        assert reg.resolve("transform")(10) == 11

        # Swap strategy at runtime
        reg.register("transform", lambda x: x * 10)
        assert reg.resolve("transform")(10) == 100

    def test_swap_preserves_other_registrations(self):
        reg = StrategyRegistry()
        reg.register("a", 1)
        reg.register("b", 2)
        reg.register("a", 99)
        assert reg.get("a") == 99
        assert reg.get("b") == 2

    def test_full_lifecycle(self):
        """Register, resolve, swap, resolve again, verify get/resolve coherence."""
        reg: StrategyRegistry[str] = StrategyRegistry(default_factory=lambda: "default")

        # Initially empty -- default kicks in
        assert reg.resolve("fmt") == "default"
        assert reg.get("fmt") is None

        # Register
        reg.register("fmt", "v1")
        assert reg.resolve("fmt") == "v1"
        assert reg.get("fmt") == "v1"

        # Swap
        reg.register("fmt", "v2")
        assert reg.resolve("fmt") == "v2"
        assert reg.get("fmt") == "v2"

        # Other keys still use default
        assert reg.resolve("other") == "default"
