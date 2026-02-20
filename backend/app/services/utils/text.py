from __future__ import annotations

import json
import re

_FENCE_PATTERN = re.compile(r"^\s*```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)
_FENCE_ANYWHERE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def strip_code_fences(text: str) -> str:
    """
    Remove surrounding markdown code fences (plaintext or ```json```),
    returning the inner payload trimmed. Mirrors the helper previously
    duplicated in mapping modules.
    """
    if not text:
        return ""
    match = _FENCE_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    # Also try fences that appear after prose (no ^ anchor)
    match = _FENCE_ANYWHERE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def extract_json_object(text: str) -> dict | None:
    """Extract a JSON object from LLM text that may contain prose before/after.

    Strategy:
    1. Try strip_code_fences first (handles ```json ... ```)
    2. Try json.loads on the result
    3. Fallback: walk through the string finding each '{' and try to parse
       from that position (handles prose with stray braces like {token_name})
    """
    if not text:
        return None

    cleaned = strip_code_fences(text)

    # Fast path: cleaned text is already valid JSON
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass

    # Walk through finding each '{' and try to parse a complete JSON object
    search_in = cleaned if cleaned != text.strip() else text
    pos = 0
    while True:
        idx = search_in.find("{", pos)
        if idx == -1:
            break
        try:
            obj, end = json.JSONDecoder().raw_decode(search_in, idx)
            if isinstance(obj, dict):
                return obj
        except (json.JSONDecodeError, ValueError):
            pass
        pos = idx + 1

    return None


__all__ = ["strip_code_fences", "extract_json_object"]
