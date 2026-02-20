from __future__ import annotations

import importlib
import re
import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from backend.legacy.core.config import EXCEL_UPLOAD_ROOT, UPLOAD_ROOT

UPLOAD_KIND_PREFIXES: dict[str, str] = {
    "pdf": "/uploads",
    "excel": "/excel-uploads",
}


def _http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"status": "error", "code": code, "message": message})


def _build_upload_kind_bases() -> dict[str, tuple[Path, str]]:
    return {
        "pdf": (UPLOAD_ROOT.resolve(), UPLOAD_KIND_PREFIXES["pdf"]),
        "excel": (EXCEL_UPLOAD_ROOT.resolve(), UPLOAD_KIND_PREFIXES["excel"]),
    }


def _get_upload_kind_bases() -> dict[str, tuple[Path, str]]:
    """
    Resolve upload roots dynamically so tests can monkeypatch backend.api.UPLOAD_ROOT / EXCEL_UPLOAD_ROOT.
    """
    bases = _build_upload_kind_bases()
    try:
        api_mod = importlib.import_module("backend.api")
    except Exception:
        return bases
    pdf_root = getattr(api_mod, "UPLOAD_ROOT", bases["pdf"][0])
    excel_root = getattr(api_mod, "EXCEL_UPLOAD_ROOT", bases["excel"][0])
    try:
        bases["pdf"] = (Path(pdf_root).resolve(), UPLOAD_KIND_PREFIXES["pdf"])
    except Exception:
        pass
    try:
        bases["excel"] = (Path(excel_root).resolve(), UPLOAD_KIND_PREFIXES["excel"])
    except Exception:
        pass
    return bases


_UPLOAD_KIND_BASES: dict[str, tuple[Path, str]] = _build_upload_kind_bases()
_TEMPLATE_ID_SAFE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{2,180}$")


def normalize_template_id(template_id: str) -> str:
    raw = str(template_id or "").strip()
    candidate = raw.replace("\\", "/").split("/")[-1].strip()
    if not candidate or candidate in {".", ".."}:
        raise _http_error(400, "invalid_template_id", "Invalid template_id format")
    normalized = candidate.lower()
    if _TEMPLATE_ID_SAFE_RE.fullmatch(normalized):
        return normalized
    try:
        return str(uuid.UUID(candidate))
    except (ValueError, TypeError):
        raise _http_error(400, "invalid_template_id", "Invalid template_id format")


def template_dir(template_id: str, *, must_exist: bool = True, create: bool = False, kind: str = "pdf") -> Path:
    normalized_kind = (kind or "pdf").lower()
    bases = _get_upload_kind_bases()
    if normalized_kind not in bases:
        raise _http_error(400, "invalid_template_kind", f"Unsupported template kind: {kind}")

    base_dir = bases[normalized_kind][0]
    tid = normalize_template_id(template_id)

    tdir = (base_dir / tid).resolve()
    if base_dir not in tdir.parents:
        raise _http_error(400, "invalid_template_path", "Invalid template_id path")

    if must_exist and not tdir.exists():
        raise _http_error(404, "template_not_found", "template_id not found")

    if create:
        tdir.mkdir(parents=True, exist_ok=True)

    return tdir


def artifact_url(path: Path | None) -> Optional[str]:
    if path is None:
        return None
    try:
        resolved = path.resolve()
    except Exception:
        return None
    if not resolved.exists():
        return None
    for base_dir, prefix in _get_upload_kind_bases().values():
        try:
            rel = resolved.relative_to(base_dir)
        except ValueError:
            continue
        return f"{prefix}/{rel.as_posix()}"
    return None


def manifest_endpoint(template_id: str, kind: str = "pdf") -> str:
    return (
        f"/excel/{template_id}/artifacts/manifest"
        if (kind or "pdf").lower() == "excel"
        else f"/templates/{template_id}/artifacts/manifest"
    )


def find_reference_pdf(template_dir_path: Path) -> Optional[Path]:
    for name in ("source.pdf", "upload.pdf", "template.pdf", "report.pdf"):
        candidate = template_dir_path / name
        if candidate.exists():
            return candidate
    return None


def find_reference_png(template_dir_path: Path) -> Optional[Path]:
    for name in ("report_final.png", "reference_p1.png", "render_p1.png"):
        candidate = template_dir_path / name
        if candidate.exists():
            return candidate
    return None
