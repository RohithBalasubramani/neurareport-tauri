# mypy: ignore-errors
from __future__ import annotations

from html.parser import HTMLParser


class _SimpleTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table_depth = 0
        self._collecting = False
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._collecting = True
                self._current_table = []
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
                self._current_row = None
        elif tag == "table":
            if self._table_depth == 1 and self._collecting and self._current_table is not None:
                self.tables.append(self._current_table[:])
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


__all__ = ["extract_first_table", "extract_tables"]
