# mypy: ignore-errors
"""
Shared helpers for report generation (PDF + Excel).

The functions here are intentionally self-contained so the two generator
implementations can import and reuse them without duplicating logic.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Callable, Iterable

_TOKEN_REGEX_CACHE: dict[str, re.Pattern[str]] = {}
_TR_BLOCK_RE = re.compile(r"(?is)<tr\b[^>]*>.*?</tr>")
_BATCH_BLOCK_ANY_TAG = re.compile(
    r"(?is)"
    r"<(?P<tag>section|div|article|main|tbody|tr)\b"
    r'[^>]*\bclass\s*=\s*["\'][^"\']*\bbatch-block\b[^"\']*["\']'
    r"[^>]*>"
    r"(?P<inner>.*?)"
    r"</(?P=tag)>"
)


def _token_regex(token: str) -> re.Pattern[str]:
    cleaned = (token or "").strip()
    if not cleaned:
        raise ValueError("Token must be a non-empty string")
    cached = _TOKEN_REGEX_CACHE.get(cleaned)
    if cached is None:
        cached = re.compile(rf"\{{\{{?\s*{re.escape(cleaned)}\s*\}}\}}?")
        _TOKEN_REGEX_CACHE[cleaned] = cached
    return cached


def _segment_has_any_token(segment: str, tokens: Iterable[str]) -> bool:
    for token in tokens:
        if not token:
            continue
        if _token_regex(token).search(segment):
            return True
    return False


def _find_rowish_block(html_text: str, row_tokens: Iterable[str]) -> tuple[str, int, int] | None:
    candidate_tokens = [tok for tok in row_tokens if isinstance(tok, str) and tok.strip()]
    if not candidate_tokens:
        return None

    matches = [m for m in _TR_BLOCK_RE.finditer(html_text) if _segment_has_any_token(m.group(0), candidate_tokens)]
    if not matches:
        return None

    prototype = matches[0].group(0).strip()
    start_index = matches[0].start()
    end_index = matches[-1].end()
    return prototype, start_index, end_index


def _find_or_infer_batch_block(html_text: str) -> tuple[str, str, str]:
    """
    Return (full_match, tag_name, inner_html) of the repeating unit.
    Preference order:
      1) Any element with class="batch-block"
      2) First <tr> inside the first <tbody>
      3) First row-like <div> (class includes row|item|card)
      4) First large container (<section|main|div|article> under <body>)
    """
    m = _BATCH_BLOCK_ANY_TAG.search(html_text)
    if m:
        return m.group(0), m.group("tag").lower(), m.group("inner")

    m_tbody = re.search(r"(?is)<tbody\b[^>]*>(?P<body>.*?)</tbody>", html_text)
    if m_tbody:
        tbody = m_tbody.group("body")
        m_tr = re.search(r"(?is)<tr\b[^>]*>(?P<tr>.*?)</tr>", tbody)
        if m_tr:
            return m_tr.group(0), "tr", m_tr.group("tr")

    m_div = re.search(r"(?is)<div\b[^>]*\b(row|item|card)\b[^>]*>(?P<inner>.*?)</div>", html_text)
    if m_div:
        return m_div.group(0), "div", m_div.group("inner")

    m_body = re.search(r"(?is)<body\b[^>]*>(?P<body>.*?)</body>", html_text)
    if m_body:
        body = m_body.group("body")
        m_cont = re.search(r"(?is)<(section|main|div|article)\b[^>]*>(?P<inner>.*?)</\1>", body)
        if m_cont:
            return m_cont.group(0), m_cont.group(1).lower(), m_cont.group("inner")

    raise RuntimeError("No explicit batch-block and no suitable repeating unit could be inferred.")


def _select_prototype_block(html_text: str, row_tokens: Iterable[str]) -> tuple[str, int, int]:
    explicit_blocks = list(_BATCH_BLOCK_ANY_TAG.finditer(html_text))
    if explicit_blocks:
        chosen_match = explicit_blocks[0]
        if row_tokens:
            for match in explicit_blocks:
                if _segment_has_any_token(match.group(0), row_tokens):
                    chosen_match = match
                    break
        prototype = chosen_match.group(0).strip()
        start0 = explicit_blocks[0].start()
        end_last = explicit_blocks[-1].end()
        return prototype, start0, end_last

    rowish = _find_rowish_block(html_text, row_tokens)
    if rowish:
        return rowish

    block_full, tag_name, _ = _find_or_infer_batch_block(html_text)

    # --- Additive: for header-only templates (no row_tokens), use the full
    #     containing element (e.g. entire <tbody>) instead of just one <tr>.
    #     This keeps all header-token <tr> rows inside the prototype block
    #     so they get filled together rather than being left in the shell. ---
    row_token_list = list(row_tokens) if row_tokens else []
    if not row_token_list and tag_name == "tr":
        m_tbody = re.search(r"(?is)<tbody\b[^>]*>.*?</tbody>", html_text)
        if m_tbody:
            block_full = m_tbody.group(0)

    start0 = html_text.find(block_full)
    if start0 < 0:
        raise RuntimeError("Inferred batch block could not be located in HTML via .find()")
    end_last = start0 + len(block_full)
    return block_full.strip(), start0, end_last


def _strip_found_block(html_text: str, block_full: str, block_tag: str) -> str:
    """Remove the found/inferred block once (used to build shell)."""
    return html_text.replace(block_full, "", 1)


def html_without_batch_blocks(html_text: str) -> str:
    """Legacy stripper kept for compatibility."""
    pat = re.compile(r'(?is)\s*<section\s+class=["\']batch-block["\']\s*>.*?</section>\s*')
    return pat.sub("", html_text)


def _raise_no_block(html: str, cause: Exception | None = None) -> None:
    """Build a short <section ...> preview and raise ValueError from here."""
    sec_tags = re.findall(r"(?is)<section\b[^>]*>", html)
    preview_lines = []
    for i, t in enumerate(sec_tags[:12]):
        snip = t[:140].replace("\n", " ")
        preview_lines.append(f'{i+1:02d}: {snip}{" ..." if len(t) > 140 else ""}')
    preview = "\n".join(preview_lines)
    msg = (
        "Could not find any <section class='batch-block'> blocks and no suitable fallback could be inferred.\n"
        "First few <section> tags present:\n" + preview
    )
    raise ValueError(msg) from cause


def _parse_date_like(value) -> datetime | None:
    if value is None:
        return None
    val = str(value).strip()
    if not val:
        return None

    iso_try = val.replace("Z", "+00:00")
    if " " in iso_try and "T" not in iso_try:
        iso_try = iso_try.replace(" ", "T", 1)
    try:
        return datetime.fromisoformat(iso_try)
    except ValueError:
        pass

    if re.fullmatch(r"\d{10,}", val):
        try:
            seconds = int(val)
            if len(val) > 10:
                scale = 10 ** (len(val) - 10)
                return datetime.fromtimestamp(seconds / scale, tz=timezone.utc)
            return datetime.fromtimestamp(seconds, tz=timezone.utc)
        except ValueError:
            pass

    try:
        from email.utils import parsedate_to_datetime
    except ImportError:  # pragma: no cover
        parsedate_to_datetime = None  # type: ignore

    if parsedate_to_datetime is not None:
        try:
            dt = parsedate_to_datetime(val)
            if dt:
                return dt if dt.tzinfo is None else dt.astimezone()
        except (TypeError, ValueError):
            pass

    candidates = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%d.%m.%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d %Y",
        "%B %d %Y",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y %H:%M:%S",
        "%d %b %Y %H:%M",
        "%d %b %Y %H:%M:%S",
        "%d %B %Y %H:%M",
        "%d %B %Y %H:%M:%S",
        "%b %d %Y %H:%M",
        "%b %d %Y %H:%M:%S",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None


def _has_time_component(raw_value, dt_obj: datetime | None) -> bool:
    if dt_obj and (dt_obj.hour or dt_obj.minute or dt_obj.second or dt_obj.microsecond):
        return True
    if raw_value is None:
        return False
    text = str(raw_value)
    if re.search(r"\d{1,2}:\d{2}", text):
        return True
    if re.search(r"\b(am|pm)\b", text, flags=re.IGNORECASE):
        return True
    if "T" in text or "t" in text:
        return True
    return False


def _format_for_token(token: str, dt_obj: datetime | None, include_time_default: bool = False) -> str:
    if not dt_obj:
        return ""

    token_lower = token.lower()
    token_clean = re.sub(r"[^a-z0-9]", "", token_lower)

    def _has(*needles: str) -> bool:
        return any(needle in token_clean for needle in needles)

    include_time = include_time_default or _has("time", "clock", "datetime", "timestamp")
    include_seconds = _has("second", "seconds", "sec", "timestamp", "precise", "fulltime")
    use_ampm = _has("ampm", "12h", "twelvehour")
    if include_seconds and not include_time:
        include_time = True
    if use_ampm and not include_time:
        include_time = True

    include_timezone = _has("timezone", "tz", "utc", "offset", "gmtoffset", "withtz", "withzone", "zulu")
    iso_like = _has("iso", "iso8601", "ymd", "rfc3339")
    rfc822_like = _has("rfc2822", "rfc822")
    http_like = _has("httpdate", "rfc7231")
    compact_like = _has("compact", "slug", "filename", "filestamp", "yyyymmdd", "numeric", "digits")
    us_like = _has("us", "usa", "mdy", "mmdd")
    dashed_like = _has("dash", "hyphen")
    long_like = _has("long", "verbose", "friendly", "pretty", "human")
    short_like = _has("short", "abbr", "mini", "brief")
    month_long_like = _has("monthname", "monthlong")
    month_short_like = _has("monthabbr", "monthshort")
    weekday_like = _has("weekday", "dayname")
    weekday_short = _has("weekdayshort", "weekdayabbr", "daynameshort")
    epoch_ms_like = _has("epochms", "millis", "milliseconds", "unixms")
    epoch_like = _has("epoch", "unixtime", "unix")

    dt_for_format = dt_obj
    if include_timezone and dt_for_format.tzinfo is None:
        try:
            dt_for_format = dt_for_format.astimezone()
        except ValueError:
            pass

    if epoch_ms_like:
        try:
            return str(int(dt_for_format.timestamp() * 1000))
        except (OSError, OverflowError, ValueError):
            pass
    if epoch_like:
        try:
            return str(int(dt_for_format.timestamp()))
        except (OSError, OverflowError, ValueError):
            pass

    if rfc822_like or http_like:
        try:
            from email.utils import format_datetime as _email_format_datetime

            base_dt = dt_for_format
            if base_dt.tzinfo is None:
                base_dt = base_dt.astimezone()
            return _email_format_datetime(base_dt)
        except Exception:
            pass

    if iso_like:
        dt_use = dt_for_format
        if include_time:
            timespec = "seconds" if include_seconds else "minutes"
            try:
                return dt_use.isoformat(timespec=timespec)
            except TypeError:
                return dt_use.isoformat()
        return dt_use.date().isoformat()

    if compact_like:
        date_part = dt_for_format.strftime("%Y%m%d")
        if include_time:
            if use_ampm:
                time_fmt = "%I%M%S%p" if include_seconds else "%I%M%p"
            else:
                time_fmt = "%H%M%S" if include_seconds else "%H%M"
            date_part = f"{date_part}_{dt_for_format.strftime(time_fmt)}"
        if include_timezone:
            tz = dt_for_format.strftime("%z")
            if tz:
                date_part = f"{date_part}{tz}"
        return date_part

    date_part = "%d/%m/%Y"
    if us_like:
        date_part = "%m/%d/%Y"
    elif dashed_like:
        date_part = "%d-%m-%Y"
    elif long_like:
        date_part = "%B %d, %Y"
    elif short_like or month_short_like:
        date_part = "%d %b %Y"
    elif month_long_like:
        date_part = "%d %B %Y"

    if weekday_like:
        prefix = "%a, " if weekday_short else "%A, "
        date_part = prefix + date_part

    fmt = date_part
    if include_time:
        if use_ampm:
            time_fmt = "%I:%M:%S %p" if include_seconds else "%I:%M %p"
        else:
            time_fmt = "%H:%M:%S" if include_seconds else "%H:%M"
        fmt = f"{fmt} {time_fmt}"
    if include_timezone:
        fmt = f"{fmt} %Z".strip()

    try:
        rendered = dt_for_format.strftime(fmt).strip()
        if not rendered and "%Z" in fmt:
            rendered = dt_for_format.strftime(fmt.replace("%Z", "%z")).strip()
        return rendered
    except Exception:
        if include_time:
            try:
                return dt_for_format.isoformat(timespec="seconds")
            except TypeError:
                return dt_for_format.isoformat()
        return dt_for_format.date().isoformat()


STYLE_OR_SCRIPT_RE = re.compile(r"(?is)(<style\b[^>]*>.*?</style>|<script\b[^>]*>.*?</script>)")


def _apply_outside_styles_scripts(html_in: str, transform_fn: Callable[[str], str]) -> str:
    parts = STYLE_OR_SCRIPT_RE.split(html_in)
    for i in range(len(parts)):
        if i % 2 == 0:
            parts[i] = transform_fn(parts[i])
    return "".join(parts)


def _sub_token_text(text: str, token: str, val: str) -> str:
    pat = re.compile(r"(\{\{\s*" + re.escape(token) + r"\s*\}\}|\{\s*" + re.escape(token) + r"\s*\})")
    return pat.sub(val, text)


def sub_token(html_in: str, token: str, val: str) -> str:
    return _apply_outside_styles_scripts(html_in, lambda txt: _sub_token_text(txt, token, val))


def _blank_known_tokens_text(text: str, tokens) -> str:
    for t in tokens:
        text = re.sub(r"\{\{\s*" + re.escape(t) + r"\s*\}\}", "", text)
        text = re.sub(r"\{\s*" + re.escape(t) + r"\s*\}", "", text)
    return text


def blank_known_tokens(html_in: str, tokens) -> str:
    return _apply_outside_styles_scripts(html_in, lambda txt: _blank_known_tokens_text(txt, tokens))


def _convert_css_length_to_mm(raw: str) -> float | None:
    if not raw:
        return None
    text = raw.strip().lower()
    if not text or text == "auto":
        return None
    m = re.match(r"([-+]?\d*\.?\d+)\s*(mm|cm|in|pt|pc|px)?", text)
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2) or "px"
    if unit == "mm":
        return value
    if unit == "cm":
        return value * 10.0
    if unit in {"in", "inch", "inches"}:
        return value * 25.4
    if unit == "pt":
        return value * (25.4 / 72.0)
    if unit == "pc":
        return value * (25.4 / 6.0)
    if unit == "px":
        return value * (25.4 / 96.0)
    return None


def _parse_page_size_value(value: str) -> tuple[float, float] | None:
    if not value:
        return None
    text = value.strip().lower()
    if not text:
        return None
    size_map = {
        "a0": (841.0, 1189.0),
        "a1": (594.0, 841.0),
        "a2": (420.0, 594.0),
        "a3": (297.0, 420.0),
        "a4": (210.0, 297.0),
        "a5": (148.0, 210.0),
        "letter": (215.9, 279.4),
        "legal": (215.9, 355.6),
        "tabloid": (279.4, 431.8),
    }
    orientation = None
    tokens = [t for t in re.split(r"\s+", text) if t]
    size_tokens = tokens
    if tokens and tokens[-1] in {"portrait", "landscape"}:
        orientation = tokens[-1]
        size_tokens = tokens[:-1]
    if len(size_tokens) == 1 and size_tokens[0] in size_map:
        width_mm, height_mm = size_map[size_tokens[0]]
    elif len(size_tokens) >= 2:
        first = _convert_css_length_to_mm(size_tokens[0])
        second = _convert_css_length_to_mm(size_tokens[1])
        if first is None or second is None:
            return None
        width_mm, height_mm = first, second
    else:
        return None
    if orientation == "landscape":
        width_mm, height_mm = height_mm, width_mm
    return width_mm, height_mm


def _parse_margin_shorthand(value: str) -> tuple[float | None, float | None, float | None, float | None]:
    parts = [p for p in re.split(r"\s+", value.strip()) if p]
    values = [_convert_css_length_to_mm(p) for p in parts]
    if not values:
        return None, None, None, None
    if len(values) == 1:
        top = right = bottom = left = values[0]
    elif len(values) == 2:
        top = bottom = values[0]
        right = left = values[1]
    elif len(values) == 3:
        top = values[0]
        right = left = values[1]
        bottom = values[2]
    else:
        top, right, bottom, left = values[:4]
    return top, right, bottom, left


def _extract_page_metrics(html_in: str) -> dict[str, float]:
    default_width_mm, default_height_mm = 210.0, 297.0
    margin_top_mm = 0.0
    margin_bottom_mm = 0.0
    page_match = re.search(r"@page\b[^{}]*\{(?P<body>.*?)\}", html_in, re.IGNORECASE | re.DOTALL)
    if page_match:
        block = page_match.group("body")
        size_match = re.search(r"size\s*:\s*([^;]+);?", block, re.IGNORECASE)
        if size_match:
            parsed_size = _parse_page_size_value(size_match.group(1))
            if parsed_size:
                default_width_mm, default_height_mm = parsed_size
        margin_match = re.search(r"margin\s*:\s*([^;]+);?", block, re.IGNORECASE)
        if margin_match:
            mt, _, mb, _ = _parse_margin_shorthand(margin_match.group(1))
            if mt is not None:
                margin_top_mm = mt
            if mb is not None:
                margin_bottom_mm = mb
        for name, setter in (("margin-top", "top"), ("margin-bottom", "bottom")):
            specific = re.search(rf"{name}\s*:\s*([^;]+);?", block, re.IGNORECASE)
            if specific:
                as_mm = _convert_css_length_to_mm(specific.group(1))
                if as_mm is None:
                    continue
                if setter == "top":
                    margin_top_mm = as_mm
                else:
                    margin_bottom_mm = as_mm
    return {
        "page_width_mm": default_width_mm,
        "page_height_mm": default_height_mm,
        "margin_top_mm": max(margin_top_mm, 0.0),
        "margin_bottom_mm": max(margin_bottom_mm, 0.0),
    }


# ---------------------------------------------------------------------------
# Additive: date column auto-detection for contracts missing date_columns
# ---------------------------------------------------------------------------

def detect_date_column(db_path, table_name: str) -> str | None:
    """Auto-detect a likely date/timestamp column in *table_name*.

    Strategy:
      1. Name-based: columns containing 'date', 'timestamp', '_dt', '_ts'.
         Prefer 'date' over 'time' when multiple match.
      2. Value-based: sample up to 5 non-null TEXT values and check if they
         parse as dates via ``_parse_date_like``.
      3. Return the column name, or ``None`` if nothing matches.

    This is a safety-net fallback — contracts should specify date_columns
    explicitly whenever possible.
    """
    if not table_name:
        return None

    return _detect_date_column_df(db_path, table_name)


def _detect_date_column_df(db_path, table_name: str) -> str | None:
    """DataFrame-based date column detection — no SQL."""
    from pathlib import Path as _Path

    try:
        from backend.legacy.utils.connection_utils import get_loader_for_ref
        loader = get_loader_for_ref(db_path)
        df = loader.frame(table_name)
    except Exception:
        return None

    if df is None or df.empty:
        return None

    _DATE_PATTERNS = ("date", "timestamp", "_dt", "_ts", "time")
    _PREFER_PATTERNS = ("date",)

    candidates: list[tuple[int, str]] = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pat in col_lower for pat in _DATE_PATTERNS):
            priority = 0 if any(p in col_lower for p in _PREFER_PATTERNS) else 1
            candidates.append((priority, str(col)))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    # Strategy 2: value-based detection
    for col in df.columns:
        col_type = loader.column_type(table_name, str(col))
        if col_type in ("INTEGER", "REAL"):
            continue
        non_null = df[col].dropna()
        if non_null.empty:
            continue
        values = [str(v).strip() for v in non_null.head(5) if str(v).strip()]
        if not values:
            continue
        date_hits = sum(1 for v in values if _parse_date_like(v) is not None)
        if date_hits >= 3 or (date_hits == len(values) and len(values) >= 1):
            return str(col)

    return None


