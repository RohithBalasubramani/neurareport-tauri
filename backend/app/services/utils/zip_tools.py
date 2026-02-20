from __future__ import annotations

import io
import os
import shutil
import zipfile
from pathlib import Path
from typing import Iterable, Optional, Tuple


def _is_safe_member(member: zipfile.ZipInfo) -> bool:
    name = member.filename.replace("\\", "/")
    if name.startswith(("/", "\\")):
        return False
    parts = [p for p in name.split("/") if p and p not in (".", "..")]
    if not parts:
        return False
    if ":" in parts[0]:
        return False
    return not any(p in ("..",) for p in parts)


def _is_within_dir(base_dir: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base_dir)
        return True
    except Exception:
        return False


def detect_zip_root(members: Iterable[str]) -> Optional[str]:
    roots = []
    for m in members:
        p = m.replace("\\", "/")
        if p.endswith("/"):
            p = p[:-1]
        parts = [seg for seg in p.split("/") if seg]
        if not parts:
            continue
        roots.append(parts[0])
    if not roots:
        return None
    first = roots[0]
    if all(r == first for r in roots):
        return first
    return None


def create_zip_from_dir(src_dir: Path, dest_zip: Path, *, include_root: bool = True) -> Path:
    src_dir = Path(src_dir).resolve()
    dest_zip = Path(dest_zip).resolve()
    dest_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(dest_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        base_prefix = src_dir.name if include_root else ""
        for path in src_dir.rglob("*"):
            if path.is_dir():
                continue
            # Skip lock files
            if path.name.startswith(".lock."):
                continue
            rel = path.relative_to(src_dir)
            arcname = f"{base_prefix}/{rel.as_posix()}" if base_prefix else rel.as_posix()
            zf.write(path, arcname=arcname)
    return dest_zip


def extract_zip_to_dir(
    zip_path: Path,
    dest_dir: Path,
    *,
    strip_root: bool = True,
    max_entries: int | None = None,
    max_uncompressed_bytes: int | None = None,
    max_file_bytes: int | None = None,
) -> Tuple[Path, str]:
    """
    Extract zip into dest_dir safely. Returns (extracted_root, root_name_in_zip).
    If strip_root is True and the zip has a single top-level folder, the contents of that
    folder are extracted directly under dest_dir. Otherwise, members are extracted with their
    original paths.
    """
    dest_dir = Path(dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    base_dir = dest_dir.resolve()

    with zipfile.ZipFile(zip_path, mode="r") as zf:
        members = list(zf.infolist())
        file_members = [member for member in members if not member.is_dir()]

        unsafe_members = [member.filename for member in members if not _is_safe_member(member)]
        if unsafe_members:
            sample = ", ".join(unsafe_members[:5])
            suffix = f" (+{len(unsafe_members) - 5} more)" if len(unsafe_members) > 5 else ""
            raise ValueError(f"Zip contains unsafe members: {sample}{suffix}")

        if max_entries is not None and len(file_members) > max_entries:
            raise ValueError(f"Zip contains {len(file_members)} files, exceeds limit {max_entries}")

        if max_uncompressed_bytes is not None:
            total_uncompressed = sum(member.file_size for member in file_members)
            if total_uncompressed > max_uncompressed_bytes:
                raise ValueError(
                    f"Zip uncompressed size {total_uncompressed} bytes exceeds limit {max_uncompressed_bytes}"
                )

        if max_file_bytes is not None:
            for member in file_members:
                if member.file_size > max_file_bytes:
                    raise ValueError(
                        f"Zip member {member.filename} size {member.file_size} exceeds limit {max_file_bytes}"
                    )

        root = detect_zip_root(m.filename for m in members)
        for member in members:
            name = member.filename.replace("\\", "/")
            if strip_root and root and name.startswith(root + "/"):
                rel = name[len(root) + 1 :]
            else:
                rel = name
            if not rel:
                continue
            target = dest_dir / rel
            if not _is_within_dir(base_dir, target):
                raise ValueError(f"Zip member {member.filename} would extract outside {base_dir}")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member, "r") as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
    return dest_dir, (root or "")
