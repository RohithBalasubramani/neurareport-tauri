from __future__ import annotations

import re
from typing import List

_DOUBLE_BRACE_PATTERN = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
_TOKEN_PATTERN = re.compile(r"\{\{[^{}]+\}\}|\{[^{}]+\}")
_TOKEN_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_\-\.]*$")


def normalize_token_braces(text: str) -> str:
    """
    Convert double-braced placeholders like ``{{token}}`` into single-braced
    ``{token}`` while leaving existing single-braced tokens untouched.
    Non-token usages (e.g., empty braces) are returned unchanged.
    """
    if not text:
        return text

    def _replace(match: re.Match[str]) -> str:
        inner = match.group(1).strip()
        if not inner:
            return match.group(0)
        return "{" + inner + "}"

    return _DOUBLE_BRACE_PATTERN.sub(_replace, text)


def extract_tokens(html: str) -> List[str]:
    """
    Return a list of token names found in the HTML text.
    Tokens wrapped in either `{token}` or `{{ token }}` are recognized.
    """
    if not html:
        return []
    normalized = normalize_token_braces(html)
    tokens: list[str] = []
    for match in _TOKEN_PATTERN.findall(normalized):
        token = match.strip()
        if token.startswith("{{") and token.endswith("}}"):
            token = token[2:-2]
        elif token.startswith("{") and token.endswith("}"):
            token = token[1:-1]
        token = token.strip()
        if not token:
            continue
        if not _TOKEN_NAME_PATTERN.match(token):
            continue
        tokens.append(token)
    return tokens


__all__ = ["normalize_token_braces", "extract_tokens"]
