"""Comprehensive tests for backend.app.utils.validation module.

Test layers:
1. Unit tests          -- each function individually with valid/invalid inputs
2. Integration tests   -- Validator chain with complex compositions
3. Property-based      -- Hypothesis strategies for invariants
4. Failure injection   -- None, empty strings, wrong types
5. Concurrency         -- Validator is not shared-state
6. Security/abuse      -- SQL injection, XSS, path traversal, SSRF, long strings
7. Usability           -- realistic validation scenarios
"""
from __future__ import annotations

import copy
import threading
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch, MagicMock

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from backend.app.utils.validation import (
    DANGEROUS_PATH_PATTERNS,
    EMAIL_PATTERN,
    SAFE_FILENAME_PATTERN,
    SAFE_ID_PATTERN,
    SAFE_NAME_PATTERN,
    SLUG_PATTERN,
    SQL_INJECTION_PATTERNS,
    UUID_PATTERN,
    XSS_PATTERNS,
    ValidationResult,
    Validator,
    contains_sql_injection,
    contains_xss,
    generate_safe_id,
    is_read_only_sql,
    is_safe_external_url,
    is_safe_filename,
    is_safe_id,
    is_safe_name,
    is_valid_email,
    is_valid_slug,
    is_valid_url,
    is_valid_uuid,
    normalize_string,
    sanitize_filename,
    sanitize_html,
    sanitize_id,
    sanitize_sql_identifier,
    truncate_string,
    validate_date_string,
    validate_field_type,
    validate_file_extension,
    validate_json_string_length,
    validate_numeric_range,
    validate_path_safety,
    validate_required_fields,
)


# =====================================================================
# Layer 1 -- Unit Tests
# =====================================================================


class TestIsSafeId:
    """Unit tests for is_safe_id."""

    def test_valid_simple_id(self):
        assert is_safe_id("abc123") is True

    def test_valid_with_dashes_underscores(self):
        assert is_safe_id("my-id_01") is True

    def test_single_char(self):
        assert is_safe_id("a") is True

    def test_max_length_63(self):
        assert is_safe_id("a" * 63) is True

    def test_too_long_64_chars(self):
        assert is_safe_id("a" * 64) is False

    def test_starts_with_dash(self):
        assert is_safe_id("-abc") is False

    def test_starts_with_underscore(self):
        assert is_safe_id("_abc") is False

    def test_empty_string(self):
        assert is_safe_id("") is False

    def test_special_chars(self):
        assert is_safe_id("abc!@#") is False

    def test_spaces(self):
        assert is_safe_id("a b c") is False

    def test_none_input(self):
        assert is_safe_id(None) is False

    def test_numeric_start(self):
        assert is_safe_id("9abc") is True


class TestIsSafeName:
    """Unit tests for is_safe_name."""

    def test_valid_simple_name(self):
        assert is_safe_name("John Doe") is True

    def test_valid_with_special(self):
        assert is_safe_name("Project (v1.0)") is True

    def test_valid_with_dash(self):
        assert is_safe_name("my-project") is True

    def test_unicode_chars(self):
        # \w with re.UNICODE matches unicode word characters like accented letters
        assert is_safe_name("caf\u00e9") is True  # pre-composed e-acute

    def test_too_long_101_chars(self):
        assert is_safe_name("a" * 101) is False

    def test_exactly_100_chars(self):
        assert is_safe_name("a" * 100) is True

    def test_empty_string(self):
        assert is_safe_name("") is False

    def test_none_input(self):
        assert is_safe_name(None) is False

    def test_angle_brackets(self):
        assert is_safe_name("<script>") is False


class TestIsSafeFilename:
    """Unit tests for is_safe_filename."""

    def test_valid_filename(self):
        assert is_safe_filename("report.pdf") is True

    def test_valid_with_parens(self):
        assert is_safe_filename("report(1).pdf") is True

    def test_double_dot_traversal(self):
        assert is_safe_filename("..") is False

    def test_path_with_traversal(self):
        assert is_safe_filename("../etc/passwd") is False

    def test_null_byte(self):
        assert is_safe_filename("file\x00.txt") is False

    def test_empty_string(self):
        assert is_safe_filename("") is False

    def test_none_input(self):
        assert is_safe_filename(None) is False

    def test_tilde(self):
        assert is_safe_filename("~root") is False

    def test_dollar_sign(self):
        assert is_safe_filename("$HOME") is False

    def test_percent_sign(self):
        assert is_safe_filename("%USERPROFILE%") is False


class TestSanitizeId:
    """Unit tests for sanitize_id."""

    def test_strips_special_chars(self):
        assert sanitize_id("abc!@#def") == "abcdef"

    def test_keeps_dashes_underscores(self):
        assert sanitize_id("a-b_c") == "a-b_c"

    def test_ensures_alnum_start(self):
        assert sanitize_id("---abc") == "abc"

    def test_truncates_to_63(self):
        result = sanitize_id("a" * 100)
        assert len(result) == 63

    def test_empty_returns_empty(self):
        assert sanitize_id("") == ""

    def test_none_returns_empty(self):
        assert sanitize_id(None) == ""

    def test_all_special_chars(self):
        assert sanitize_id("!@#$%") == ""


