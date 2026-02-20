"""Email address normalisation and validation utilities.

Provides a single entry-point — ``normalize_email_targets`` — that every
caller must use when accepting email-recipient input.  The function:

1. Splits comma / semicolon-delimited strings.
2. Strips whitespace and SMTP-unsafe control characters.
3. Validates each candidate against ``is_valid_email`` (regex from
   ``backend.app.utils.validation``).
4. Deduplicates (case-insensitive, first-seen casing wins).
5. Enforces an upper bound on recipient count (default 500).
6. Returns **only valid** addresses — invalid entries are logged and
   collected in the optional ``rejected`` out-list.
"""
from __future__ import annotations

import logging
import re
from typing import Iterable, Optional

from backend.app.utils.validation import is_valid_email

logger = logging.getLogger(__name__)

# Control characters that MUST NOT appear in email addresses.
# Newlines (\r, \n) would enable SMTP header injection; NUL bytes cause
# truncation in C-backed mailers.
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")

# RFC 5321 §4.5.3.1 — maximum lengths
_MAX_EMAIL_TOTAL_LENGTH = 254
_MAX_LOCAL_PART_LENGTH = 64

# Absolute upper-bound — any input producing more candidates is truncated
# with a warning.  Callers may pass a lower limit via *max_recipients*.
MAX_RECIPIENTS_HARD_LIMIT = 500


def _is_valid_email_strict(addr: str) -> bool:
    """Format check *and* RFC 5321 length enforcement."""
    if len(addr) > _MAX_EMAIL_TOTAL_LENGTH:
        return False
    at_pos = addr.find("@")
    if at_pos < 0:
        return False
    if at_pos > _MAX_LOCAL_PART_LENGTH:
        return False
    return is_valid_email(addr)


def normalize_email_targets(
    raw: Optional[Iterable[str] | str],
    *,
    max_recipients: int = MAX_RECIPIENTS_HARD_LIMIT,
    validate: bool = True,
    rejected: Optional[list[str]] = None,
) -> list[str]:
    """Normalise, validate, and deduplicate email recipients.

    Parameters
    ----------
    raw:
        ``None``, a single comma/semicolon-delimited string, or an iterable
        of individual address strings.
    max_recipients:
        Upper bound on the number of addresses returned.  Silently truncates
        (with a WARNING log) when exceeded.  Capped internally at
        ``MAX_RECIPIENTS_HARD_LIMIT``.
    validate:
        When ``True`` (default), each candidate is checked with
        ``is_valid_email``; invalid entries are dropped and logged.
        Set to ``False`` only in migration / legacy-compat code paths.
    rejected:
        Optional mutable list.  If provided, every dropped candidate is
        appended here so that the caller can surface feedback.

    Returns
    -------
    list[str]
        De-duplicated list of normalised (and optionally validated) email
        addresses, with original casing preserved (first occurrence wins).
    """
    if raw is None:
        return []

    # 1. Flatten input --------------------------------------------------
    candidates: list[str]
    if isinstance(raw, str):
        candidates = [piece for piece in re.split(r"[;,]", raw) if piece is not None]
    else:
        candidates = list(raw)

    # 2. Clamp max_recipients to hard limit ----------------------------
    effective_limit = min(max(max_recipients, 1), MAX_RECIPIENTS_HARD_LIMIT)

    # 3. Normalise, validate, deduplicate ------------------------------
    normalised: list[str] = []
    seen: set[str] = set()

    for value in candidates:
        text = _CONTROL_CHAR_RE.sub("", str(value or "")).strip()
        if not text:
            continue

        lower = text.lower()
        if lower in seen:
            continue

        if validate and not _is_valid_email_strict(text):
            logger.warning(
                "email_target_rejected",
                extra={"address": _redact_email(text), "reason": "invalid_format"},
            )
            if rejected is not None:
                rejected.append(text)
            continue

        seen.add(lower)
        normalised.append(text)

    # 4. Enforce recipient cap -----------------------------------------
    if len(normalised) > effective_limit:
        logger.warning(
            "email_recipients_truncated",
            extra={
                "original_count": len(normalised),
                "limit": effective_limit,
            },
        )
        normalised = normalised[:effective_limit]

    return normalised


def _redact_email(addr: str) -> str:
    """Redact the local-part of an email for safe logging.

    ``alice@example.com`` → ``a***e@example.com``
    Non-email strings are truncated to 20 chars.
    """
    if "@" in addr:
        local, domain = addr.rsplit("@", 1)
        if len(local) <= 2:
            return f"{'*' * len(local)}@{domain}"
        return f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}@{domain}"
    return addr[:20] + ("…" if len(addr) > 20 else "")
