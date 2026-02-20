"""Input validation and sanitization utilities.

Provides comprehensive validation for:
- IDs and names
- File paths and filenames
- SQL identifiers
- Email addresses
- URLs
- JSON content
- Numeric ranges
- Date/time values
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union
import ipaddress
import socket
from urllib.parse import urlparse

T = TypeVar("T")


# =============================================================================
# Validation Result
# =============================================================================

@dataclass
class ValidationResult:
    """Result of a validation operation."""
    valid: bool
    value: Any = None
    error: Optional[str] = None
    field: Optional[str] = None

    @staticmethod
    def success(value: Any = None) -> "ValidationResult":
        return ValidationResult(valid=True, value=value)

    @staticmethod
    def failure(error: str, field: Optional[str] = None) -> "ValidationResult":
        return ValidationResult(valid=False, error=error, field=field)


# =============================================================================
# Patterns
# =============================================================================

# Patterns for validation
SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$")
SAFE_NAME_PATTERN = re.compile(r"^[\w\s\-\.()]{1,100}$", re.UNICODE)
SAFE_FILENAME_PATTERN = re.compile(r"^[\w\-\.()]+$", re.UNICODE)
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE
)
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Dangerous path patterns to block
DANGEROUS_PATH_PATTERNS = [
    r"\.\.",  # Parent directory traversal
    r"^/",  # Absolute paths (Unix)
    r"^[A-Za-z]:",  # Absolute paths (Windows)
    r"~",  # Home directory expansion
    r"\$",  # Environment variable expansion
    r"%",  # Windows environment variables
    r"\x00",  # Null byte injection
]

# Common SQL injection patterns
SQL_INJECTION_PATTERNS = [
    r";\s*--",
    r";\s*drop\s",
    r";\s*delete\s",
    r";\s*update\s",
    r";\s*insert\s",
    r"union\s+select",
    r"or\s+1\s*=\s*1",
    r"'\s*or\s*'",
]

# Common XSS patterns
XSS_PATTERNS = [
    r"<script",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe",
    r"<object",
    r"<embed",
]


def is_safe_id(value: str) -> bool:
    """Check if a value is safe to use as an ID (alphanumeric with dashes/underscores)."""
    if not value or not isinstance(value, str):
        return False
    return bool(SAFE_ID_PATTERN.match(value))


def is_safe_name(value: str) -> bool:
    """Check if a value is safe to use as a display name."""
    if not value or not isinstance(value, str):
        return False
    return bool(SAFE_NAME_PATTERN.match(value)) and len(value) <= 100


def is_safe_filename(value: str) -> bool:
    """Check if a value is safe to use as a filename."""
    if not value or not isinstance(value, str):
        return False
    if not SAFE_FILENAME_PATTERN.match(value):
        return False
    # Block dangerous patterns
    for pattern in DANGEROUS_PATH_PATTERNS:
        if re.search(pattern, value):
            return False
    return True


def sanitize_id(value: str) -> str:
    """Sanitize a string to be safe for use as an ID."""
    if not value:
        return ""
    # Remove non-alphanumeric characters except dashes and underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "", value)
    # Ensure it starts with alphanumeric
    sanitized = re.sub(r"^[^a-zA-Z0-9]+", "", sanitized)
    return sanitized[:63]  # Max 63 chars


def sanitize_filename(value: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    if not value:
        return ""
    # Remove path separators and dangerous characters
    sanitized = re.sub(r"[/\\:*?\"<>|]", "", value)
    # Remove parent directory traversal
    sanitized = sanitized.replace("..", "")
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    # Ensure non-empty
    if not sanitized:
        return "unnamed"
    return sanitized[:255]  # Max 255 chars for most filesystems


def validate_path_safety(path: str | Path) -> tuple[bool, Optional[str]]:
    """
    Validate that a path is safe (no traversal attacks, etc).
    Returns (is_safe, error_message).
    """
    path_str = str(path)

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATH_PATTERNS:
        if re.search(pattern, path_str):
            return False, f"Path contains disallowed pattern: {pattern}"

    # Check for null bytes
    if "\x00" in path_str:
        return False, "Path contains null byte"

    return True, None


def validate_file_extension(filename: str, allowed_extensions: list[str]) -> tuple[bool, Optional[str]]:
    """
    Validate that a file has an allowed extension.
    Returns (is_valid, error_message).
    """
    if not filename:
        return False, "Filename is required"

    ext = Path(filename).suffix.lower()
    if not ext:
        return False, "File must have an extension"

    # Normalize extensions (add leading dot if missing)
    allowed = [e.lower() if e.startswith(".") else f".{e.lower()}" for e in allowed_extensions]

    if ext not in allowed:
        return False, f"Invalid file type '{ext}'. Allowed: {', '.join(allowed)}"

    return True, None


def sanitize_sql_identifier(value: str) -> str:
    """
    Sanitize a SQL identifier (table/column name).
    Note: This is for display/logging only, not for building SQL queries.
    Use parameterized queries for actual SQL.
    """
    if not value:
        return ""
    # Remove all non-alphanumeric characters except underscore
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "", value)
    return sanitized[:128]


def validate_json_string_length(value: str, max_length: int = 10000) -> tuple[bool, Optional[str]]:
    """Validate that a JSON string field is not too long."""
    if not value:
        return True, None
    if len(value) > max_length:
        return False, f"Value too long (max {max_length} characters)"
    return True, None


# =============================================================================
# Additional Validation Functions
# =============================================================================

def is_valid_email(value: str) -> bool:
    """Check if a string is a valid email address."""
    if not value or not isinstance(value, str):
        return False
    return bool(EMAIL_PATTERN.match(value.strip()))


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    if not value or not isinstance(value, str):
        return False
    return bool(UUID_PATTERN.match(value.strip()))


def is_valid_slug(value: str) -> bool:
    """Check if a string is a valid URL slug."""
    if not value or not isinstance(value, str):
        return False
    return bool(SLUG_PATTERN.match(value.strip()))


def is_valid_url(value: str, require_https: bool = False) -> bool:
    """Check if a string is a valid URL."""
    if not value or not isinstance(value, str):
        return False

    try:
        parsed = urlparse(value.strip())
        if not parsed.scheme or not parsed.netloc:
            return False
        if require_https and parsed.scheme != "https":
            return False
        if parsed.scheme not in ("http", "https"):
            return False
        return True
    except Exception:
        return False


_PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def is_safe_external_url(url: str) -> tuple[bool, str | None]:
    """Validate that a URL is safe for server-side requests (anti-SSRF).

    Blocks:
    - Non-HTTP(S) schemes (file://, ftp://, etc.)
    - localhost, 127.0.0.0/8, ::1
    - Private networks (10.x, 172.16-31.x, 192.168.x)
    - Link-local / cloud metadata (169.254.x.x)
    - 0.0.0.0

    Returns (is_safe, error_message).
    """
    if not url or not isinstance(url, str):
        return False, "URL is required"

    try:
        parsed = urlparse(url.strip())
    except Exception:
        return False, "Invalid URL"

    # Scheme check
    if parsed.scheme not in ("http", "https"):
        return False, f"Scheme '{parsed.scheme}' is not allowed; use http or https"

    hostname = parsed.hostname
    if not hostname:
        return False, "URL has no hostname"

    # Obvious hostname check
    if hostname in ("localhost", "0.0.0.0"):
        return False, f"Hostname '{hostname}' is not allowed"

    # Resolve hostname to IP and check against private ranges
    try:
        addr_infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        return False, f"Could not resolve hostname '{hostname}'"

    for family, _type, _proto, _canon, sockaddr in addr_infos:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        for network in _PRIVATE_NETWORKS:
            if ip in network:
                return False, f"URL resolves to private/reserved address ({ip_str})"

        # Also block unspecified address (0.0.0.0 / ::)
        if ip == ipaddress.ip_address("0.0.0.0") or ip == ipaddress.ip_address("::"):
            return False, "URL resolves to unspecified address"

    return True, None


def contains_sql_injection(value: str) -> bool:
    """Check if a string contains potential SQL injection patterns."""
    if not value:
        return False

    lower_value = value.lower()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, lower_value, re.IGNORECASE):
            return True
    return False


_BLOCKED_SQL_KEYWORDS = re.compile(
    r"\b(DROP|ALTER|TRUNCATE|CREATE|INSERT|UPDATE|DELETE|GRANT|REVOKE|EXEC|EXECUTE|MERGE|REPLACE|CALL)\b",
    re.IGNORECASE,
)

_SQL_LINE_COMMENT = re.compile(r"--[^\n]*")
_SQL_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def is_read_only_sql(query: str) -> tuple[bool, str | None]:
    """Check whether a SQL query is read-only (SELECT / WITH only).

    Returns (is_safe, error_message).
    Strips comments before analysis.  Blocks DDL, DML, and admin
    statements: DROP, ALTER, TRUNCATE, CREATE, INSERT, UPDATE, DELETE,
    GRANT, REVOKE, EXEC, EXECUTE, MERGE, REPLACE, CALL.
    """
    if not query or not query.strip():
        return False, "Query is empty"

    # Strip comments
    cleaned = _SQL_LINE_COMMENT.sub(" ", query)
    cleaned = _SQL_BLOCK_COMMENT.sub(" ", cleaned)
    cleaned = cleaned.strip()

    if not cleaned:
        return False, "Query is empty after removing comments"

    # Check first keyword
    first_word = cleaned.split()[0].upper()
    if first_word not in ("SELECT", "WITH"):
        return False, f"Only SELECT queries are allowed (got {first_word})"

    # Scan for blocked keywords anywhere (e.g. sub-statements)
    match = _BLOCKED_SQL_KEYWORDS.search(cleaned)
    if match:
        return False, f"Query contains blocked keyword: {match.group(0).upper()}"

    return True, None


def contains_xss(value: str) -> bool:
    """Check if a string contains potential XSS patterns."""
    if not value:
        return False

    lower_value = value.lower()
    for pattern in XSS_PATTERNS:
        if re.search(pattern, lower_value, re.IGNORECASE):
            return True
    return False


def sanitize_html(value: str) -> str:
    """Remove potentially dangerous HTML content."""
    if not value:
        return ""

    # Remove script tags and content
    result = re.sub(r"<script[^>]*>.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL)

    # Remove event handlers
    result = re.sub(r"\s*on\w+\s*=\s*[\"'][^\"']*[\"']", "", result, flags=re.IGNORECASE)

    # Remove javascript: URLs
    result = re.sub(r"javascript:", "", result, flags=re.IGNORECASE)

    return result


def normalize_string(value: str) -> str:
    """Normalize a string by removing control characters and normalizing unicode."""
    if not value:
        return ""

    # Normalize unicode
    normalized = unicodedata.normalize("NFC", value)

    # Remove control characters except newline and tab
    normalized = "".join(
        char for char in normalized
        if char == "\n" or char == "\t" or not unicodedata.category(char).startswith("C")
    )

    return normalized.strip()


def validate_numeric_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    field_name: str = "value",
) -> tuple[bool, Optional[str]]:
    """Validate that a numeric value is within a range."""
    if min_value is not None and value < min_value:
        return False, f"{field_name} must be at least {min_value}"
    if max_value is not None and value > max_value:
        return False, f"{field_name} must be at most {max_value}"
    return True, None


def validate_date_string(
    value: str,
    formats: Optional[List[str]] = None,
) -> tuple[bool, Optional[datetime]]:
    """
    Validate that a string is a valid date.
    Returns (is_valid, parsed_datetime or None).
    """
    if not value:
        return False, None

    formats = formats or [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(value.strip(), fmt)
            return True, parsed
        except ValueError:
            continue

    return False, None


def validate_required_fields(
    data: dict,
    required_fields: List[str],
) -> tuple[bool, List[str]]:
    """
    Validate that all required fields are present and non-empty.
    Returns (is_valid, list of missing fields).
    """
    missing = []
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)

    return len(missing) == 0, missing


def validate_field_type(
    value: Any,
    expected_type: type,
    field_name: str = "value",
) -> tuple[bool, Optional[str]]:
    """Validate that a value is of the expected type."""
    if not isinstance(value, expected_type):
        return False, f"{field_name} must be of type {expected_type.__name__}"
    return True, None


def truncate_string(value: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to max length, adding suffix if truncated."""
    if not value or len(value) <= max_length:
        return value
    return value[:max_length - len(suffix)] + suffix


def generate_safe_id(value: str, max_length: int = 63) -> str:
    """Generate a safe ID from a string."""
    if not value:
        return ""

    # Normalize and lowercase
    safe = normalize_string(value).lower()

    # Replace spaces and special chars with hyphens
    safe = re.sub(r"[^a-z0-9]+", "-", safe)

    # Remove leading/trailing hyphens
    safe = safe.strip("-")

    # Ensure starts with alphanumeric
    if safe and not safe[0].isalnum():
        safe = "x" + safe

    return safe[:max_length]


# =============================================================================
# Validator Chain
# =============================================================================

class Validator:
    """
    Chainable validator for building complex validation rules.

    Usage:
        result = Validator(value).required().min_length(3).max_length(50).validate()
        if not result.valid:
            print(result.error)
    """

    def __init__(self, value: Any, field_name: str = "value"):
        self._value = value
        self._field = field_name
        self._errors: List[str] = []
        self._stop_on_first_error = False

    def stop_on_first_error(self) -> "Validator":
        """Stop validation after first error."""
        self._stop_on_first_error = True
        return self

    def _add_error(self, error: str) -> None:
        self._errors.append(error)

    def _should_continue(self) -> bool:
        return not self._stop_on_first_error or not self._errors

    def required(self, message: Optional[str] = None) -> "Validator":
        """Validate that the value is not None or empty."""
        if not self._should_continue():
            return self

        if self._value is None:
            self._add_error(message or f"{self._field} is required")
        elif isinstance(self._value, str) and not self._value.strip():
            self._add_error(message or f"{self._field} cannot be empty")

        return self

    def min_length(self, length: int, message: Optional[str] = None) -> "Validator":
        """Validate minimum length."""
        if not self._should_continue():
            return self

        if isinstance(self._value, (str, list, dict)) and len(self._value) < length:
            self._add_error(message or f"{self._field} must be at least {length} characters")

        return self

    def max_length(self, length: int, message: Optional[str] = None) -> "Validator":
        """Validate maximum length."""
        if not self._should_continue():
            return self

        if isinstance(self._value, (str, list, dict)) and len(self._value) > length:
            self._add_error(message or f"{self._field} must be at most {length} characters")

        return self

    def pattern(self, regex: str, message: Optional[str] = None) -> "Validator":
        """Validate against a regex pattern."""
        if not self._should_continue():
            return self

        if isinstance(self._value, str) and not re.match(regex, self._value):
            self._add_error(message or f"{self._field} has invalid format")

        return self

    def email(self, message: Optional[str] = None) -> "Validator":
        """Validate as email address."""
        if not self._should_continue():
            return self

        if isinstance(self._value, str) and not is_valid_email(self._value):
            self._add_error(message or f"{self._field} must be a valid email address")

        return self

    def url(self, require_https: bool = False, message: Optional[str] = None) -> "Validator":
        """Validate as URL."""
        if not self._should_continue():
            return self

        if isinstance(self._value, str) and not is_valid_url(self._value, require_https):
            self._add_error(message or f"{self._field} must be a valid URL")

        return self

    def safe_id(self, message: Optional[str] = None) -> "Validator":
        """Validate as safe ID."""
        if not self._should_continue():
            return self

        if isinstance(self._value, str) and not is_safe_id(self._value):
            self._add_error(message or f"{self._field} contains invalid characters")

        return self

    def no_sql_injection(self, message: Optional[str] = None) -> "Validator":
        """Validate against SQL injection patterns."""
        if not self._should_continue():
            return self

        if isinstance(self._value, str) and contains_sql_injection(self._value):
            self._add_error(message or f"{self._field} contains potentially dangerous content")

        return self

    def no_xss(self, message: Optional[str] = None) -> "Validator":
        """Validate against XSS patterns."""
        if not self._should_continue():
            return self

        if isinstance(self._value, str) and contains_xss(self._value):
            self._add_error(message or f"{self._field} contains potentially dangerous content")

        return self

    def custom(self, validator: Callable[[Any], bool], message: str) -> "Validator":
        """Apply a custom validation function."""
        if not self._should_continue():
            return self

        if not validator(self._value):
            self._add_error(message)

        return self

    def validate(self) -> ValidationResult:
        """Execute validation and return result."""
        if self._errors:
            return ValidationResult.failure(
                error="; ".join(self._errors),
                field=self._field,
            )
        return ValidationResult.success(value=self._value)
