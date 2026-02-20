from __future__ import annotations

import json
import logging
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from filelock import FileLock, Timeout as FileLockTimeout

logger = logging.getLogger("neura.lock")

_LOCK_TTL_SECONDS = 120.0  # 2 minutes — generous for report generation


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


# ── Lock metadata sidecar ──────────────────────────────────────────────


def _write_lock_meta(lock_path: Path, correlation_id: str | None = None) -> None:
    """Write metadata sidecar alongside the lock file."""
    meta_path = Path(str(lock_path) + ".meta")
    meta = {
        "pid": os.getpid(),
        "timestamp": time.time(),
        "correlation_id": correlation_id,
    }
    try:
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
    except OSError:
        pass


def _read_lock_meta(lock_path: Path) -> dict | None:
    meta_path = Path(str(lock_path) + ".meta")
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _remove_lock_meta(lock_path: Path) -> None:
    meta_path = Path(str(lock_path) + ".meta")
    try:
        meta_path.unlink(missing_ok=True)
    except OSError:
        pass


def _is_pid_alive(pid: int) -> bool:
    """Check if a process is still running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _force_remove_lock(lock_path: Path) -> None:
    """Remove a lock file and its metadata sidecar."""
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass
    _remove_lock_meta(lock_path)


def _check_and_break_stale_lock(lock_path: Path, ttl: float = _LOCK_TTL_SECONDS) -> bool:
    """Check if a lock is stale (holder dead or TTL exceeded). Break it if so.
    Returns True if a stale lock was broken."""
    if not lock_path.exists():
        return False

    meta = _read_lock_meta(lock_path)
    if meta is None:
        # No metadata — check file age as fallback
        try:
            age = time.time() - lock_path.stat().st_mtime
        except OSError:
            return False
        if age > ttl:
            logger.warning(
                "stale_lock_broken_no_meta",
                extra={"lock": str(lock_path), "age_s": round(age, 1), "ttl": ttl},
            )
            _force_remove_lock(lock_path)
            return True
        return False

    holder_pid = meta.get("pid")
    lock_age = time.time() - meta.get("timestamp", 0)

    if holder_pid and not _is_pid_alive(holder_pid):
        logger.warning(
            "stale_lock_broken_dead_pid",
            extra={"lock": str(lock_path), "pid": holder_pid, "age_s": round(lock_age, 1)},
        )
        _force_remove_lock(lock_path)
        return True

    if lock_age > ttl:
        logger.warning(
            "stale_lock_broken_ttl",
            extra={"lock": str(lock_path), "pid": holder_pid, "age_s": round(lock_age, 1), "ttl": ttl},
        )
        _force_remove_lock(lock_path)
        return True

    return False


# ── Public lock context managers ────────────────────────────────────────


@contextmanager
def acquire_template_lock(
    template_dir: Path,
    name: str,
    correlation_id: str | None = None,
    timeout: float = 30.0,
) -> Generator[None, None, None]:
    """
    Context manager for template locking.
    Prevents concurrent modifications to the same template.
    Automatically detects and breaks stale locks (dead PID or TTL exceeded).

    Args:
        template_dir: Directory containing the template
        name: Lock name (usually template ID)
        correlation_id: Optional correlation ID for logging
        timeout: Maximum time to wait for lock acquisition

    Raises:
        TemplateLockError: If lock cannot be acquired within timeout
    """
    if not _locks_enabled():
        yield
        return

    lock_path = Path(template_dir) / f".lock.{name}"
    holder = f"pid={os.getpid()}"
    if correlation_id:
        holder = f"{holder},corr={correlation_id}"

    # Check and break stale locks before attempting acquisition
    _check_and_break_stale_lock(lock_path)

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
        # One more stale-check attempt after timeout
        if _check_and_break_stale_lock(lock_path):
            try:
                lock = _acquire_lock(lock_path, timeout=5.0, poll_interval=0.1)
            except FileLockTimeout:
                raise TemplateLockError(
                    f"Failed to acquire template lock '{name}' within {timeout}s (stale lock broken but re-acquire failed).",
                    lock_holder="unknown",
                ) from exc
        else:
            raise TemplateLockError(
                f"Failed to acquire template lock '{name}' within {timeout}s.",
                lock_holder="unknown",
            ) from exc

    # Write metadata sidecar so stale detection works for future callers
    _write_lock_meta(lock_path, correlation_id)

    try:
        yield
    finally:
        lock.release()
        _remove_lock_meta(lock_path)


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

    # Check and break stale locks before attempting acquisition
    _check_and_break_stale_lock(lock_path)

    try:
        lock = _acquire_lock(lock_path, timeout=timeout, poll_interval=0.1)
        acquired = True
    except FileLockTimeout:
        acquired = False

    if acquired:
        _write_lock_meta(lock_path, correlation_id)

    try:
        yield acquired
    finally:
        if acquired:
            lock.release()
            _remove_lock_meta(lock_path)
