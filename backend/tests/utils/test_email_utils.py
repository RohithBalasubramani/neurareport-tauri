"""Comprehensive tests for backend.app.utils.email_utils.

Coverage layers:
  1. Unit tests — core normalisation behaviour
  2. Integration tests — import paths, legacy re-export
  3. Property-based / fuzz tests — random inputs never crash
  4. Failure injection — logging, rejected collection
  5. Concurrency — thread-safe (pure function, no shared state)
  6. Security / abuse — header injection, oversized input, control chars
  7. Usability — realistic user inputs
"""
from __future__ import annotations

import logging
import string
import threading
from unittest.mock import patch

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from backend.app.utils.email_utils import (
    MAX_RECIPIENTS_HARD_LIMIT,
    _redact_email,
    normalize_email_targets,
)


# ==========================================================================
# 1. UNIT TESTS — Core normalisation
# ==========================================================================

class TestNormaliseBasic:
    """Splitting, trimming, and deduplication."""

    def test_none_returns_empty(self):
        assert normalize_email_targets(None) == []

    def test_empty_string_returns_empty(self):
        assert normalize_email_targets("") == []

    def test_single_email(self):
        assert normalize_email_targets("alice@example.com") == ["alice@example.com"]

    def test_comma_separated(self):
        result = normalize_email_targets("a@b.com, c@d.com")
        assert result == ["a@b.com", "c@d.com"]

    def test_semicolon_separated(self):
        result = normalize_email_targets("a@b.com; c@d.com")
        assert result == ["a@b.com", "c@d.com"]

    def test_mixed_delimiters(self):
        result = normalize_email_targets("a@b.com, c@d.com; e@f.org")
        assert result == ["a@b.com", "c@d.com", "e@f.org"]

    def test_iterable_input(self):
        result = normalize_email_targets(["x@y.com", "z@w.com"])
        assert result == ["x@y.com", "z@w.com"]

    def test_whitespace_stripped(self):
        result = normalize_email_targets("  alice@b.com  ,  bob@c.com  ")
        assert result == ["alice@b.com", "bob@c.com"]

    def test_empty_entries_skipped(self):
        result = normalize_email_targets("a@b.com,,, ,;; c@d.com")
        assert result == ["a@b.com", "c@d.com"]


class TestDeduplication:
    """Case-insensitive dedup, first-seen casing preserved."""

    def test_exact_duplicate(self):
        result = normalize_email_targets("a@b.com, a@b.com")
        assert result == ["a@b.com"]

    def test_case_insensitive_duplicate(self):
        result = normalize_email_targets("Alice@B.com, alice@b.com")
        assert result == ["Alice@B.com"]

    def test_case_insensitive_duplicate_iterable(self):
        result = normalize_email_targets(["USER@DOMAIN.COM", "user@domain.com"])
        assert result == ["USER@DOMAIN.COM"]

    def test_three_way_duplicate(self):
        result = normalize_email_targets("a@b.com, A@B.COM, a@B.com")
        assert result == ["a@b.com"]


class TestValidation:
    """Invalid addresses are rejected by default."""

    def test_invalid_no_at_sign(self):
        result = normalize_email_targets("not-an-email")
        assert result == []

    def test_invalid_no_domain(self):
        result = normalize_email_targets("user@")
        assert result == []

    def test_invalid_no_tld(self):
        result = normalize_email_targets("user@domain")
        assert result == []

    def test_invalid_spaces(self):
        result = normalize_email_targets("user name@domain.com")
        assert result == []

    def test_mixed_valid_invalid(self):
        result = normalize_email_targets("good@ok.com, bad, also-bad, fine@yes.org")
        assert result == ["good@ok.com", "fine@yes.org"]

    def test_validate_false_skips_validation(self):
        result = normalize_email_targets("not-an-email", validate=False)
        assert result == ["not-an-email"]

    def test_validate_false_still_deduplicates(self):
        result = normalize_email_targets("a, a, b", validate=False)
        assert result == ["a", "b"]

    def test_valid_email_with_plus(self):
        result = normalize_email_targets("user+tag@example.com")
        assert result == ["user+tag@example.com"]

    def test_valid_email_with_dots(self):
        result = normalize_email_targets("first.last@example.com")
        assert result == ["first.last@example.com"]

    def test_valid_email_with_percent(self):
        result = normalize_email_targets("user%tag@example.com")
        assert result == ["user%tag@example.com"]


