"""Helpers for SQL safety checks."""
from __future__ import annotations

import re

WRITE_KEYWORDS = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "MERGE",
    "GRANT",
    "REVOKE",
    "COMMENT",
    "RENAME",
    "VACUUM",
    "ATTACH",
    "DETACH",
)

WRITE_PATTERN = re.compile(r"\b(" + "|".join(WRITE_KEYWORDS) + r")\b", re.IGNORECASE)


def _strip_literals_and_comments(sql: str) -> str:
    """Remove string literals and comments for safer keyword scanning."""
    if not sql:
        return ""

    out = []
    in_single = False
    in_double = False
    in_line_comment = False
    in_block_comment = False
    i = 0

    while i < len(sql):
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < len(sql) else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                out.append(" ")
            i += 1
            continue

        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                out.append(" ")
                continue
            i += 1
            continue

        if not in_single and not in_double:
            if ch == "-" and nxt == "-":
                in_line_comment = True
                i += 2
                continue
            if ch == "/" and nxt == "*":
                in_block_comment = True
                i += 2
                continue

        if not in_double and ch == "'":
            if in_single and nxt == "'":
                # Escaped single quote ('') inside single-quoted string — skip both
                out.append(" ")
                out.append(" ")
                i += 2
                continue
            in_single = not in_single
            out.append(" ")
            i += 1
            continue

        if not in_single and ch == '"':
            if in_double and nxt == '"':
                # Escaped double quote ("") inside double-quoted string — skip both
                out.append(" ")
                out.append(" ")
                i += 2
                continue
            in_double = not in_double
            out.append(" ")
            i += 1
            continue

        if in_single or in_double:
            out.append(" ")
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def get_write_operation(sql: str | None) -> str | None:
    """Return the first detected write operation keyword, if any."""
    cleaned = _strip_literals_and_comments(sql or "")
    match = WRITE_PATTERN.search(cleaned)
    return match.group(1).upper() if match else None


def is_select_or_with(sql: str | None) -> bool:
    cleaned = _strip_literals_and_comments(sql or "")
    leading = cleaned.lstrip().upper()
    if not (leading.startswith("SELECT") or leading.startswith("WITH")):
        return False
    # Reject if the query body contains write keywords (e.g. after a semicolon)
    if get_write_operation(sql) is not None:
        return False
    return True
