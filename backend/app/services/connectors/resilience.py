"""
Resilience utilities for database connectors.

Implements retry logic with exponential backoff and error classification
following state-of-the-art patterns from Tenacity, Sidekiq, and AWS.
"""
from __future__ import annotations

import asyncio
import logging
import random
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

logger = logging.getLogger("neura.connectors.resilience")

# Type variable for generic decorator
T = TypeVar("T")


# =============================================================================
# Error Classification
# =============================================================================

# Transient errors that should be retried (temporary failures)
TRANSIENT_ERRORS: Tuple[Type[Exception], ...] = (
    ConnectionError,
    ConnectionRefusedError,
    ConnectionResetError,
    ConnectionAbortedError,
    TimeoutError,
    asyncio.TimeoutError,
    OSError,  # Network errors often raise OSError
)

# Permanent errors that should NOT be retried (will never succeed)
PERMANENT_ERRORS: Tuple[Type[Exception], ...] = (
    ValueError,  # Invalid configuration
    TypeError,   # Type errors in config
    KeyError,    # Missing required config
    PermissionError,  # Permission denied
)


def is_transient_error(exception: Exception) -> bool:
    """
    Check if an exception represents a transient (retriable) error.

    Args:
        exception: The exception to classify

    Returns:
        True if the error is transient and should be retried
    """
    # Check exception type
    if isinstance(exception, PERMANENT_ERRORS):
        return False

    if isinstance(exception, TRANSIENT_ERRORS):
        return True

    # Check error message for common patterns
    error_msg = str(exception).lower()

    # Permanent patterns (check first)
    permanent_patterns = [
        "authentication failed",
        "permission denied",
        "access denied",
        "invalid credentials",
        "invalid password",
        "invalid username",
        "not found",
        "does not exist",
        "invalid configuration",
    ]
    for pattern in permanent_patterns:
        if pattern in error_msg:
            return False

    # Transient patterns
    transient_patterns = [
        "connection refused",
        "connection reset",
        "connection timed out",
        "timeout",
        "temporarily unavailable",
        "too many connections",
        "database is locked",
        "deadlock",
        "try again",
        "service unavailable",
        "503",
        "502",
        "504",
    ]
    for pattern in transient_patterns:
        if pattern in error_msg:
            return True

    # Default: unknown errors are considered transient (optimistic)
    logger.debug(f"Unknown error type, treating as transient: {type(exception).__name__}")
    return True


def is_permanent_error(exception: Exception) -> bool:
    """
    Check if an exception represents a permanent (non-retriable) error.

    Args:
        exception: The exception to classify

    Returns:
        True if the error is permanent and should not be retried
    """
    return not is_transient_error(exception)


# =============================================================================
# Retry Decorator
# =============================================================================

def with_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator for database operations with retry logic.

    Implements exponential backoff with optional jitter to prevent
    thundering herd problems.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time between retries in seconds (default: 1.0)
        max_wait: Maximum wait time between retries in seconds (default: 30.0)
        exponential_base: Base for exponential backoff calculation (default: 2.0)
        jitter: Add random jitter to wait times (default: True)
        retry_on: Tuple of exception types to retry on (default: TRANSIENT_ERRORS)
        on_retry: Optional callback called before each retry with (exception, attempt)

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_attempts=3, min_wait=1, max_wait=30)
        async def connect_to_database():
            ...
    """
    if retry_on is None:
        retry_on = TRANSIENT_ERRORS

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if this is a permanent error
                    if is_permanent_error(e):
                        logger.warning(
                            f"Permanent error on {func.__name__}, not retrying: {e}"
                        )
                        raise

                    # Check if we should retry on this exception type
                    if not isinstance(e, retry_on) and not is_transient_error(e):
                        logger.warning(
                            f"Non-retriable error on {func.__name__}: {e}"
                        )
                        raise

                    # Last attempt - don't retry
                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retries ({max_attempts}) exceeded for {func.__name__}: {e}"
                        )
                        raise

                    # Calculate wait time with exponential backoff
                    wait_time = min(
                        max_wait,
                        max(min_wait, min_wait * (exponential_base ** (attempt - 1)))
                    )

                    # Add jitter (0-50% of wait time)
                    if jitter:
                        wait_time = wait_time * (1 + random.uniform(0, 0.5))

                    logger.info(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} "
                        f"after {wait_time:.2f}s: {e}"
                    )

                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.debug(f"Retry callback error: {callback_error}")

                    await asyncio.sleep(wait_time)

            # Should not reach here, but raise last exception if we do
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected state in retry decorator for {func.__name__}")

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            import time
            last_exception: Optional[Exception] = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if this is a permanent error
                    if is_permanent_error(e):
                        logger.warning(
                            f"Permanent error on {func.__name__}, not retrying: {e}"
                        )
                        raise

                    # Check if we should retry on this exception type
                    if not isinstance(e, retry_on) and not is_transient_error(e):
                        logger.warning(
                            f"Non-retriable error on {func.__name__}: {e}"
                        )
                        raise

                    # Last attempt - don't retry
                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retries ({max_attempts}) exceeded for {func.__name__}: {e}"
                        )
                        raise

                    # Calculate wait time with exponential backoff
                    wait_time = min(
                        max_wait,
                        max(min_wait, min_wait * (exponential_base ** (attempt - 1)))
                    )

                    # Add jitter (0-50% of wait time)
                    if jitter:
                        wait_time = wait_time * (1 + random.uniform(0, 0.5))

                    logger.info(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} "
                        f"after {wait_time:.2f}s: {e}"
                    )

                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.debug(f"Retry callback error: {callback_error}")

                    time.sleep(wait_time)

            # Should not reach here, but raise last exception if we do
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected state in retry decorator for {func.__name__}")

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# =============================================================================
# Connection Pool Health
# =============================================================================

class ConnectionHealth:
    """Track connection health metrics."""

    def __init__(self):
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        self.total_latency_ms: float = 0.0
        self.consecutive_failures: int = 0
        self.last_error: Optional[str] = None

    def record_success(self, latency_ms: float) -> None:
        """Record a successful operation."""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_latency_ms += latency_ms
        self.consecutive_failures = 0

    def record_failure(self, error: Exception) -> None:
        """Record a failed operation."""
        self.total_requests += 1
        self.failed_requests += 1
        self.consecutive_failures += 1
        self.last_error = str(error)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def average_latency_ms(self) -> float:
        """Calculate average latency in milliseconds."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests

    @property
    def status(self) -> str:
        """Determine overall health status."""
        if self.consecutive_failures >= 5:
            return "unhealthy"
        if self.consecutive_failures >= 2 or self.success_rate < 90:
            return "degraded"
        return "healthy"

    def to_dict(self) -> dict:
        """Convert health metrics to dictionary."""
        return {
            "status": self.status,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(self.success_rate, 2),
            "average_latency_ms": round(self.average_latency_ms, 2),
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def retry_on_connection_error(func: Callable[..., T]) -> Callable[..., T]:
    """
    Simple decorator to retry on connection errors with default settings.

    Equivalent to @with_retry() with defaults.
    """
    return with_retry()(func)


def retry_with_longer_backoff(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for operations that need longer backoff (e.g., rate-limited APIs).
    """
    return with_retry(max_attempts=5, min_wait=2.0, max_wait=60.0)(func)


# Export all public symbols
__all__ = [
    "TRANSIENT_ERRORS",
    "PERMANENT_ERRORS",
    "is_transient_error",
    "is_permanent_error",
    "with_retry",
    "retry_on_connection_error",
    "retry_with_longer_backoff",
    "ConnectionHealth",
]