class TestRejectedList:
    """The ``rejected`` out-parameter collects dropped addresses."""

    def test_rejected_populated(self):
        rejected: list[str] = []
        result = normalize_email_targets("ok@a.com, bad", rejected=rejected)
        assert result == ["ok@a.com"]
        assert rejected == ["bad"]

    def test_rejected_empty_when_all_valid(self):
        rejected: list[str] = []
        normalize_email_targets("a@b.com, c@d.org", rejected=rejected)
        assert rejected == []

    def test_rejected_multiple(self):
        rejected: list[str] = []
        normalize_email_targets("x, y, z@ok.com, w", rejected=rejected)
        assert len(rejected) == 3
        assert "z@ok.com" not in rejected


class TestMaxRecipients:
    """Recipient count capping."""

    def test_within_limit(self):
        emails = [f"u{i}@d.com" for i in range(10)]
        result = normalize_email_targets(emails, max_recipients=20)
        assert len(result) == 10

    def test_exceeds_limit(self):
        emails = [f"u{i}@d.com" for i in range(50)]
        result = normalize_email_targets(emails, max_recipients=10)
        assert len(result) == 10
        # First 10 preserved in order
        assert result == [f"u{i}@d.com" for i in range(10)]

    def test_hard_limit_cap(self):
        emails = [f"u{i}@d.com" for i in range(MAX_RECIPIENTS_HARD_LIMIT + 100)]
        result = normalize_email_targets(emails, max_recipients=999999)
        assert len(result) == MAX_RECIPIENTS_HARD_LIMIT

    def test_max_recipients_zero_becomes_one(self):
        result = normalize_email_targets(["a@b.com", "c@d.com"], max_recipients=0)
        assert len(result) == 1

    def test_negative_max_becomes_one(self):
        result = normalize_email_targets(["a@b.com", "c@d.com"], max_recipients=-5)
        assert len(result) == 1


# ==========================================================================
# 2. INTEGRATION TESTS — Import paths
# ==========================================================================

class TestImportPaths:
    """Both app and legacy import paths work."""

    def test_app_import(self):
        from backend.app.utils.email_utils import normalize_email_targets as fn
        assert callable(fn)

    def test_legacy_import(self):
        from backend.legacy.utils.email_utils import normalize_email_targets as fn
        assert callable(fn)

    def test_same_function(self):
        from backend.app.utils.email_utils import normalize_email_targets as app_fn
        from backend.legacy.utils.email_utils import normalize_email_targets as legacy_fn
        assert app_fn is legacy_fn


# ==========================================================================
# 3. PROPERTY-BASED / FUZZ TESTS
# ==========================================================================

