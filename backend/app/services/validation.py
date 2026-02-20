from __future__ import annotations

from backend.app.utils import validation as _validation


def is_safe_name(value: str) -> bool:
    """Service-layer validation boundary for safe display names."""
    return _validation.is_safe_name(value)


def validate_file_extension(filename: str, allowed_extensions: list[str]) -> tuple[bool, str | None]:
    """Service-layer validation boundary for upload file extensions."""
    return _validation.validate_file_extension(filename, allowed_extensions)


def is_read_only_sql(query: str) -> tuple[bool, str | None]:
    """Service-layer validation boundary for SQL read-only checks."""
    return _validation.is_read_only_sql(query)


def validate_path_safety(path: str) -> tuple[bool, str | None]:
    """Service-layer validation boundary for file path safety."""
    return _validation.validate_path_safety(path)


def is_safe_external_url(url: str) -> tuple[bool, str | None]:
    """Service-layer validation boundary for SSRF protection on external URLs."""
    return _validation.is_safe_external_url(url)


__all__ = ["is_safe_name", "validate_file_extension", "is_read_only_sql", "validate_path_safety", "is_safe_external_url"]
