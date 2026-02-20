from __future__ import annotations

import json
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Mapping, Optional, Callable

from fastapi import HTTPException

from backend.app.repositories.state import state_store
from backend.app.services.config import get_settings
from backend.app.services.utils import write_json_atomic
from backend.legacy.utils.schedule_utils import utcnow_iso
from backend.legacy.utils.template_utils import artifact_url, template_dir, normalize_template_id

logger = logging.getLogger(__name__)

_DEFAULT_VERIFY_PDF_BYTES: int | None = None
_TEMPLATE_ID_SAFE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{2,180}$")


def format_bytes(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} bytes"
    value = num_bytes / 1024
    unit = "KiB"
    if value >= 1024:
        value /= 1024
        unit = "MiB"
        if value >= 1024:
            value /= 1024
            unit = "GiB"
    human = f"{value:.1f}".rstrip("0").rstrip(".")
    return f"{human} {unit}"


def resolve_pdf_upload_limit(default: int | None = _DEFAULT_VERIFY_PDF_BYTES) -> int | None:
    if default is None:
        default = int(get_settings().max_verify_pdf_bytes)
    if default <= 0:
        return None
    return default


MAX_VERIFY_PDF_BYTES = resolve_pdf_upload_limit()


def slugify_template_name(value: str | None) -> str:
    raw = str(value or "").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug[:60].strip("-")


def template_id_exists(template_id: str, *, kind: str = "pdf") -> bool:
    try:
        template_dir(template_id, must_exist=True, create=False, kind=kind)
        return True
    except HTTPException:
        return False


def generate_template_id(base_name: str | None = None, *, kind: str = "pdf") -> str:
    slug = slugify_template_name(base_name)
    if not slug:
        slug = "template"
    for _ in range(10):
        suffix = uuid.uuid4().hex[:6]
        candidate = f"{slug}-{suffix}"
        if _TEMPLATE_ID_SAFE_RE.fullmatch(candidate) and not template_id_exists(candidate, kind=kind):
            return candidate
    fallback = f"{slug}-{uuid.uuid4().hex[:10]}"
    if _TEMPLATE_ID_SAFE_RE.fullmatch(fallback) and not template_id_exists(fallback, kind=kind):
        return fallback
    return uuid.uuid4().hex


def http_error(status_code: int, code: str, message: str, details: str | None = None) -> HTTPException:
    payload = {"status": "error", "code": code, "message": message}
    if details:
        payload["details"] = details
    return HTTPException(status_code=status_code, detail=payload)


def template_history_path(template_dir_path: Path) -> Path:
    return template_dir_path / "template_history.json"


def _truncate_history(entries: list[dict], limit: int = 2) -> list[dict]:
    if limit <= 0:
        return []
    if len(entries) <= limit:
        return entries
    return entries[-limit:]


def read_template_history(template_dir_path: Path) -> list[dict]:
    path = template_history_path(template_dir_path)
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(raw, list):
        return []
    cleaned = [entry for entry in raw if isinstance(entry, dict)]
    return _truncate_history(cleaned)


def append_template_history_entry(template_dir_path: Path, entry: dict) -> list[dict]:
    history = read_template_history(template_dir_path)
    history.append(entry)
    history = _truncate_history(history)
    write_json_atomic(
        template_history_path(template_dir_path),
        history,
        ensure_ascii=False,
        indent=2,
        step="template_history",
    )
    return history


def load_template_generator_summary(template_id: str) -> dict[str, Any]:
    record = state_store.get_template_record(template_id) or {}
    generator = record.get("generator") or {}
    raw_summary = generator.get("summary") or {}
    if isinstance(raw_summary, dict):
        return dict(raw_summary)
    return {}


def update_template_generator_summary_for_edit(
    template_id: str,
    *,
    edit_type: str,
    notes: str | None = None,
) -> dict[str, Any]:
    summary = load_template_generator_summary(template_id)
    now_iso = utcnow_iso()
    summary["lastEditType"] = edit_type
    summary["lastEditAt"] = now_iso
    if notes is not None:
        summary["lastEditNotes"] = notes
    state_store.update_template_generator(template_id, summary=summary)
    return summary


def normalize_artifact_map(artifacts: Mapping[str, Any] | None, artifact_url_fn: Callable[[Path | str | None], Optional[str]] = artifact_url) -> dict[str, str]:
    normalized: dict[str, str] = {}
    if not artifacts:
        return normalized
    for name, raw in artifacts.items():
        url = None
        if isinstance(raw, Path):
            url = artifact_url_fn(raw)
        elif isinstance(raw, str):
            url = raw if raw.startswith("/") else artifact_url_fn(Path(raw))
        if url:
            normalized[str(name)] = url
    return normalized


def resolve_template_kind(template_id: str) -> str:
    from backend.legacy.utils.template_utils import UPLOAD_KIND_PREFIXES

    record = state_store.get_template_record(template_id) or {}
    kind = str(record.get("kind") or "").lower()
    if kind in UPLOAD_KIND_PREFIXES:
        return kind
    normalized = normalize_template_id(template_id)
    tdir = template_dir(normalized, kind="excel", must_exist=False, create=False)
    return "excel" if tdir.exists() else "pdf"


def ensure_template_exists(template_id: str, *, kind: str = "pdf") -> Path:
    return template_dir(template_id, must_exist=True, create=False, kind=kind)