class TestSanitizeFilename:
    """Unit tests for sanitize_filename."""

    def test_removes_path_separators(self):
        result = sanitize_filename("dir/file.txt")
        assert "/" not in result
        assert "\\" not in result

    def test_removes_double_dot(self):
        result = sanitize_filename("../file.txt")
        assert ".." not in result

    def test_empty_returns_empty(self):
        # Note: source says empty returns ""
        assert sanitize_filename("") == ""

    def test_none_returns_empty(self):
        assert sanitize_filename(None) == ""

    def test_all_dangerous_returns_unnamed(self):
        # All chars stripped leads to empty, returns "unnamed"
        assert sanitize_filename("..") == "unnamed"

    def test_truncates_to_255(self):
        result = sanitize_filename("a" * 300)
        assert len(result) == 255

    def test_strips_leading_dots(self):
        result = sanitize_filename(".hidden")
        assert not result.startswith(".")

    def test_strips_leading_spaces(self):
        result = sanitize_filename("  file.txt")
        assert not result.startswith(" ")

    def test_removes_windows_special_chars(self):
        result = sanitize_filename('file<name>:test?"star*|pipe')
        for ch in '<>:?"*|':
            assert ch not in result


class TestValidatePathSafety:
    """Unit tests for validate_path_safety."""

    def test_safe_relative_path(self):
        safe, err = validate_path_safety("data/reports/file.txt")
        assert safe is True
        assert err is None

    def test_traversal_blocked(self):
        safe, err = validate_path_safety("../etc/passwd")
        assert safe is False
        assert err is not None

    def test_absolute_unix_blocked(self):
        safe, err = validate_path_safety("/etc/passwd")
        assert safe is False

    def test_absolute_windows_blocked(self):
        safe, err = validate_path_safety("C:\\Windows\\System32")
        assert safe is False

    def test_null_byte_blocked(self):
        safe, err = validate_path_safety("file\x00.txt")
        assert safe is False

    def test_tilde_blocked(self):
        safe, err = validate_path_safety("~/secret")
        assert safe is False

    def test_env_var_unix_blocked(self):
        safe, err = validate_path_safety("$HOME/secret")
        assert safe is False

    def test_env_var_windows_blocked(self):
        safe, err = validate_path_safety("%APPDATA%/secret")
        assert safe is False

    def test_accepts_path_object(self):
        # Path objects should work too (converted to str)
        safe, err = validate_path_safety(Path("data") / "file.txt")
        assert safe is True


class TestValidateFileExtension:
    """Unit tests for validate_file_extension."""

    def test_valid_extension(self):
        valid, err = validate_file_extension("report.pdf", [".pdf", ".docx"])
        assert valid is True
        assert err is None

    def test_invalid_extension(self):
        valid, err = validate_file_extension("script.exe", [".pdf", ".docx"])
        assert valid is False
        assert "Invalid file type" in err

    def test_no_extension(self):
        valid, err = validate_file_extension("README", [".txt"])
        assert valid is False
        assert "must have an extension" in err

    def test_extension_normalization_without_dot(self):
        valid, err = validate_file_extension("report.pdf", ["pdf", "docx"])
        assert valid is True

    def test_extension_normalization_with_dot(self):
        valid, err = validate_file_extension("report.pdf", [".pdf"])
        assert valid is True

    def test_case_insensitive(self):
        valid, err = validate_file_extension("photo.JPG", [".jpg", ".png"])
        assert valid is True

    def test_empty_filename(self):
        valid, err = validate_file_extension("", [".txt"])
        assert valid is False


class TestSanitizeSqlIdentifier:
    """Unit tests for sanitize_sql_identifier."""

    def test_keeps_alnum_underscore(self):
        assert sanitize_sql_identifier("users_table") == "users_table"

    def test_strips_special_chars(self):
        assert sanitize_sql_identifier("users; DROP TABLE--") == "usersDROPTABLE"

    def test_truncates_to_128(self):
        result = sanitize_sql_identifier("a" * 200)
        assert len(result) == 128

    def test_empty_returns_empty(self):
        assert sanitize_sql_identifier("") == ""

    def test_none_returns_empty(self):
        assert sanitize_sql_identifier(None) == ""


class TestValidateJsonStringLength:
    """Unit tests for validate_json_string_length."""

    def test_within_limit(self):
        valid, err = validate_json_string_length("hello", 100)
        assert valid is True

    def test_exceeds_limit(self):
        valid, err = validate_json_string_length("a" * 101, 100)
        assert valid is False
        assert "too long" in err

    def test_empty_is_valid(self):
        valid, err = validate_json_string_length("", 100)
        assert valid is True

    def test_none_is_valid(self):
        valid, err = validate_json_string_length(None, 100)
        assert valid is True

    def test_default_limit(self):
        valid, _ = validate_json_string_length("a" * 10001)
        assert valid is False


class TestIsValidEmail:
    """Unit tests for is_valid_email."""

    def test_valid_email(self):
        assert is_valid_email("user@example.com") is True

    def test_valid_with_plus(self):
        assert is_valid_email("user+tag@example.com") is True

    def test_no_at_sign(self):
        assert is_valid_email("userexample.com") is False

    def test_no_domain(self):
        assert is_valid_email("user@") is False

    def test_spaces(self):
        assert is_valid_email("user @example.com") is False

    def test_empty(self):
        assert is_valid_email("") is False

    def test_none(self):
        assert is_valid_email(None) is False

    def test_valid_subdomain(self):
        assert is_valid_email("user@mail.example.com") is True


