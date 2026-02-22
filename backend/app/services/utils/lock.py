from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from filelock import FileLock, Timeout as FileLockTimeout

logger = logging.getLogger("neura.lock")


class TemplateLockError(RuntimeError):
    """Raised when a template lock cannot be acquired."""

    def __init__(self, message: str, lock_holder: Optional[str] = None):
        super().__init__(message)
        self.lock_holder = lock_holder


def _locks_enabled() -> bool:
    disable_flag = os.getenv("NEURA_DISABLE_LOCKS", "").lower()
    if disable_flag in {"1", "true", "yes"}:
        return False
    enable_flag = os.getenv("NEURA_LOCKS_ENABLED", "").lower()
    if enable_flag in {"1", "true", "yes"}:
        return True
    if os.getenv("PYTEST_CURRENT_TEST"):
        return False
    return True


def _acquire_lock(lock_path: Path, *, timeout: float, poll_interval: float) -> FileLock:
    lock = FileLock(str(lock_path))
    lock.acquire(timeout=timeout, poll_interval=poll_interval)
    return lock


class _EagerTemplateLock:
    """Context manager that acquires a file lock eagerly (at construction time).

    Unlike @contextmanager generators which defer to __enter__, this acquires
    the lock immediately so callers can catch TemplateLockError at the call site.
    """

    def __init__(self, lock: FileLock):
        self._lock = lock

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._lock.release()


def acquire_template_lock(
    template_dir: Path,
    name: str,
    correlation_id: str | None = None,
    timeout: float = 900.0,
) -> _EagerTemplateLock:
    """
    Acquire a template lock and return a context manager for releasing it.

    The lock is acquired immediately (not deferred to __enter__), so callers
    can catch TemplateLockError at the call site with try/except.

    Args:
        template_dir: Directory containing the template
        name: Lock name (usually template ID)
        correlation_id: Optional correlation ID for logging
        timeout: Maximum time to wait for lock acquisition

    Raises:
        TemplateLockError: If lock cannot be acquired within timeout
    """
    if not _locks_enabled():
        @contextmanager
        def _noop():
            yield
        return _noop()

    lock_path = Path(template_dir) / f".lock.{name}"
    holder = f"pid={os.getpid()}"
    if correlation_id:
        holder = f"{holder},corr={correlation_id}"

    logger.info(
        "lock_acquiring",
        extra={
            "event": "lock_acquiring",
            "lock": str(lock_path),
            "holder": holder,
            "correlation_id": correlation_id,
        },
    )

    try:
        lock = _acquire_lock(lock_path, timeout=timeout, poll_interval=0.1)
    except FileLockTimeout as exc:
        raise TemplateLockError(
            f"Failed to acquire template lock '{name}' within {timeout}s.",
            lock_holder="unknown",
        ) from exc

    return _EagerTemplateLock(lock)


@contextmanager
def try_acquire_template_lock(
    template_dir: Path,
    name: str,
    correlation_id: str | None = None,
    timeout: float = 5.0,
) -> Generator[bool, None, None]:
    """
    Non-blocking version that yields True if lock acquired, False otherwise.
    Does not raise an exception on failure.
    """
    if not _locks_enabled():
        yield True
        return

    lock_path = Path(template_dir) / f".lock.{name}"
    holder = f"pid={os.getpid()}"
    if correlation_id:
        holder = f"{holder},corr={correlation_id}"

    try:
        lock = _acquire_lock(lock_path, timeout=timeout, poll_interval=0.1)
        acquired = True
    except FileLockTimeout:
        acquired = False

    try:
        yield acquired
    finally:
        if acquired:
            lock.release()
