from __future__ import annotations

import contextlib
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger("neura.fs")


def _maybe_fail(step: str | None) -> None:
    fail_after = os.getenv("NEURA_FAIL_AFTER_STEP")
    if step and fail_after and fail_after.strip().lower() == step.strip().lower():
        raise RuntimeError(f"Simulated failure after step '{step}'")


def write_text_atomic(path: Path, data: str | bytes, *, encoding: str = "utf-8", step: str | None = None) -> None:
    """
    Persist text to `path` atomically:
      1. Write to a temp file within the same directory.
      2. Flush + fsync to guarantee contents on disk.
      3. Replace the target path.
    """
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    tmp_path = Path(tmp_name)
    binary = isinstance(data, (bytes, bytearray))
    try:
        if binary:
            with os.fdopen(fd, "wb") as tmp_file:
                tmp_file.write(data)  # type: ignore[arg-type]
                tmp_file.flush()
                with contextlib.suppress(OSError):
                    os.fsync(tmp_file.fileno())
        else:
            with os.fdopen(fd, "w", encoding=encoding, newline="") as tmp_file:
                tmp_file.write(data)  # type: ignore[arg-type]
                tmp_file.flush()
                with contextlib.suppress(OSError):
                    os.fsync(tmp_file.fileno())
        _maybe_fail(step)
        tmp_path.replace(path)
    except Exception:
        logger.exception("atomic_write_failed", extra={"path": str(path)})
        raise
    finally:
        with contextlib.suppress(FileNotFoundError):
            tmp_path.unlink()


def write_json_atomic(
    path: Path,
    payload: Any,
    *,
    encoding: str = "utf-8",
    indent: int | None = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
    step: str | None = None,
) -> None:
    """
    Serialize payload to JSON and write atomically.
    Mirrors json.dumps kwargs with sensible defaults for readability.
    """
    data = json.dumps(
        payload,
        indent=indent,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
    )
    write_text_atomic(path, data, encoding=encoding, step=step)