class TestIsValidUuid:
    """Unit tests for is_valid_uuid."""

    def test_valid_lowercase(self):
        assert is_valid_uuid("550e8400-e29b-41d4-a716-446655440000") is True

    def test_valid_uppercase(self):
        assert is_valid_uuid("550E8400-E29B-41D4-A716-446655440000") is True

    def test_invalid_format(self):
        assert is_valid_uuid("not-a-uuid") is False

    def test_empty(self):
        assert is_valid_uuid("") is False

    def test_none(self):
        assert is_valid_uuid(None) is False

    def test_no_dashes(self):
        assert is_valid_uuid("550e8400e29b41d4a716446655440000") is False


class TestIsValidSlug:
    """Unit tests for is_valid_slug."""

    def test_valid_slug(self):
        assert is_valid_slug("my-project-name") is True

    def test_valid_no_hyphens(self):
        assert is_valid_slug("myproject") is True

    def test_uppercase_invalid(self):
        assert is_valid_slug("My-Project") is False

    def test_spaces_invalid(self):
        assert is_valid_slug("my project") is False

    def test_empty(self):
        assert is_valid_slug("") is False

    def test_none(self):
        assert is_valid_slug(None) is False

    def test_trailing_hyphen(self):
        assert is_valid_slug("my-project-") is False

    def test_leading_hyphen(self):
        assert is_valid_slug("-my-project") is False

    def test_consecutive_hyphens(self):
        assert is_valid_slug("my--project") is False


class TestIsValidUrl:
    """Unit tests for is_valid_url."""

    def test_valid_http(self):
        assert is_valid_url("http://example.com") is True

    def test_valid_https(self):
        assert is_valid_url("https://example.com") is True

    def test_ftp_invalid(self):
        assert is_valid_url("ftp://example.com") is False

    def test_require_https_with_http(self):
        assert is_valid_url("http://example.com", require_https=True) is False

    def test_require_https_with_https(self):
        assert is_valid_url("https://example.com", require_https=True) is True

    def test_no_scheme(self):
        assert is_valid_url("example.com") is False

    def test_empty(self):
        assert is_valid_url("") is False

    def test_none(self):
        assert is_valid_url(None) is False

    def test_with_path(self):
        assert is_valid_url("https://example.com/path/to/resource") is True


class TestContainsSqlInjection:
    """Unit tests for contains_sql_injection."""

    def test_semicolon_drop(self):
        assert contains_sql_injection("; DROP TABLE users") is True

    def test_semicolon_delete(self):
        assert contains_sql_injection("; DELETE FROM users") is True

    def test_union_select(self):
        assert contains_sql_injection("UNION SELECT * FROM passwords") is True

    def test_or_1_equals_1(self):
        assert contains_sql_injection("OR 1=1") is True

    def test_tautology_quotes(self):
        assert contains_sql_injection("' OR '") is True

    def test_semicolon_comment(self):
        assert contains_sql_injection("; --") is True

    def test_safe_string(self):
        assert contains_sql_injection("Hello World") is False

    def test_empty(self):
        assert contains_sql_injection("") is False

    def test_none(self):
        assert contains_sql_injection(None) is False


class TestIsReadOnlySql:
    """Unit tests for is_read_only_sql."""

    def test_select_ok(self):
        ok, err = is_read_only_sql("SELECT * FROM users")
        assert ok is True

    def test_with_ok(self):
        ok, err = is_read_only_sql("WITH cte AS (SELECT 1) SELECT * FROM cte")
        assert ok is True

    def test_insert_blocked(self):
        ok, err = is_read_only_sql("INSERT INTO users VALUES (1)")
        assert ok is False

    def test_drop_blocked(self):
        ok, err = is_read_only_sql("DROP TABLE users")
        assert ok is False

    def test_update_blocked(self):
        ok, err = is_read_only_sql("UPDATE users SET name='x'")
        assert ok is False

    def test_delete_blocked(self):
        ok, err = is_read_only_sql("DELETE FROM users")
        assert ok is False

    def test_empty_query(self):
        ok, err = is_read_only_sql("")
        assert ok is False
        assert "empty" in err.lower()

    def test_whitespace_only(self):
        ok, err = is_read_only_sql("   ")
        assert ok is False

    def test_select_with_hidden_insert(self):
        ok, err = is_read_only_sql("SELECT 1; INSERT INTO users VALUES(1)")
        assert ok is False

    def test_comments_stripped(self):
        ok, err = is_read_only_sql("-- comment\nSELECT 1")
        assert ok is True

    def test_block_comment_stripped(self):
        ok, err = is_read_only_sql("/* comment */ SELECT 1")
        assert ok is True

    def test_only_comments(self):
        ok, err = is_read_only_sql("-- this is just a comment")
        assert ok is False


class TestContainsXss:
    """Unit tests for contains_xss."""

    def test_script_tag(self):
        assert contains_xss("<script>alert(1)</script>") is True

    def test_event_handler(self):
        assert contains_xss('<img onerror="alert(1)">') is True

    def test_javascript_url(self):
        assert contains_xss("javascript:alert(1)") is True

    def test_iframe(self):
        assert contains_xss("<iframe src='evil'>") is True

    def test_object_tag(self):
        assert contains_xss("<object data='evil'>") is True

    def test_embed_tag(self):
        assert contains_xss("<embed src='evil'>") is True

    def test_safe_string(self):
        assert contains_xss("Hello, world!") is False

    def test_empty(self):
        assert contains_xss("") is False

    def test_none(self):
        assert contains_xss(None) is False


