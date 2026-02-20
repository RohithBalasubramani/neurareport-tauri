"""Unified error hierarchy for the entire backend.

All domain-specific errors inherit from NeuraError.
Each error has a code, message, and optional details.
This replaces scattered HTTPException usage in business logic.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class NeuraError(Exception):
    """Base error type for all NeuraReport errors."""

    code = "error"

    def __init__(
        self,
        message: str,
        *,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
        self.cause = cause

    def __str__(self) -> str:
        if self.details:
            return f"[{self.code}] {self.message} - {self.details}"
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        result = {"code": self.code, "message": self.message}
        if self.details:
            result["details"] = self.details
        return result


class ValidationError(NeuraError):
    """Raised when input validation fails."""

    code = "validation_error"


class NotFoundError(NeuraError):
    """Raised when a requested resource does not exist."""

    code = "not_found"


class ConflictError(NeuraError):
    """Raised when an operation conflicts with current state."""

    code = "conflict"


class ExternalServiceError(NeuraError):
    """Raised when an external service (LLM, email, etc.) fails."""

    code = "external_service_error"

    def __init__(
        self,
        message: str,
        *,
        service: str = "unknown",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details=details, cause=cause)
        self.service = service


class ConfigurationError(NeuraError):
    """Raised when system configuration is invalid."""

    code = "configuration_error"


class PipelineError(NeuraError):
    """Raised when a pipeline step fails."""

    code = "pipeline_error"

    def __init__(
        self,
        message: str,
        *,
        step: str = "unknown",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details=details, cause=cause)
        self.step = step


class DataSourceError(NeuraError):
    """Raised when data source operations fail."""

    code = "data_source_error"


class RenderError(NeuraError):
    """Raised when rendering fails."""

    code = "render_error"

    def __init__(
        self,
        message: str,
        *,
        format: str = "unknown",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, details=details, cause=cause)
        self.format = format
