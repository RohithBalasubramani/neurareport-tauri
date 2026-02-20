from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterable

from backend.app.services.utils import write_json_atomic

_MAPPING_KEYS_FILENAME = "mapping_keys.json"


def mapping_keys_path(template_dir: Path) -> Path:
    return template_dir / _MAPPING_KEYS_FILENAME


def normalize_key_tokens(raw: Iterable[str] | None) -> list[str]:
    if raw is None:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for item in raw:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def load_mapping_keys(template_dir: Path) -> list[str]:
    path = mapping_keys_path(template_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if isinstance(data, dict):
        raw_keys = data.get("keys")
    elif isinstance(data, list):
        raw_keys = data
    else:
        raw_keys = None
    return normalize_key_tokens(raw_keys if isinstance(raw_keys, Iterable) else None)


def write_mapping_keys(template_dir: Path, keys: Iterable[str]) -> list[str]:
    normalized = normalize_key_tokens(keys)
    path = mapping_keys_path(template_dir)
    payload = {
        "keys": normalized,
        "updated_at": int(time.time()),
    }
    write_json_atomic(path, payload, ensure_ascii=False, indent=2, step="mapping_keys")
    return normalized