class TestSanitizeHtml:
    """Unit tests for sanitize_html."""

    def test_removes_script_tags(self):
        result = sanitize_html("<p>Hello</p><script>alert(1)</script>")
        assert "<script" not in result
        assert "alert" not in result
        assert "<p>Hello</p>" in result

    def test_removes_event_handlers(self):
        result = sanitize_html('<img src="x" onerror="alert(1)">')
        assert "onerror" not in result

    def test_removes_javascript_url(self):
        result = sanitize_html('<a href="javascript:alert(1)">click</a>')
        assert "javascript:" not in result

    def test_empty(self):
        assert sanitize_html("") == ""

    def test_none(self):
        assert sanitize_html(None) == ""

    def test_preserves_safe_html(self):
        result = sanitize_html("<p>Hello <b>World</b></p>")
        assert "<p>Hello <b>World</b></p>" == result


class TestNormalizeString:
    """Unit tests for normalize_string."""

    def test_nfc_normalization(self):
        # e + combining acute accent -> NFC form
        combined = "e\u0301"
        result = normalize_string(combined)
        assert result == unicodedata.normalize("NFC", combined)

    def test_control_chars_stripped(self):
        result = normalize_string("hello\x00world\x01!")
        assert "\x00" not in result
        assert "\x01" not in result

    def test_newline_preserved(self):
        result = normalize_string("hello\nworld")
        assert "\n" in result

    def test_tab_preserved(self):
        result = normalize_string("hello\tworld")
        assert "\t" in result

    def test_empty(self):
        assert normalize_string("") == ""

    def test_none(self):
        assert normalize_string(None) == ""

    def test_strips_whitespace(self):
        result = normalize_string("  hello  ")
        assert result == "hello"


class TestValidateNumericRange:
    """Unit tests for validate_numeric_range."""

    def test_within_range(self):
        ok, err = validate_numeric_range(5, min_value=1, max_value=10)
        assert ok is True
        assert err is None

    def test_below_min(self):
        ok, err = validate_numeric_range(0, min_value=1)
        assert ok is False
        assert "at least" in err

    def test_above_max(self):
        ok, err = validate_numeric_range(100, max_value=50)
        assert ok is False
        assert "at most" in err

    def test_no_bounds(self):
        ok, err = validate_numeric_range(9999)
        assert ok is True

    def test_float_within_range(self):
        ok, err = validate_numeric_range(3.14, min_value=0.0, max_value=10.0)
        assert ok is True

    def test_at_boundary(self):
        ok, err = validate_numeric_range(10, min_value=10, max_value=10)
        assert ok is True


class TestValidateDateString:
    """Unit tests for validate_date_string."""

    def test_iso_format(self):
        ok, parsed = validate_date_string("2024-01-15")
        assert ok is True
        assert isinstance(parsed, datetime)

    def test_slash_format(self):
        ok, parsed = validate_date_string("2024/01/15")
        assert ok is True

    def test_datetime_format(self):
        ok, parsed = validate_date_string("2024-01-15T10:30:00")
        assert ok is True

    def test_invalid_date(self):
        ok, parsed = validate_date_string("not-a-date")
        assert ok is False
        assert parsed is None

    def test_empty(self):
        ok, parsed = validate_date_string("")
        assert ok is False

    def test_none(self):
        ok, parsed = validate_date_string(None)
        assert ok is False

    def test_custom_format(self):
        ok, parsed = validate_date_string("15-Jan-2024", formats=["%d-%b-%Y"])
        assert ok is True


class TestValidateRequiredFields:
    """Unit tests for validate_required_fields."""

    def test_all_present(self):
        data = {"name": "Alice", "email": "alice@example.com"}
        ok, missing = validate_required_fields(data, ["name", "email"])
        assert ok is True
        assert missing == []

    def test_missing_fields(self):
        data = {"name": "Alice"}
        ok, missing = validate_required_fields(data, ["name", "email"])
        assert ok is False
        assert "email" in missing

    def test_empty_string_counts_as_missing(self):
        data = {"name": "  ", "email": "a@b.com"}
        ok, missing = validate_required_fields(data, ["name", "email"])
        assert ok is False
        assert "name" in missing

    def test_none_value_counts_as_missing(self):
        data = {"name": None}
        ok, missing = validate_required_fields(data, ["name"])
        assert ok is False
        assert "name" in missing


class TestValidateFieldType:
    """Unit tests for validate_field_type."""

    def test_correct_type(self):
        ok, err = validate_field_type("hello", str)
        assert ok is True
        assert err is None

    def test_wrong_type(self):
        ok, err = validate_field_type(123, str)
        assert ok is False
        assert "str" in err

    def test_int_type(self):
        ok, err = validate_field_type(42, int)
        assert ok is True

    def test_dict_type(self):
        ok, err = validate_field_type({}, dict)
        assert ok is True


class TestTruncateString:
    """Unit tests for truncate_string."""

    def test_short_no_truncation(self):
        assert truncate_string("hello", 10) == "hello"

    def test_long_truncated_with_suffix(self):
        result = truncate_string("hello world", 8)
        assert result == "hello..."
        assert len(result) == 8

    def test_exact_length_no_truncation(self):
        assert truncate_string("12345", 5) == "12345"

    def test_custom_suffix(self):
        result = truncate_string("hello world", 9, suffix="~~")
        assert result.endswith("~~")
        assert len(result) == 9

    def test_empty(self):
        assert truncate_string("", 10) == ""

    def test_none(self):
        assert truncate_string(None, 10) is None


