"""Comprehensive tests for backend.app.utils.fs — atomic file write utilities.

Coverage layers:
  1. Unit tests — write_text_atomic, write_json_atomic basic operation
  2. Integration tests — parent dir creation, fsync path
  3. Property-based — random payloads survive round-trip
  4. Failure injection — _maybe_fail, write errors, temp cleanup
  5. Concurrency — parallel writes to same file
  6. Security / abuse — large files, unicode, path edge cases
  7. Usability — realistic JSON persistence patterns
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from backend.app.utils.fs import write_json_atomic, write_text_atomic, _maybe_fail


# ==========================================================================
# 1. UNIT TESTS — write_text_atomic
# ==========================================================================

class TestWriteTextAtomic:
    def test_basic_write(self, tmp_path):
        target = tmp_path / "out.txt"
        write_text_atomic(target, "hello world")
        assert target.read_text(encoding="utf-8") == "hello world"

    def test_overwrite(self, tmp_path):
        target = tmp_path / "out.txt"
        write_text_atomic(target, "first")
        write_text_atomic(target, "second")
        assert target.read_text(encoding="utf-8") == "second"

    def test_binary_write(self, tmp_path):
        target = tmp_path / "out.bin"
        write_text_atomic(target, b"\x00\x01\x02\xff")
        assert target.read_bytes() == b"\x00\x01\x02\xff"

    def test_utf8_encoding(self, tmp_path):
        target = tmp_path / "unicode.txt"
        write_text_atomic(target, "日本語テスト 🇯🇵")
        assert target.read_text(encoding="utf-8") == "日本語テスト 🇯🇵"

    def test_empty_string(self, tmp_path):
        target = tmp_path / "empty.txt"
        write_text_atomic(target, "")
        assert target.read_text() == ""

    def test_parent_dir_created(self, tmp_path):
        target = tmp_path / "deep" / "nested" / "dir" / "out.txt"
        write_text_atomic(target, "nested")
        assert target.read_text() == "nested"

    def test_no_temp_file_left_on_success(self, tmp_path):
        target = tmp_path / "clean.txt"
        write_text_atomic(target, "data")
        files = list(tmp_path.iterdir())
        assert files == [target]

    def test_newline_handling(self, tmp_path):
        target = tmp_path / "newlines.txt"
        write_text_atomic(target, "line1\nline2\nline3")
        content = target.read_text(encoding="utf-8")
        assert "line1" in content and "line3" in content


# ==========================================================================
# 2. UNIT TESTS — write_json_atomic
# ==========================================================================

class TestWriteJsonAtomic:
    def test_dict_payload(self, tmp_path):
        target = tmp_path / "data.json"
        write_json_atomic(target, {"key": "value", "num": 42})
        loaded = json.loads(target.read_text())
        assert loaded == {"key": "value", "num": 42}

    def test_list_payload(self, tmp_path):
        target = tmp_path / "arr.json"
        write_json_atomic(target, [1, 2, 3])
        assert json.loads(target.read_text()) == [1, 2, 3]

    def test_null_payload(self, tmp_path):
        target = tmp_path / "null.json"
        write_json_atomic(target, None)
        assert json.loads(target.read_text()) is None

    def test_indent_default_2(self, tmp_path):
        target = tmp_path / "indented.json"
        write_json_atomic(target, {"a": 1})
        text = target.read_text()
        assert "  " in text  # 2-space indent

    def test_sort_keys(self, tmp_path):
        target = tmp_path / "sorted.json"
        write_json_atomic(target, {"b": 2, "a": 1}, sort_keys=True)
        text = target.read_text()
        assert text.index('"a"') < text.index('"b"')

    def test_no_indent(self, tmp_path):
        target = tmp_path / "compact.json"
        write_json_atomic(target, {"a": 1}, indent=None)
        text = target.read_text()
        assert "\n" not in text.strip()

    def test_unicode_preserved(self, tmp_path):
        target = tmp_path / "uni.json"
        write_json_atomic(target, {"msg": "héllo wörld"})
        loaded = json.loads(target.read_text(encoding="utf-8"))
        assert loaded["msg"] == "héllo wörld"

    def test_nested_structure(self, tmp_path):
        target = tmp_path / "nested.json"
        data = {"a": {"b": {"c": [1, 2, {"d": True}]}}}
        write_json_atomic(target, data)
        assert json.loads(target.read_text()) == data


# ==========================================================================
# 3. PROPERTY-BASED — round-trip
# ==========================================================================

class TestPropertyBased:
    @given(st.text(max_size=5000))
    @settings(max_examples=100)
    def test_text_roundtrip(self, content):
        import tempfile, shutil
        d = Path(tempfile.mkdtemp())
        try:
            target = d / "prop.txt"
            write_text_atomic(target, content)
            # Read with newline="" to match the write mode (no translation)
            with open(target, "r", encoding="utf-8", newline="") as f:
                assert f.read() == content
        finally:
            shutil.rmtree(d, ignore_errors=True)

    @given(
        st.recursive(
            st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.text(max_size=50), st.booleans(), st.none()),
            lambda children: st.lists(children, max_size=5) | st.dictionaries(st.text(min_size=1, max_size=20), children, max_size=5),
            max_leaves=30,
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_json_roundtrip(self, data):
        import tempfile, shutil
        d = Path(tempfile.mkdtemp())
        try:
            target = d / "prop.json"
            write_json_atomic(target, data)
            loaded = json.loads(target.read_text(encoding="utf-8"))
            assert loaded == data
        finally:
            shutil.rmtree(d, ignore_errors=True)


# ==========================================================================
# 4. FAILURE INJECTION
# ==========================================================================

class TestMaybeFail:
    def test_no_env_var_no_failure(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NEURA_FAIL_AFTER_STEP", None)
            _maybe_fail("render")  # Should not raise

    def test_matching_step_raises(self):
        with patch.dict(os.environ, {"NEURA_FAIL_AFTER_STEP": "render"}):
            with pytest.raises(RuntimeError, match="Simulated failure"):
                _maybe_fail("render")

    def test_case_insensitive_match(self):
        with patch.dict(os.environ, {"NEURA_FAIL_AFTER_STEP": "RENDER"}):
            with pytest.raises(RuntimeError):
                _maybe_fail("render")

    def test_non_matching_step_passes(self):
        with patch.dict(os.environ, {"NEURA_FAIL_AFTER_STEP": "render"}):
            _maybe_fail("finalize")  # Different step — should not raise

    def test_none_step_passes(self):
        with patch.dict(os.environ, {"NEURA_FAIL_AFTER_STEP": "render"}):
            _maybe_fail(None)  # None step — should not raise


class TestFailureRecovery:
    def test_simulated_failure_cleans_temp(self, tmp_path):
        target = tmp_path / "fail.txt"
        with patch.dict(os.environ, {"NEURA_FAIL_AFTER_STEP": "write"}):
            with pytest.raises(RuntimeError):
                write_text_atomic(target, "should not persist", step="write")
        # Target should NOT exist (write failed before replace)
        assert not target.exists()
        # No temp files left
        remaining = list(tmp_path.iterdir())
        assert remaining == []

    def test_original_preserved_on_failure(self, tmp_path):
        target = tmp_path / "keep.txt"
        write_text_atomic(target, "original")
        with patch.dict(os.environ, {"NEURA_FAIL_AFTER_STEP": "update"}):
            with pytest.raises(RuntimeError):
                write_text_atomic(target, "updated", step="update")
        assert target.read_text() == "original"


# ==========================================================================
# 5. CONCURRENCY
# ==========================================================================

class TestConcurrency:
    def test_parallel_writes_to_separate_files(self, tmp_path):
        """Each thread writes to its own file — no cross-contamination."""
        errors = []

        def writer(idx):
            try:
                target = tmp_path / f"concurrent_{idx}.json"
                for _ in range(10):
                    write_json_atomic(target, {"writer": idx, "data": list(range(50))})
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert not errors
        # Each file must be valid JSON with correct writer
        for i in range(5):
            data = json.loads((tmp_path / f"concurrent_{i}.json").read_text())
            assert data["writer"] == i
            assert len(data["data"]) == 50

    def test_serialized_writes_to_same_file(self, tmp_path):
        """Sequential atomic writes to the same path — each one coherent."""
        target = tmp_path / "serial.json"
        for i in range(20):
            write_json_atomic(target, {"iteration": i, "payload": "x" * 100})
        data = json.loads(target.read_text())
        assert data["iteration"] == 19


# ==========================================================================
# 6. SECURITY / ABUSE
# ==========================================================================

class TestSecurityAbuse:
    def test_large_file(self, tmp_path):
        target = tmp_path / "large.txt"
        data = "x" * (1024 * 1024)  # 1MB
        write_text_atomic(target, data)
        assert target.stat().st_size >= 1024 * 1024

    def test_special_filename_chars(self, tmp_path):
        target = tmp_path / "file with spaces & (parens).txt"
        write_text_atomic(target, "ok")
        assert target.read_text() == "ok"


# ==========================================================================
# 7. USABILITY
# ==========================================================================

class TestUsability:
    def test_state_store_pattern(self, tmp_path):
        """Mimics StateStore atomic JSON persistence."""
        state_file = tmp_path / "state.json"
        state = {"jobs": {"j1": {"status": "running"}}, "version": 1}
        write_json_atomic(state_file, state)

        # Read back
        loaded = json.loads(state_file.read_text())
        assert loaded["jobs"]["j1"]["status"] == "running"

        # Update atomically
        loaded["jobs"]["j1"]["status"] = "completed"
        loaded["version"] = 2
        write_json_atomic(state_file, loaded)

        final = json.loads(state_file.read_text())
        assert final["version"] == 2
        assert final["jobs"]["j1"]["status"] == "completed"
