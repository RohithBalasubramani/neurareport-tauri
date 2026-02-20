"""Comprehensive tests for backend.app.utils.env_loader.

Coverage layers:
  1. Unit tests — parsing, quote stripping, comment handling, export prefix
  2. Integration tests — file search priority, candidate path ordering
  3. Property-based — random key=value lines never crash
  4. Failure injection — missing file, permission error, encoding error
  5. Concurrency — not applicable (startup-only, single-threaded)
  6. Security / abuse — path injection via NEURA_ENV_FILE, oversized files
  7. Usability — realistic .env file formats
"""
from __future__ import annotations

import os
import textwrap
import threading
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

from backend.app.utils.env_loader import (
    _apply_env_file,
    _iter_candidate_paths,
    _strip_quotes,
    load_env_file,
)


# ==========================================================================
# Helpers
# ==========================================================================

@pytest.fixture
def env_dir(tmp_path):
    """Return a temp directory for writing .env files."""
    return tmp_path


def _write_env(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def _clean_env():
    """Remove test keys from os.environ after each test."""
    marker_keys = set()
    orig = os.environ.copy()
    yield marker_keys
    for key in list(os.environ):
        if key not in orig:
            del os.environ[key]


# ==========================================================================
# 1. UNIT TESTS — _strip_quotes
# ==========================================================================

class TestStripQuotes:
    def test_double_quotes(self):
        assert _strip_quotes('"hello"') == "hello"

    def test_single_quotes(self):
        assert _strip_quotes("'hello'") == "hello"

    def test_no_quotes(self):
        assert _strip_quotes("hello") == "hello"

    def test_empty_string(self):
        assert _strip_quotes("") == ""

    def test_mismatched_quotes_left(self):
        assert _strip_quotes("\"hello'") == "\"hello'"

    def test_only_double_quotes(self):
        assert _strip_quotes('""') == ""

    def test_only_single_quotes(self):
        assert _strip_quotes("''") == ""

    def test_inner_quotes_preserved(self):
        assert _strip_quotes('"he\'llo"') == "he'llo"

    def test_whitespace_inside_quotes(self):
        assert _strip_quotes('"  spaced  "') == "  spaced  "


# ==========================================================================
# 2. UNIT TESTS — _apply_env_file
# ==========================================================================

class TestApplyEnvFile:
    """Test the core KEY=VALUE parsing logic."""

    def test_simple_key_value(self, env_dir):
        f = _write_env(env_dir / ".env", "FOO_TEST=bar\n")
        _apply_env_file(f)
        assert os.environ.get("FOO_TEST") == "bar"

    def test_comment_ignored(self, env_dir):
        f = _write_env(env_dir / ".env", "# comment\nKEY_COMMENT_TEST=val\n")
        _apply_env_file(f)
        assert os.environ.get("KEY_COMMENT_TEST") == "val"

    def test_empty_lines_ignored(self, env_dir):
        f = _write_env(env_dir / ".env", "\n\nEMPTY_LINE_TEST=yes\n\n")
        _apply_env_file(f)
        assert os.environ.get("EMPTY_LINE_TEST") == "yes"

    def test_export_prefix(self, env_dir):
        f = _write_env(env_dir / ".env", "export EXPORTED_TEST=123\n")
        _apply_env_file(f)
        assert os.environ.get("EXPORTED_TEST") == "123"

    def test_double_quoted_value(self, env_dir):
        f = _write_env(env_dir / ".env", 'DQ_TEST="quoted value"\n')
        _apply_env_file(f)
        assert os.environ.get("DQ_TEST") == "quoted value"

    def test_single_quoted_value(self, env_dir):
        f = _write_env(env_dir / ".env", "SQ_TEST='single quoted'\n")
        _apply_env_file(f)
        assert os.environ.get("SQ_TEST") == "single quoted"

    def test_value_with_equals(self, env_dir):
        f = _write_env(env_dir / ".env", "EQ_TEST=a=b=c\n")
        _apply_env_file(f)
        assert os.environ.get("EQ_TEST") == "a=b=c"

    def test_no_equals_line_skipped(self, env_dir):
        f = _write_env(env_dir / ".env", "no_equals_here\nVALID_TEST=yes\n")
        _apply_env_file(f)
        assert os.environ.get("VALID_TEST") == "yes"
        assert "no_equals_here" not in os.environ

    def test_key_starting_with_hash_skipped(self, env_dir):
        f = _write_env(env_dir / ".env", "#DISABLED=true\nENABLED_TEST=true\n")
        _apply_env_file(f)
        assert os.environ.get("ENABLED_TEST") == "true"
        assert "#DISABLED" not in os.environ

    def test_setdefault_does_not_override(self, env_dir):
        """Existing env vars are never overridden."""
        os.environ["PRE_EXISTING_TEST"] = "original"
        f = _write_env(env_dir / ".env", "PRE_EXISTING_TEST=overridden\n")
        _apply_env_file(f)
        assert os.environ["PRE_EXISTING_TEST"] == "original"

    def test_whitespace_around_key_value(self, env_dir):
        f = _write_env(env_dir / ".env", "  WS_KEY_TEST  =  ws_val  \n")
        _apply_env_file(f)
        assert os.environ.get("WS_KEY_TEST") == "ws_val"

    def test_empty_value(self, env_dir):
        f = _write_env(env_dir / ".env", "EMPTY_VAL_TEST=\n")
        _apply_env_file(f)
        assert os.environ.get("EMPTY_VAL_TEST") == ""


# ==========================================================================
# 3. INTEGRATION TESTS — load_env_file + candidate paths
# ==========================================================================

class TestIterCandidatePaths:
    """Candidate path ordering."""

    def test_neura_env_file_override_first(self):
        with patch.dict(os.environ, {"NEURA_ENV_FILE": "/custom/.env"}):
            paths = list(_iter_candidate_paths())
            assert paths[0] == Path("/custom/.env")

    def test_without_override_yields_two_paths(self):
        with patch.dict(os.environ, {}, clear=False):
            # Remove NEURA_ENV_FILE if set
            env = os.environ.copy()
            env.pop("NEURA_ENV_FILE", None)
            with patch.dict(os.environ, env, clear=True):
                paths = list(_iter_candidate_paths())
                assert len(paths) == 2
                # Both are .env files
                assert all(p.name == ".env" for p in paths)


class TestLoadEnvFile:
    """Integration: find and load the first existing .env file."""

    def test_loads_first_found(self, env_dir):
        env_file = _write_env(env_dir / ".env", "LOAD_TEST_FIRST=yes\n")
        with patch(
            "backend.app.utils.env_loader._iter_candidate_paths",
            return_value=iter([env_file]),
        ):
            result = load_env_file()
            assert result is not None
            assert result.name == ".env"
            assert os.environ.get("LOAD_TEST_FIRST") == "yes"

    def test_skips_missing_files(self, env_dir):
        missing = env_dir / "missing.env"
        present = _write_env(env_dir / ".env", "LOAD_TEST_SKIP=found\n")
        with patch(
            "backend.app.utils.env_loader._iter_candidate_paths",
            return_value=iter([missing, present]),
        ):
            result = load_env_file()
            assert result is not None
            assert os.environ.get("LOAD_TEST_SKIP") == "found"

    def test_returns_none_when_no_file_exists(self, env_dir):
        with patch(
            "backend.app.utils.env_loader._iter_candidate_paths",
            return_value=iter([env_dir / "nonexistent1", env_dir / "nonexistent2"]),
        ):
            result = load_env_file()
            assert result is None

    def test_stops_after_first_success(self, env_dir):
        first = _write_env(env_dir / "first.env", "FIRST_LOADED_TEST=1\n")
        second = _write_env(env_dir / "second.env", "SECOND_LOADED_TEST=2\n")
        with patch(
            "backend.app.utils.env_loader._iter_candidate_paths",
            return_value=iter([first, second]),
        ):
            load_env_file()
            assert os.environ.get("FIRST_LOADED_TEST") == "1"
            assert os.environ.get("SECOND_LOADED_TEST") is None


# ==========================================================================
# 4. PROPERTY-BASED / FUZZ TESTS
# ==========================================================================

class TestPropertyBased:
    @given(st.text(max_size=500))
    @settings(max_examples=200)
    def test_strip_quotes_never_crashes(self, s: str):
        result = _strip_quotes(s)
        assert isinstance(result, str)

    @given(
        st.lists(
            st.tuples(
                st.from_regex(r"[A-Z_][A-Z_0-9]{0,30}", fullmatch=True),
                st.text(alphabet="abcdefghijklmnop0123456789 _-./", max_size=100),
            ),
            max_size=50,
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_apply_env_never_crashes(self, pairs):
        import tempfile
        lines = [f"{k}={v}" for k, v in pairs]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("\n".join(lines))
            tmp_path = Path(tmp.name)
        before = set(os.environ.keys())
        try:
            _apply_env_file(tmp_path)
        finally:
            for key in set(os.environ.keys()) - before:
                del os.environ[key]
            tmp_path.unlink(missing_ok=True)


# ==========================================================================
# 5. FAILURE INJECTION TESTS
# ==========================================================================

class TestFailureInjection:
    def test_encoding_error_handled(self, env_dir):
        """Binary file doesn't crash load_env_file."""
        bad_file = env_dir / ".env"
        bad_file.write_bytes(b"\x80\x81\x82INVALID_UTF8=yes\n")
        with patch(
            "backend.app.utils.env_loader._iter_candidate_paths",
            return_value=iter([bad_file]),
        ):
            # Should not raise — either loads or logs and returns None
            result = load_env_file()
            # The file may or may not load depending on platform encoding
            # The key guarantee is: no crash

    def test_exception_during_load_logs_and_continues(self, env_dir, caplog):
        """If _apply_env_file raises, we log and try next candidate."""
        bad = env_dir / "bad.env"
        good = _write_env(env_dir / "good.env", "FALLBACK_TEST=yes\n")

        # Create a file that exists but causes _apply_env_file to raise
        bad.write_text("GOOD=line\n", encoding="utf-8")

        def raise_on_bad(path):
            if "bad" in str(path):
                raise PermissionError("No access")
            return _apply_env_file(path)

        with patch(
            "backend.app.utils.env_loader._iter_candidate_paths",
            return_value=iter([bad, good]),
        ), patch(
            "backend.app.utils.env_loader._apply_env_file",
            side_effect=raise_on_bad,
        ):
            result = load_env_file()
            assert result is not None
            assert os.environ.get("FALLBACK_TEST") == "yes"


# ==========================================================================
# 6. SECURITY / ABUSE TESTS
# ==========================================================================

class TestSecurityAbuse:
    def test_neura_env_file_path_traversal(self, env_dir):
        """NEURA_ENV_FILE with traversal chars — still resolves safely."""
        malicious = env_dir / ".." / ".." / ".env"
        # expanduser won't resolve traversal — that's fine, the file just won't exist
        with patch.dict(os.environ, {"NEURA_ENV_FILE": str(malicious)}):
            paths = list(_iter_candidate_paths())
            assert len(paths) >= 1
            # The first path contains the override
            assert paths[0] == Path(str(malicious)).expanduser()

    def test_large_env_file_processed(self, env_dir):
        """Large but valid .env file doesn't crash."""
        lines = [f"KEY_{i}_LARGE_TEST={i}" for i in range(1000)]
        f = _write_env(env_dir / ".env", "\n".join(lines) + "\n")
        before = set(os.environ.keys())
        try:
            _apply_env_file(f)
            # Spot-check a few
            assert os.environ.get("KEY_0_LARGE_TEST") == "0"
            assert os.environ.get("KEY_999_LARGE_TEST") == "999"
        finally:
            for key in set(os.environ.keys()) - before:
                del os.environ[key]

    def test_value_with_shell_expansion_chars(self, env_dir):
        """Shell metacharacters in values are stored literally (no expansion)."""
        f = _write_env(env_dir / ".env", "SHELL_TEST=$HOME/$(whoami)\n")
        _apply_env_file(f)
        assert os.environ.get("SHELL_TEST") == "$HOME/$(whoami)"


# ==========================================================================
# 7. USABILITY TESTS — Realistic .env file formats
# ==========================================================================

class TestUsability:
    def test_typical_env_file(self, env_dir):
        f = _write_env(env_dir / ".env", """\
        # Database configuration
        DATABASE_URL_USABILITY="postgresql://localhost:5432/neura"
        REDIS_URL_USABILITY='redis://localhost:6379/0'

        # API Keys
        export OPENAI_API_KEY_USABILITY=sk-test-123456
        ANTHROPIC_API_KEY_USABILITY=sk-ant-789

        # Feature flags
        DEBUG_USABILITY=false
        LOG_LEVEL_USABILITY=info
        """)
        _apply_env_file(f)
        assert os.environ.get("DATABASE_URL_USABILITY") == "postgresql://localhost:5432/neura"
        assert os.environ.get("REDIS_URL_USABILITY") == "redis://localhost:6379/0"
        assert os.environ.get("OPENAI_API_KEY_USABILITY") == "sk-test-123456"
        assert os.environ.get("DEBUG_USABILITY") == "false"

    def test_docker_compose_style(self, env_dir):
        """Values without quotes, common in docker-compose .env files."""
        f = _write_env(env_dir / ".env", """\
        POSTGRES_PASSWORD_DOCKER=mysecret
        POSTGRES_DB_DOCKER=neura
        POSTGRES_USER_DOCKER=admin
        """)
        _apply_env_file(f)
        assert os.environ.get("POSTGRES_PASSWORD_DOCKER") == "mysecret"
        assert os.environ.get("POSTGRES_DB_DOCKER") == "neura"

    def test_multiline_env_not_supported(self, env_dir):
        """Multiline values are NOT supported — each line is independent."""
        f = _write_env(env_dir / ".env", """\
        MULTI_LINE_TEST="line1
        line2"
        AFTER_MULTI_TEST=ok
        """)
        _apply_env_file(f)
        # The first line sets MULTI_LINE_TEST to "line1 (broken — expected)
        assert os.environ.get("AFTER_MULTI_TEST") == "ok"