class TestGenerateSafeId:
    """Unit tests for generate_safe_id."""

    def test_spaces_to_hyphens(self):
        result = generate_safe_id("Hello World")
        assert "-" in result or result == "hello-world"

    def test_special_chars_removed(self):
        result = generate_safe_id("Hello! World@123")
        assert "!" not in result
        assert "@" not in result

    def test_lowercase(self):
        result = generate_safe_id("HELLO")
        assert result == result.lower()

    def test_max_length(self):
        result = generate_safe_id("a" * 100, max_length=20)
        assert len(result) <= 20

    def test_empty(self):
        assert generate_safe_id("") == ""

    def test_none(self):
        assert generate_safe_id(None) == ""

    def test_leading_hyphens_stripped(self):
        result = generate_safe_id("---hello")
        assert not result.startswith("-")


class TestValidationResult:
    """Unit tests for ValidationResult dataclass."""

    def test_success(self):
        r = ValidationResult.success("data")
        assert r.valid is True
        assert r.value == "data"
        assert r.error is None

    def test_failure(self):
        r = ValidationResult.failure("bad input", field="email")
        assert r.valid is False
        assert r.error == "bad input"
        assert r.field == "email"

    def test_success_no_value(self):
        r = ValidationResult.success()
        assert r.valid is True
        assert r.value is None

    def test_failure_no_field(self):
        r = ValidationResult.failure("error")
        assert r.field is None


class TestValidatorChain:
    """Unit tests for Validator chain class."""

    def test_required_valid(self):
        result = Validator("hello").required().validate()
        assert result.valid is True

    def test_required_none(self):
        result = Validator(None).required().validate()
        assert result.valid is False

    def test_required_empty_string(self):
        result = Validator("  ").required().validate()
        assert result.valid is False

    def test_min_length_valid(self):
        result = Validator("hello").min_length(3).validate()
        assert result.valid is True

    def test_min_length_invalid(self):
        result = Validator("ab").min_length(3).validate()
        assert result.valid is False

    def test_max_length_valid(self):
        result = Validator("hello").max_length(10).validate()
        assert result.valid is True

    def test_max_length_invalid(self):
        result = Validator("hello world").max_length(5).validate()
        assert result.valid is False

    def test_pattern_valid(self):
        result = Validator("abc123").pattern(r"^[a-z0-9]+$").validate()
        assert result.valid is True

    def test_pattern_invalid(self):
        result = Validator("abc 123").pattern(r"^[a-z0-9]+$").validate()
        assert result.valid is False

    def test_email_valid(self):
        result = Validator("user@example.com").email().validate()
        assert result.valid is True

    def test_email_invalid(self):
        result = Validator("not-email").email().validate()
        assert result.valid is False

    def test_url_valid(self):
        result = Validator("https://example.com").url().validate()
        assert result.valid is True

    def test_url_require_https(self):
        result = Validator("http://example.com").url(require_https=True).validate()
        assert result.valid is False

    def test_safe_id_valid(self):
        result = Validator("my-id-01").safe_id().validate()
        assert result.valid is True

    def test_safe_id_invalid(self):
        result = Validator("!invalid").safe_id().validate()
        assert result.valid is False

    def test_no_sql_injection_safe(self):
        result = Validator("hello world").no_sql_injection().validate()
        assert result.valid is True

    def test_no_sql_injection_detected(self):
        result = Validator("'; DROP TABLE users--").no_sql_injection().validate()
        assert result.valid is False

    def test_no_xss_safe(self):
        result = Validator("hello world").no_xss().validate()
        assert result.valid is True

    def test_no_xss_detected(self):
        result = Validator("<script>alert(1)</script>").no_xss().validate()
        assert result.valid is False

    def test_custom_validator(self):
        result = Validator(42).custom(lambda v: v > 0, "Must be positive").validate()
        assert result.valid is True

    def test_custom_validator_fails(self):
        result = Validator(-1).custom(lambda v: v > 0, "Must be positive").validate()
        assert result.valid is False
        assert "positive" in result.error

    def test_stop_on_first_error(self):
        result = (
            Validator(None, "field")
            .stop_on_first_error()
            .required()
            .min_length(3)
            .validate()
        )
        assert result.valid is False
        # Should have only one error since stop_on_first_error is active
        assert ";" not in result.error

    def test_multiple_errors(self):
        result = Validator("ab").min_length(5).max_length(1).validate()
        assert result.valid is False
        # Both errors should be present
        assert ";" in result.error

    def test_field_name_in_result(self):
        result = Validator("", "username").required().validate()
        assert result.field == "username"

    def test_custom_error_messages(self):
        result = Validator(None).required(message="Fill this in!").validate()
        assert result.error == "Fill this in!"


# =====================================================================
# Layer 2 -- Integration Tests (Validator chain complex compositions)
# =====================================================================


class TestValidatorIntegration:
    """Integration tests: complex Validator chain compositions."""

    def test_full_chain_valid(self):
        result = (
            Validator("user@example.com", "email")
            .required()
            .min_length(5)
            .max_length(100)
            .email()
            .no_sql_injection()
            .no_xss()
            .validate()
        )
        assert result.valid is True
        assert result.value == "user@example.com"

    def test_full_chain_invalid_email(self):
        result = (
            Validator("not-valid", "email")
            .required()
            .min_length(5)
            .max_length(100)
            .email()
            .validate()
        )
        assert result.valid is False
        assert "email" in result.error.lower()

    def test_url_chain_with_https(self):
        result = (
            Validator("https://secure.example.com/api", "url")
            .required()
            .url(require_https=True)
            .no_sql_injection()
            .no_xss()
            .validate()
        )
        assert result.valid is True

    def test_safe_id_chain(self):
        result = (
            Validator("my-project-01", "project_id")
            .required()
            .min_length(3)
            .max_length(63)
            .safe_id()
            .validate()
        )
        assert result.valid is True

    def test_multiple_validators_for_different_fields(self):
        """Validate multiple fields independently."""
        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "url": "https://example.com",
        }
        results = {
            "name": Validator(data["name"], "name").required().min_length(2).validate(),
            "email": Validator(data["email"], "email").required().email().validate(),
            "url": Validator(data["url"], "url").required().url().validate(),
        }
        assert all(r.valid for r in results.values())

    def test_chain_with_injection_attack(self):
        result = (
            Validator("'; DROP TABLE users--", "query")
            .required()
            .no_sql_injection()
            .no_xss()
            .validate()
        )
        assert result.valid is False


