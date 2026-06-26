# mypy: ignore-errors
from __future__ import annotations

from html.parser import HTMLParser


class _SimpleTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self.thead_counts: list[int] = []
        self._table_depth = 0
        self._collecting = False
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None
        self._in_thead = False
        self._thead_row_count = 0

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._collecting = True
                self._current_table = []
                self._thead_row_count = 0
        elif tag == "thead" and self._collecting:
            self._in_thead = True
        elif tag in ("tbody", "tfoot") and self._collecting:
            self._in_thead = False
        elif self._collecting and tag == "tr":
            self._current_row = []
        elif self._collecting and tag in ("td", "th"):
            self._current_cell = []

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in ("td", "th") and self._collecting and self._current_row is not None:
            text = "".join(self._current_cell or []).strip()
            self._current_row.append(text)
            self._current_cell = None
        elif tag == "tr" and self._collecting:
            if self._current_row is not None:
                if any(cell.strip() for cell in self._current_row):
                    self._current_table.append(self._current_row[:])
                    if self._in_thead:
                        self._thead_row_count += 1
                self._current_row = None
        elif tag == "thead":
            self._in_thead = False
        elif tag == "table":
            if self._table_depth == 1 and self._collecting and self._current_table is not None:
                self.tables.append(self._current_table[:])
                self.thead_counts.append(self._thead_row_count)
                self._collecting = False
                self._current_table = None
            self._table_depth = max(0, self._table_depth - 1)

    def handle_data(self, data: str):
        if self._collecting and self._current_cell is not None:
            self._current_cell.append(data)

    def first_table(self) -> list[list[str]]:
        return self.tables[0] if self.tables else []


def _table_score(table: list[list[str]]) -> int:
    if not table:
        return 0
    row_count = len(table)
    max_cols = max((len(row) for row in table), default=0)
    multi_col_rows = sum(1 for row in table if sum(1 for cell in row if cell) >= 2)
    return (multi_col_rows or row_count) * max(1, max_cols)


def extract_first_table(html_text: str) -> list[list[str]]:
    tables = extract_tables(html_text, max_tables=None)
    if not tables:
        return []
    best_table = tables[0]
    best_score = _table_score(best_table)
    for table in tables[1:]:
        score = _table_score(table)
        if score > best_score:
            best_table = table
            best_score = score
    return best_table


def extract_tables(html_text: str, *, max_tables: int | None = None) -> list[list[list[str]]]:
    parser = _SimpleTableParser()
    parser.feed(html_text or "")
    normalized_tables: list[list[list[str]]] = []
    for table in parser.tables:
        if max_tables is not None and len(normalized_tables) >= max_tables:
            break
        normalized: list[list[str]] = []
        for row in table:
            cleaned = [(cell or "").strip() for cell in row]
            if any(cell for cell in cleaned):
                normalized.append(cleaned)
        if normalized:
            normalized_tables.append(normalized)
    return normalized_tables


def extract_tables_with_header_counts(html_text: str) -> list[tuple[list[list[str]], int]]:
    """Return tables paired with their <thead> row counts."""
    parser = _SimpleTableParser()
    parser.feed(html_text or "")
    result: list[tuple[list[list[str]], int]] = []
    for i, table in enumerate(parser.tables):
        normalized: list[list[str]] = []
        thead_total = parser.thead_counts[i] if i < len(parser.thead_counts) else 0
        skipped_empty = 0
        for row_idx, row in enumerate(table):
            cleaned = [(cell or "").strip() for cell in row]
            if any(cell for cell in cleaned):
                normalized.append(cleaned)
            elif row_idx < thead_total:
                skipped_empty += 1
        if normalized:
            result.append((normalized, max(0, thead_total - skipped_empty)))
    return result


_BG_RE = __import__("re").compile(r"background(?:-color)?\s*:\s*([^;]+)", __import__("re").IGNORECASE)
_FG_RE = __import__("re").compile(r"(?<!-)\bcolor\s*:\s*([^;]+)", __import__("re").IGNORECASE)


def _to_span(value) -> int:
    try:
        n = int(str(value).strip())
        return n if n >= 1 else 1
    except (TypeError, ValueError):
        return 1