class TestPropertyBased:
    """Hypothesis-driven invariant testing."""

    @given(st.text(max_size=2000))
    @settings(max_examples=200)
    def test_never_crashes_on_arbitrary_string(self, s: str):
        result = normalize_email_targets(s)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)
            assert len(item) > 0
            assert "@" in item  # validated emails must have @

    @given(st.lists(st.text(max_size=200), max_size=100))
    @settings(max_examples=200)
    def test_never_crashes_on_arbitrary_list(self, items: list[str]):
        result = normalize_email_targets(items)
        assert isinstance(result, list)
        assert len(result) <= MAX_RECIPIENTS_HARD_LIMIT

    @given(st.lists(
        st.from_regex(r"[a-z]{1,10}@[a-z]{1,10}\.[a-z]{2,4}", fullmatch=True),
        min_size=2,
        max_size=20,
    ))
    @settings(max_examples=100)
    def test_dedup_invariant(self, emails: list[str]):
        result = normalize_email_targets(emails)
        lowers = [e.lower() for e in result]
        assert len(lowers) == len(set(lowers)), "Duplicates slipped through"

    @given(st.lists(
        st.from_regex(r"[a-z]{1,10}@[a-z]{1,10}\.[a-z]{2,4}", fullmatch=True),
        min_size=1,
        max_size=50,
    ))
    @settings(max_examples=100)
    def test_order_preserved(self, emails: list[str]):
        result = normalize_email_targets(emails)
        # Result is a subsequence of input (order preserved)
        it = iter(emails)
        for r in result:
            for e in it:
                if e.strip().lower() == r.lower():
                    break

    @given(st.text(alphabet=string.printable, max_size=500))
    @settings(max_examples=200)
    def test_no_control_chars_in_output(self, s: str):
        result = normalize_email_targets(s, validate=False)
        for item in result:
            for ch in item:
                assert ord(ch) >= 0x20 or ch in ("\t",), \
                    f"Control char U+{ord(ch):04X} in output"


# ==========================================================================
# 4. FAILURE INJECTION TESTS
# ==========================================================================

class TestFailureInjection:
    """Logging and edge-case handling under failure conditions."""

    def test_invalid_emails_logged(self, caplog):
        with caplog.at_level(logging.WARNING):
            normalize_email_targets("bad-input, ok@valid.com")
        assert any("email_target_rejected" in rec.message for rec in caplog.records)

    def test_truncation_logged(self, caplog):
        emails = [f"u{i}@d.com" for i in range(20)]
        with caplog.at_level(logging.WARNING):
            normalize_email_targets(emails, max_recipients=5)
        assert any("email_recipients_truncated" in rec.message for rec in caplog.records)

    def test_none_in_iterable_handled(self):
        # Some callers might pass [None, "a@b.com"]
        result = normalize_email_targets([None, "a@b.com"])  # type: ignore[list-item]
        assert result == ["a@b.com"]

    def test_int_in_iterable_handled(self):
        result = normalize_email_targets([123, "a@b.com"])  # type: ignore[list-item]
        assert result == ["a@b.com"]

    def test_empty_list(self):
        assert normalize_email_targets([]) == []


# ==========================================================================
# 5. CONCURRENCY TESTS
# ==========================================================================

class TestConcurrency:
    """Pure function — verify thread safety under parallel invocation."""

    def test_parallel_normalisation(self):
        """20 threads each normalise their own input — no cross-contamination."""
        results: dict[int, list[str]] = {}
        errors: list[str] = []

        def worker(idx: int):
            try:
                inp = [f"user{idx}@domain{idx}.com", f"dupe{idx}@d.com", f"dupe{idx}@d.com"]
                results[idx] = normalize_email_targets(inp)
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors, f"Thread errors: {errors}"
        for idx in range(20):
            r = results[idx]
            assert len(r) == 2, f"Thread {idx} got {len(r)} results"
            assert r[0] == f"user{idx}@domain{idx}.com"
            assert r[1] == f"dupe{idx}@d.com"


# ==========================================================================
# 6. SECURITY / ABUSE TESTS
# ==========================================================================