# =====================================================================
# Layer 3 -- Property-based Tests (Hypothesis)
# =====================================================================


class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(st.text(min_size=0, max_size=200))
    @settings(max_examples=100)
    def test_sanitize_id_always_safe_or_empty(self, s):
        """sanitize_id output is always safe_id-compatible or empty."""
        result = sanitize_id(s)
        if result:
            assert is_safe_id(result), f"sanitize_id({s!r}) produced {result!r} which is not safe"

    @given(st.text(min_size=0, max_size=300))
    @settings(max_examples=100)
    def test_sanitize_filename_no_path_separators(self, s):
        """sanitize_filename output never contains path separators."""
        result = sanitize_filename(s)
        assert "/" not in result, f"Found / in sanitize_filename({s!r})"
        assert "\\" not in result, f"Found \\ in sanitize_filename({s!r})"

    @given(st.text(min_size=1, max_size=500), st.integers(min_value=4, max_value=100))
    @settings(max_examples=100)
    def test_truncate_string_respects_max_length(self, s, max_len):
        """truncate_string output is always <= max_length."""
        result = truncate_string(s, max_len)
        assert len(result) <= max_len, f"len({result!r}) = {len(result)} > {max_len}"

    @given(st.text(min_size=0, max_size=200))
    @settings(max_examples=100)
    def test_normalize_string_no_control_chars(self, s):
        """normalize_string output has no control chars except \\n and \\t."""
        result = normalize_string(s)
        for ch in result:
            cat = unicodedata.category(ch)
            if cat.startswith("C"):
                assert ch in ("\n", "\t"), (
                    f"Control char U+{ord(ch):04X} ({cat}) found in normalize_string({s!r})"
                )

    @given(st.text(min_size=0, max_size=200))
    @settings(max_examples=100)
    def test_sanitize_filename_no_double_dots(self, s):
        """sanitize_filename output never contains '..'."""
        result = sanitize_filename(s)
        assert ".." not in result

    @given(st.text(min_size=0, max_size=200))
    @settings(max_examples=100)
    def test_generate_safe_id_is_lowercase(self, s):
        """generate_safe_id output is always lowercase."""
        result = generate_safe_id(s)
        assert result == result.lower()


# =====================================================================
# Layer 4 -- Failure Injection Tests
# =====================================================================


class TestFailureInjection:
    """Failure injection: None, empty, wrong types."""

    @pytest.mark.parametrize("val", [None, "", 0, 123, [], {}, 3.14, True])
    def test_is_safe_id_non_string(self, val):
        """is_safe_id handles non-string/empty inputs gracefully."""
        result = is_safe_id(val)
        assert result is False or isinstance(result, bool)

    @pytest.mark.parametrize("val", [None, "", 0, 123, [], {}])
    def test_is_safe_name_non_string(self, val):
        result = is_safe_name(val)
        assert isinstance(result, bool)

    @pytest.mark.parametrize("val", [None, "", 0, 123])
    def test_is_safe_filename_non_string(self, val):
        result = is_safe_filename(val)
        assert result is False

    @pytest.mark.parametrize("val", [None, ""])
    def test_sanitize_id_falsy(self, val):
        assert sanitize_id(val) == ""

    @pytest.mark.parametrize("val", [None, ""])
    def test_sanitize_filename_falsy(self, val):
        result = sanitize_filename(val)
        assert isinstance(result, str)

    @pytest.mark.parametrize("val", [None, "", 0, 123])
    def test_is_valid_email_non_string(self, val):
        assert is_valid_email(val) is False

    @pytest.mark.parametrize("val", [None, "", 0])
    def test_is_valid_uuid_non_string(self, val):
        assert is_valid_uuid(val) is False

    @pytest.mark.parametrize("val", [None, "", 0])
    def test_is_valid_slug_non_string(self, val):
        assert is_valid_slug(val) is False

    @pytest.mark.parametrize("val", [None, "", 0])
    def test_is_valid_url_non_string(self, val):
        assert is_valid_url(val) is False

    @pytest.mark.parametrize("val", [None, ""])
    def test_contains_sql_injection_falsy(self, val):
        assert contains_sql_injection(val) is False

    @pytest.mark.parametrize("val", [None, ""])
    def test_contains_xss_falsy(self, val):
        assert contains_xss(val) is False

    @pytest.mark.parametrize("val", [None, ""])
    def test_sanitize_html_falsy(self, val):
        assert sanitize_html(val) == ""

    @pytest.mark.parametrize("val", [None, ""])
    def test_normalize_string_falsy(self, val):
        assert normalize_string(val) == ""


# =====================================================================
# Layer 5 -- Concurrency Tests (Validator not shared-state)
# =====================================================================