def _norm_color(raw: str | None) -> str | None:
    """Normalise a CSS color to an #RRGGBB hex string, else None."""
    if not raw:
        return None
    raw = raw.strip().strip("'\"")
    if not raw:
        return None
    if raw.startswith("#"):
        h = raw[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            return "#" + h.upper()
        return None
    m = __import__("re").match(r"rgba?\(([^)]+)\)", raw, __import__("re").IGNORECASE)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")[:3]]
        try:
            r, g, b = (max(0, min(255, int(float(p)))) for p in parts)
            return "#%02X%02X%02X" % (r, g, b)
        except (ValueError, IndexError):
            return None
    named = {
        "white": "#FFFFFF", "black": "#000000", "red": "#FF0000", "green": "#008000",
        "blue": "#0000FF", "yellow": "#FFFF00", "orange": "#FFA500", "gray": "#808080",
        "grey": "#808080",
    }
    return named.get(raw.lower())


def _cell_colors(style: str | None, bgcolor: str | None):
    bg = fg = None
    if style:
        mb = _BG_RE.search(style)
        if mb:
            bg = _norm_color(mb.group(1))
        mf = _FG_RE.search(style)
        if mf:
            fg = _norm_color(mf.group(1))
    if bg is None and bgcolor:
        bg = _norm_color(bgcolor)
    return bg, fg


class _GridTableParser(HTMLParser):
    """Like _SimpleTableParser but preserves colspan/rowspan, th/td, section, and colors."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[dict] = []
        self._depth = 0
        self._collecting = False
        self._table: dict | None = None
        self._row: list[dict] | None = None
        self._cell: dict | None = None
        self._section: str | None = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "table":
            self._depth += 1
            if self._depth == 1:
                self._collecting = True
                self._table = {"rows": []}
                self._section = None
            return
        if not self._collecting:
            return
        if tag == "thead":
            self._section = "thead"
        elif tag == "tbody":
            self._section = "tbody"
        elif tag == "tfoot":
            self._section = "tfoot"
        elif tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            ad = {k.lower(): (v or "") for k, v in attrs}
            bg, fg = _cell_colors(ad.get("style"), ad.get("bgcolor"))
            self._cell = {
                "_parts": [],
                "colspan": _to_span(ad.get("colspan")),
                "rowspan": _to_span(ad.get("rowspan")),
                "bg": bg,
                "fg": fg,
                "header": tag == "th",
                "section": self._section or ("thead" if tag == "th" else "tbody"),
            }

    def handle_endtag(self, tag):
        tag = tag.lower()
        if not self._collecting:
            if tag == "table":
                self._depth = max(0, self._depth - 1)
            return
        if tag in ("td", "th"):
            if self._cell is not None and self._row is not None:
                self._cell["text"] = "".join(self._cell.pop("_parts")).strip()
                self._row.append(self._cell)
                self._cell = None
        elif tag == "tr":
            if self._row is not None and self._table is not None:
                self._table["rows"].append(self._row)
                self._row = None
        elif tag in ("thead", "tbody", "tfoot"):
            self._section = None
        elif tag == "table":
            if self._depth == 1 and self._table is not None:
                self.tables.append(self._table)
                self._table = None
                self._collecting = False
            self._depth = max(0, self._depth - 1)

    def handle_data(self, data):
        if self._collecting and self._cell is not None:
            self._cell["_parts"].append(data)


def _expand_table_grid(rows: list[list[dict]]):
    """Expand a list of cell-rows into an absolute grid honouring colspan/rowspan.

    Returns (placements, n_rows, n_cols) where each placement is
    (row, col, rowspan, colspan, cell_dict) at absolute 0-based coordinates.
    """
    filled: dict[int, set[int]] = {}
    placements: list[tuple[int, int, int, int, dict]] = []
    n_rows = len(rows)
    for r in range(n_rows):
        filled.setdefault(r, set())
    for r, row in enumerate(rows):
        c = 0
        for cell in row:
            while c in filled[r]:
                c += 1
            cs = cell["colspan"]
            rs = cell["rowspan"]
            for rr in range(r, r + rs):
                filled.setdefault(rr, set())
                for cc in range(c, c + cs):
                    filled[rr].add(cc)
            placements.append((r, c, rs, cs, cell))
            c += cs
    n_cols = max((max(s) + 1 for s in filled.values() if s), default=0)
    return placements, n_rows, n_cols


def extract_table_grids(html_text: str) -> list[dict]:
    """Return top-level tables as grid models with span/section/color info.

    Each table dict: {placements, n_rows, n_cols, thead_count} where
    placements is a list of (row, col, rowspan, colspan, cell) and each cell is
    {text, colspan, rowspan, bg, fg, header, section}.
    """
    parser = _GridTableParser()
    parser.feed(html_text or "")
    out: list[dict] = []
    for tbl in parser.tables:
        rows = tbl["rows"]
        if not rows:
            continue
        placements, n_rows, n_cols = _expand_table_grid(rows)
        thead_count = sum(
            1 for row in rows if row and all(c["section"] == "thead" for c in row)
        )
        out.append({
            "placements": placements,
            "n_rows": n_rows,
            "n_cols": n_cols,
            "thead_count": thead_count,
        })
    return out


def html_has_table_spans(html_text: str) -> bool:
    """True when any cell uses colspan/rowspan > 1 (grouped/merged header)."""
    return bool(
        __import__("re").search(
            r"<t[dh]\b[^>]*\b(?:colspan|rowspan)\s*=\s*['\"]?\s*[2-9]",
            html_text or "",
            __import__("re").IGNORECASE,
        )
    )


__all__ = [
    "extract_first_table",
    "extract_tables",
    "extract_tables_with_header_counts",
    "extract_table_grids",
    "html_has_table_spans",
]