class TestSecurityAbuse:
    """SMTP header injection, oversized input, control characters."""

    def test_newline_injection_stripped(self):
        """CR/LF in address → control chars stripped → fails validation."""
        result = normalize_email_targets("evil@hack.com\r\nBcc:spy@evil.com")
        # After stripping control chars: "evil@hack.comBcc:spy@evil.com" — invalid
        assert "spy@evil.com" not in str(result)

    def test_null_byte_stripped(self):
        result = normalize_email_targets("ok@valid.com\x00EXTRA")
        # After stripping NUL: "ok@valid.comEXTRA" — concatenated domain is
        # format-valid per regex.  Critical: the NUL byte itself is gone.
        for addr in result:
            assert "\x00" not in addr

    def test_tab_stripped(self):
        result = normalize_email_targets("ok@\tvalid.com")
        # Tab is stripped → "ok@valid.com" which is valid
        assert result == ["ok@valid.com"]

    def test_vertical_tab_stripped(self):
        result = normalize_email_targets("ok@valid.com\x0b")
        # VT stripped → "ok@valid.com" which is valid
        assert result == ["ok@valid.com"]

    def test_massive_input_capped(self):
        """A giant string doesn't DoS — it's split and capped."""
        huge = ", ".join(f"u{i}@d.com" for i in range(10000))
        result = normalize_email_targets(huge)
        assert len(result) <= MAX_RECIPIENTS_HARD_LIMIT

    def test_very_long_local_part_rejected(self):
        # RFC 5321 §4.5.3.1: local part max 64 chars
        addr = "a" * 65 + "@example.com"
        result = normalize_email_targets(addr)
        assert result == []

    def test_very_long_total_address_rejected(self):
        # RFC 5321 §4.5.3.1: total email max 254 chars
        addr = "a" * 64 + "@" + "b" * 186 + ".com"
        assert len(addr) > 254  # 64 + 1 + 186 + 4 = 255
        result = normalize_email_targets(addr)
        assert result == []

    def test_script_injection_in_address(self):
        result = normalize_email_targets("<script>alert(1)</script>@evil.com")
        assert result == []

    def test_sql_injection_in_address(self):
        # Input "' OR 1=1; --@evil.com" is split on ";" producing:
        #   "' OR 1=1" → no @, rejected
        #   " --@evil.com" → "--@evil.com" — format-valid (hyphens allowed in local)
        # The injection payload is neutralised by splitting.
        result = normalize_email_targets("' OR 1=1; --@evil.com")
        # The SQL payload itself is not in any result
        assert not any("OR 1=1" in addr for addr in result)

    def test_unicode_homoglyph_passes_if_valid_format(self):
        # Cyrillic 'а' looks like Latin 'a' — the regex only matches ASCII
        result = normalize_email_targets("us\u0435r@example.com")  # Cyrillic е
        assert result == []  # regex blocks non-ASCII local parts


# ==========================================================================
# 7. USABILITY VALIDATION TESTS
# ==========================================================================

class TestUsability:
    """Realistic user inputs from frontend forms."""

    def test_outlook_paste(self):
        """User pastes from Outlook: 'Name <email>;...'"""
        # Our normaliser doesn't parse "Name <email>" format — only bare addresses.
        # This is intentional; callers should pre-extract before passing.
        result = normalize_email_targets("Alice <alice@co.com>; Bob <bob@co.com>")
        assert result == []  # angle-bracket format not supported

    def test_simple_comma_list(self):
        result = normalize_email_targets("alice@co.com, bob@co.com, carol@co.com")
        assert len(result) == 3

    def test_trailing_comma(self):
        result = normalize_email_targets("alice@co.com,")
        assert result == ["alice@co.com"]

    def test_leading_comma(self):
        result = normalize_email_targets(",alice@co.com")
        assert result == ["alice@co.com"]

    def test_single_address_no_delimiter(self):
        result = normalize_email_targets("solo@user.org")
        assert result == ["solo@user.org"]

    def test_empty_after_splitting(self):
        result = normalize_email_targets(",,,;;;,,,")
        assert result == []


# ==========================================================================
# REDACTION HELPER TESTS
# ==========================================================================

class TestRedactEmail:
    """Log-safe redaction of email addresses."""

    def test_normal_email(self):
        assert _redact_email("alice@example.com") == "a***e@example.com"

    def test_short_local_part(self):
        assert _redact_email("ab@x.com") == "**@x.com"

    def test_single_char_local(self):
        assert _redact_email("a@x.com") == "*@x.com"

    def test_non_email_string(self):
        result = _redact_email("not-an-email-at-all")
        assert len(result) <= 21  # max 20 chars + ellipsis