class TestConcurrency:
    """Verify Validator instances are independent (no shared state)."""

    def test_validators_are_independent(self):
        """Two Validator instances do not share state."""
        v1 = Validator("hello", "field1")
        v2 = Validator("world", "field2")

        v1.required().min_length(100)  # will fail
        v2.required().min_length(1)  # will pass

        r1 = v1.validate()
        r2 = v2.validate()

        assert r1.valid is False
        assert r2.valid is True

    def test_thread_safety(self):
        """Run multiple validators concurrently; results must be correct."""
        results = {}

        def validate_in_thread(idx, value, should_pass):
            v = Validator(value, f"field_{idx}")
            if should_pass:
                result = v.required().min_length(1).validate()
            else:
                result = v.required().min_length(1000).validate()
            results[idx] = result

        threads = []
        for i in range(20):
            should_pass = i % 2 == 0
            t = threading.Thread(
                target=validate_in_thread,
                args=(i, f"value_{i}", should_pass),
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        for i in range(20):
            expected = i % 2 == 0
            assert results[i].valid is expected, f"Thread {i} expected valid={expected}"


# =====================================================================
# Layer 6 -- Security / Abuse Tests
# =====================================================================


class TestSecurityAbuse:
    """Security and abuse tests: injection, traversal, SSRF, long strings."""

    # -- SQL injection attacks --
    @pytest.mark.parametrize(
        "payload",
        [
            "'; DROP TABLE users--",
            "1; DELETE FROM accounts",
            "admin' OR 1=1--",
            "UNION SELECT password FROM users",
            "1; UPDATE users SET admin=1",
            "1; INSERT INTO logs VALUES('hacked')",
            "' OR '1'='1",
        ],
    )
    def test_sql_injection_detected(self, payload):
        assert contains_sql_injection(payload) is True

    # -- XSS attacks --
    @pytest.mark.parametrize(
        "payload",
        [
            "<script>document.location='http://evil.com'</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(document.cookie)",
            "<iframe src='http://evil.com'>",
            "<object data='http://evil.com'>",
            "<embed src='http://evil.com'>",
            '<body onload="alert(1)">',
            '<div onmouseover="steal()">',
        ],
    )
    def test_xss_detected(self, payload):
        assert contains_xss(payload) is True

    # -- Path traversal --
    @pytest.mark.parametrize(
        "path",
        [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\sam",
            "~/Documents/secret.txt",
            "$HOME/.ssh/id_rsa",
            "%APPDATA%\\secrets",
            "file\x00.txt",
        ],
    )
    def test_path_traversal_blocked(self, path):
        safe, _ = validate_path_safety(path)
        assert safe is False

    # -- Null byte injection --
    def test_null_byte_in_filename(self):
        assert is_safe_filename("file.txt\x00.exe") is False

    def test_null_byte_in_path(self):
        safe, _ = validate_path_safety("upload/file.txt\x00.exe")
        assert safe is False

    # -- Very long strings --
    def test_very_long_id(self):
        long_str = "a" * 10000
        assert is_safe_id(long_str) is False
        sanitized = sanitize_id(long_str)
        assert len(sanitized) <= 63

    def test_very_long_filename(self):
        long_str = "a" * 10000
        sanitized = sanitize_filename(long_str)
        assert len(sanitized) <= 255

    def test_very_long_sql_identifier(self):
        long_str = "a" * 10000
        sanitized = sanitize_sql_identifier(long_str)
        assert len(sanitized) <= 128

    def test_very_long_string_truncation(self):
        long_str = "a" * 10000
        result = truncate_string(long_str, 100)
        assert len(result) <= 100

    # -- Unicode homoglyphs --
    def test_unicode_homoglyph_in_email(self):
        # Cyrillic 'a' looks like Latin 'a'
        assert is_valid_email("\u0430dmin@example.com") is False  # Cyrillic 'a'

    # -- SSRF tests for is_safe_external_url --
    def test_ssrf_localhost(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            safe, err = is_safe_external_url("http://localhost/admin")
            assert safe is False
            assert "localhost" in err

    def test_ssrf_127_0_0_1(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (2, 1, 6, "", ("127.0.0.1", 0)),
            ]
            safe, err = is_safe_external_url("http://127.0.0.1/admin")
            assert safe is False

    def test_ssrf_metadata_ip(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (2, 1, 6, "", ("169.254.169.254", 0)),
            ]
            safe, err = is_safe_external_url("http://169.254.169.254/latest/meta-data/")
            assert safe is False
            assert "private" in err.lower() or "reserved" in err.lower()

    def test_ssrf_zero_ip(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            safe, err = is_safe_external_url("http://0.0.0.0/")
            assert safe is False

    def test_ssrf_file_scheme(self):
        safe, err = is_safe_external_url("file:///etc/passwd")
        assert safe is False
        assert "Scheme" in err

    def test_ssrf_ftp_scheme(self):
        safe, err = is_safe_external_url("ftp://evil.com/file")
        assert safe is False

    def test_ssrf_private_10_network(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (2, 1, 6, "", ("10.0.0.1", 0)),
            ]
            safe, err = is_safe_external_url("http://internal.corp/api")
            assert safe is False

    def test_ssrf_private_172_network(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (2, 1, 6, "", ("172.16.0.1", 0)),
            ]
            safe, err = is_safe_external_url("http://internal.corp/api")
            assert safe is False

    def test_ssrf_private_192_network(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (2, 1, 6, "", ("192.168.1.1", 0)),
            ]
            safe, err = is_safe_external_url("http://internal.corp/api")
            assert safe is False

    def test_ssrf_safe_external_url(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [
                (2, 1, 6, "", ("93.184.216.34", 0)),
            ]
            safe, err = is_safe_external_url("https://example.com")
            assert safe is True
            assert err is None

    def test_ssrf_dns_failure(self):
        with patch("backend.app.utils.validation.socket.getaddrinfo") as mock_gai:
            mock_gai.side_effect = __import__("socket").gaierror("DNS lookup failed")
            safe, err = is_safe_external_url("http://nonexistent.invalid")
            assert safe is False
            assert "resolve" in err.lower()

    def test_ssrf_empty_url(self):
        safe, err = is_safe_external_url("")
        assert safe is False

    def test_ssrf_none_url(self):
        safe, err = is_safe_external_url(None)
        assert safe is False


# =====================================================================
# Layer 7 -- Usability Tests (realistic scenarios)
# =====================================================================


class TestUsabilityScenarios:
    """Realistic validation scenarios for common use cases."""

    def test_user_registration_form(self):
        """Validate a user registration form."""
        form = {
            "username": "john_doe",
            "email": "john@example.com",
            "display_name": "John Doe",
            "password": "securepassword123",
        }

        # Required fields
        ok, missing = validate_required_fields(
            form, ["username", "email", "display_name", "password"]
        )
        assert ok is True

        # Username is safe ID
        assert is_safe_id(form["username"]) is True

        # Email is valid
        assert is_valid_email(form["email"]) is True

        # Display name is safe
        assert is_safe_name(form["display_name"]) is True

        # No injection in any field
        for key, val in form.items():
            assert contains_sql_injection(val) is False
            assert contains_xss(val) is False

    def test_file_upload_validation(self):
        """Validate a file upload scenario."""
        filename = "Q4-Report_(Final).pdf"

        # Filename is safe
        assert is_safe_filename(filename) is True

        # Extension is allowed
        valid, err = validate_file_extension(filename, [".pdf", ".docx", ".xlsx"])
        assert valid is True

        # Path safety
        safe, err = validate_path_safety(f"uploads/{filename}")
        assert safe is True

        # Sanitize just in case
        sanitized = sanitize_filename(filename)
        assert sanitized  # non-empty

    def test_file_upload_attack_blocked(self):
        """Block malicious file upload."""
        evil_filename = "../../../etc/passwd"

        assert is_safe_filename(evil_filename) is False
        safe, _ = validate_path_safety(evil_filename)
        assert safe is False

    def test_api_query_parameter_validation(self):
        """Validate API query parameters."""
        params = {
            "page": 1,
            "per_page": 25,
            "sort_by": "created_at",
            "search": "quarterly report",
        }

        # Numeric range
        ok, _ = validate_numeric_range(params["page"], min_value=1)
        assert ok is True
        ok, _ = validate_numeric_range(params["per_page"], min_value=1, max_value=100)
        assert ok is True

        # SQL identifier for sort_by
        sanitized_sort = sanitize_sql_identifier(params["sort_by"])
        assert sanitized_sort == "created_at"

        # Search is safe
        assert contains_sql_injection(params["search"]) is False
        assert contains_xss(params["search"]) is False

    def test_api_query_with_injection_attempt(self):
        """Block SQL injection in query params."""
        malicious_sort = "name; DROP TABLE users--"
        sanitized = sanitize_sql_identifier(malicious_sort)
        assert "DROP" not in sanitized or ";" not in sanitized
        # The sanitized version keeps only alnum+underscore
        assert all(c.isalnum() or c == "_" for c in sanitized)

    def test_date_range_filter(self):
        """Validate date range filtering scenario."""
        start = "2024-01-01"
        end = "2024-12-31"

        ok_start, parsed_start = validate_date_string(start)
        ok_end, parsed_end = validate_date_string(end)

        assert ok_start is True
        assert ok_end is True
        assert parsed_start < parsed_end

    def test_slug_for_url(self):
        """Generate and validate URL slugs."""
        title = "My Awesome Blog Post!"
        slug = generate_safe_id(title)
        # generate_safe_id produces lowercase with hyphens
        assert slug == slug.lower()
        assert "!" not in slug

    def test_html_content_sanitization(self):
        """Sanitize user-submitted HTML content."""
        html = '<p>Hello <b>world</b></p><script>steal()</script><img onerror="alert(1)">'

        sanitized = sanitize_html(html)
        assert "<script" not in sanitized
        assert "onerror" not in sanitized
        assert "<p>" in sanitized

    def test_json_field_length_validation(self):
        """Validate JSON field lengths."""
        short_desc = "This is fine."
        long_desc = "x" * 20000

        ok, _ = validate_json_string_length(short_desc, max_length=10000)
        assert ok is True

        ok, _ = validate_json_string_length(long_desc, max_length=10000)
        assert ok is False

    def test_comprehensive_validator_chain_for_username(self):
        """Use Validator chain for a complete username validation."""
        result = (
            Validator("john_doe-42", "username")
            .required()
            .min_length(3)
            .max_length(63)
            .safe_id()
            .no_sql_injection()
            .no_xss()
            .validate()
        )
        assert result.valid is True
        assert result.value == "john_doe-42"

    def test_comprehensive_validator_chain_rejection(self):
        """Validator chain rejects bad username with clear error."""
        result = (
            Validator("<script>alert('xss')</script>", "username")
            .required()
            .min_length(3)
            .max_length(63)
            .safe_id()
            .no_xss()
            .validate()
        )
        assert result.valid is False
        assert result.field == "username"
