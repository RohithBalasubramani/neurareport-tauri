from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from backend.app.utils.fs import write_json_atomic

logger = logging.getLogger("neura.artifacts")

MANIFEST_NAME = "artifact_manifest.json"
MANIFEST_SCHEMA_VERSION = "1.0"


def compute_checksums(files: Mapping[str, Path]) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for name, path in files.items():
        if not path.exists():
            continue
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                h.update(chunk)
        checksums[name] = h.hexdigest()
    return checksums


def write_artifact_manifest(
    template_dir: Path,
    *,
    step: str,
    files: Mapping[str, Path],
    inputs: Iterable[str],
    correlation_id: str | None = None,
) -> Path:
    """
    Persist artifact manifest alongside template artifacts.
    """
    template_dir = template_dir.resolve()
    manifest_path = template_dir / MANIFEST_NAME

    existing_payload: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            existing_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception(
                "manifest_read_failed",
                extra={"event": "manifest_read_failed", "path": str(manifest_path)},
            )
            existing_payload = {}

    existing_files = dict(existing_payload.get("files") or {})
    existing_checksums = dict(existing_payload.get("file_checksums") or {})
    existing_inputs = list(existing_payload.get("input_refs") or [])

    def _store_path(path: Path) -> str:
        try:
            return str(path.resolve().relative_to(template_dir))
        except ValueError:
            return str(path)

    merged_files = existing_files | {name: _store_path(path) for name, path in files.items()}
    new_checksums = compute_checksums(files)
    merged_checksums = existing_checksums | new_checksums

    input_list = list(inputs)
    merged_inputs: list[str] = []
    for item in existing_inputs + input_list:
        if item not in merged_inputs:
            merged_inputs.append(item)

    payload = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "files": merged_files,
        "file_checksums": merged_checksums,
        "input_refs": merged_inputs,
        "correlation_id": correlation_id,
        "pid": os.getpid(),
    }
    write_json_atomic(manifest_path, payload, indent=2, ensure_ascii=False, sort_keys=True, step="artifact_manifest")
    logger.info(
        "artifact_manifest_written",
        extra={
            "event": "artifact_manifest_written",
            "template_dir": str(template_dir),
            "step": step,
            "correlation_id": correlation_id,
        },
    )
    return manifest_path


def load_manifest(template_dir: Path) -> dict | None:
    path = template_dir / MANIFEST_NAME
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.exception(
            "manifest_load_failed",
            extra={"event": "manifest_load_failed", "path": str(path)},
        )
        return None
