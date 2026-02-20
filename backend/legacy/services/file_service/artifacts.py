from __future__ import annotations

from pathlib import Path
from typing import Callable

from fastapi import HTTPException

from backend.app.services.utils.artifacts import load_manifest
from backend.legacy.utils.template_utils import artifact_url, template_dir


def artifact_manifest_response(
    template_id: str,
    *,
    kind: str = "pdf",
    template_dir_fn: Callable[..., Path] = template_dir,
) -> dict:
    tdir = template_dir_fn(template_id, kind=kind, must_exist=True, create=False)
    manifest = load_manifest(tdir)
    if not manifest:
        raise HTTPException(status_code=404, detail="manifest_not_found")
    manifest = dict(manifest)
    manifest.setdefault("template_id", template_id)
    manifest.setdefault("kind", kind)
    return manifest


def artifact_head_response(
    template_id: str,
    name: str,
    *,
    kind: str = "pdf",
    template_dir_fn: Callable[..., Path] = template_dir,
) -> dict:
    tdir = template_dir_fn(template_id, kind=kind, must_exist=True, create=False)
    target = tdir / name
    if not target.resolve().is_relative_to(tdir.resolve()):
        raise HTTPException(status_code=400, detail="invalid_artifact_name")
    if not target.exists():
        raise HTTPException(status_code=404, detail="artifact_not_found")
    stat = target.stat()
    url = artifact_url(target)
    return {
        "template_id": template_id,
        "kind": kind,
        "name": name,
        "url": url,
        "size": stat.st_size,
        "modified": int(stat.st_mtime),
    }
