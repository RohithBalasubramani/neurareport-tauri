"""
Error classification for job retry logic.

Determines whether errors are retriable (transient) or permanent.
This allows the job system to automatically retry transient failures
while immediately failing on permanent errors.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger("neura.jobs.error_classifier")


class ErrorCategory(str, Enum):
    """Categories of errors for classification."""

    TRANSIENT = "transient"      # Temporary failure, should retry
    PERMANENT = "permanent"      # Will never succeed, don't retry
    RESOURCE = "resource"        # Resource exhaustion, retry with backoff
    TIMEOUT = "timeout"          # Operation timed out, may retry
    UNKNOWN = "unknown"          # Unknown error, default to retry


@dataclass
class ClassifiedError:
    """Result of error classification."""

    category: ErrorCategory
    is_retriable: bool
    original_message: str
    normalized_message: str
    suggested_backoff_multiplier: float = 1.0


class ErrorClassifier:
    """
    Classify errors as retriable or permanent.

    Uses pattern matching to identify common error types and determine
    whether they should be retried.
    """

    # Errors that are definitely retriable (transient failures)
    # NOTE: Order matters! More specific patterns should come before generic ones.
    TRANSIENT_PATTERNS = [
        # Rate limiting (check first, before "try again" pattern)
        (r"rate limit", ErrorCategory.RESOURCE),
        (r"throttl", ErrorCategory.RESOURCE),
        (r"429", ErrorCategory.RESOURCE),

        # Network/connection issues
        (r"connection refused", ErrorCategory.TRANSIENT),
        (r"connection reset", ErrorCategory.TRANSIENT),
        (r"connection timed out", ErrorCategory.TIMEOUT),
        (r"timeout", ErrorCategory.TIMEOUT),
        (r"temporary failure", ErrorCategory.TRANSIENT),
        (r"temporarily unavailable", ErrorCategory.TRANSIENT),
        (r"try again", ErrorCategory.TRANSIENT),
        (r"service unavailable", ErrorCategory.TRANSIENT),
        (r"503", ErrorCategory.TRANSIENT),
        (r"502", ErrorCategory.TRANSIENT),
        (r"504", ErrorCategory.TRANSIENT),

        # Database issues
        (r"database is locked", ErrorCategory.RESOURCE),
        (r"too many connections", ErrorCategory.RESOURCE),
        (r"deadlock", ErrorCategory.TRANSIENT),
        (r"lock wait timeout", ErrorCategory.TIMEOUT),
        (r"could not connect to server", ErrorCategory.TRANSIENT),

        # Browser/rendering issues (often transient)
        (r"playwright", ErrorCategory.TRANSIENT),
        (r"chromium", ErrorCategory.TRANSIENT),
        (r"browser.*closed", ErrorCategory.TRANSIENT),
        (r"target.*closed", ErrorCategory.TRANSIENT),
        (r"page crashed", ErrorCategory.TRANSIENT),

        # File system issues (often transient)
        (r"resource temporarily unavailable", ErrorCategory.RESOURCE),
        (r"no space left", ErrorCategory.RESOURCE),
        (r"disk quota", ErrorCategory.RESOURCE),
    ]

    # Errors that are definitely permanent (will never succeed)
    PERMANENT_PATTERNS = [
        # Not found errors
        (r"template not found", ErrorCategory.PERMANENT),
        (r"template_id.*not found", ErrorCategory.PERMANENT),
        (r"contract missing", ErrorCategory.PERMANENT),
        (r"connection not found", ErrorCategory.PERMANENT),
        (r"file not found", ErrorCategory.PERMANENT),
        (r"does not exist", ErrorCategory.PERMANENT),

        # Authentication/authorization
        (r"authentication failed", ErrorCategory.PERMANENT),
        (r"permission denied", ErrorCategory.PERMANENT),
        (r"unauthorized", ErrorCategory.PERMANENT),
        (r"forbidden", ErrorCategory.PERMANENT),
        (r"401", ErrorCategory.PERMANENT),
        (r"403", ErrorCategory.PERMANENT),

        # Validation errors
        (r"invalid template", ErrorCategory.PERMANENT),
        (r"invalid.*id", ErrorCategory.PERMANENT),
        (r"validation.*failed", ErrorCategory.PERMANENT),
        (r"schema.*invalid", ErrorCategory.PERMANENT),
        (r"malformed", ErrorCategory.PERMANENT),

        # Configuration errors
        (r"missing required", ErrorCategory.PERMANENT),
        (r"configuration error", ErrorCategory.PERMANENT),
    ]

    @classmethod
    def classify(cls, error: str | Exception) -> ClassifiedError:
        """
        Classify an error as retriable or permanent.

        Args:
            error: Error message string or Exception object

        Returns:
            ClassifiedError with category and retriability determination
        """
        if isinstance(error, Exception):
            error_str = str(error)
            error_type = type(error).__name__
        else:
            error_str = str(error)
            error_type = None

        error_lower = error_str.lower()

        # Check permanent patterns first (they take precedence)
        for pattern, category in cls.PERMANENT_PATTERNS:
            if re.search(pattern, error_lower):
                return ClassifiedError(
                    category=category,
                    is_retriable=False,
                    original_message=error_str,
                    normalized_message=f"[{category.value}] {error_str}",
                    suggested_backoff_multiplier=1.0,
                )

        # Check transient patterns
        for pattern, category in cls.TRANSIENT_PATTERNS:
            if re.search(pattern, error_lower):
                # Resource exhaustion errors should use longer backoff
                multiplier = 2.0 if category == ErrorCategory.RESOURCE else 1.0
                return ClassifiedError(
                    category=category,
                    is_retriable=True,
                    original_message=error_str,
                    normalized_message=f"[{category.value}] {error_str}",
                    suggested_backoff_multiplier=multiplier,
                )

        # Check for TimeoutError exception type
        if error_type and "timeout" in error_type.lower():
            return ClassifiedError(
                category=ErrorCategory.TIMEOUT,
                is_retriable=True,
                original_message=error_str,
                normalized_message=f"[{ErrorCategory.TIMEOUT.value}] {error_str}",
                suggested_backoff_multiplier=1.0,
            )

        # Default: unknown errors are retriable (optimistic)
        # This ensures we don't permanently fail on unexpected errors
        logger.info(
            "error_classification_unknown",
            extra={
                "error_message": error_str[:200],
                "error_type": error_type,
                "decision": "retriable",
            }
        )

        return ClassifiedError(
            category=ErrorCategory.UNKNOWN,
            is_retriable=True,  # Optimistic default
            original_message=error_str,
            normalized_message=f"[unknown] {error_str}",
            suggested_backoff_multiplier=1.0,
        )

    @classmethod
    def is_retriable(cls, error: str | Exception) -> bool:
        """
        Quick check if an error is retriable.

        Args:
            error: Error message string or Exception object

        Returns:
            True if the error is retriable, False otherwise
        """
        return cls.classify(error).is_retriable

    @classmethod
    def get_backoff_multiplier(cls, error: str | Exception) -> float:
        """
        Get the suggested backoff multiplier for an error.

        Resource exhaustion errors should use longer backoff.

        Args:
            error: Error message string or Exception object

        Returns:
            Multiplier to apply to base backoff (1.0 = normal, 2.0 = double)
        """
        return cls.classify(error).suggested_backoff_multiplier


def is_retriable_error(error: str | Exception) -> bool:
    """
    Convenience function to check if an error is retriable.

    Args:
        error: Error message string or Exception object

    Returns:
        True if the error is retriable, False otherwise
    """
    return ErrorClassifier.is_retriable(error)


def classify_error(error: str | Exception) -> ClassifiedError:
    """
    Convenience function to classify an error.

    Args:
        error: Error message string or Exception object

    Returns:
        ClassifiedError with full classification details
    """
    return ErrorClassifier.classify(error)
