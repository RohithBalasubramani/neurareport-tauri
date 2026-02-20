# mypy: ignore-errors
"""
Report Context Provider.

Makes report data consumable by agents. This is the bridge layer between
the report system and the agent system.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("neura.reports.context")

# Maximum characters of text content to include (to fit LLM context windows)
DEFAULT_MAX_TEXT_CHARS = 60_000


@dataclass
class ReportContext:
    """All report data an agent needs to analyze a report."""

    run_id: str
    template_id: str
    template_name: str
    template_kind: str
    connection_id: Optional[str]
    connection_name: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    status: str
    created_at: Optional[str]

    html_content: str = ""
    text_content: str = ""
    tables: List[Dict[str, Any]] = field(default_factory=list)
    artifact_urls: Dict[str, Optional[str]] = field(default_factory=dict)
    key_values: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReportContextProvider:
    """
    Service that reads report run records and artifacts, making them
    consumable by agents (text extraction, table parsing, etc.).
    """

    def __init__(self, max_text_chars: int = DEFAULT_MAX_TEXT_CHARS):
        self._max_text_chars = max_text_chars

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_report_context(self, run_id: str) -> Optional[ReportContext]:
        """
        Load full report context for a given run_id.

        Returns None if the run doesn't exist.
        """
        run = self._get_run(run_id)
        if not run:
            return None

        artifacts = run.get("artifacts") or {}
        html_content = ""
        text_content = ""
        tables: List[Dict[str, Any]] = []

        # Try to read the HTML artifact from disk
        html_url = artifacts.get("html_url")
        html_path = self._resolve_artifact_path(html_url)
        if html_path and html_path.is_file():
            try:
                raw_html = html_path.read_text(encoding="utf-8", errors="replace")
                html_content = raw_html
                text_content = self._extract_text_from_html(raw_html)
                tables = self._extract_tables_from_html(raw_html)
            except Exception as exc:
                logger.warning("Failed to read HTML artifact %s: %s", html_path, exc)
        else:
            if html_url:
                logger.warning(
                    "HTML artifact not found on disk for run %s: url=%s resolved=%s",
                    run_id, html_url, html_path,
                )
            else:
                logger.warning("No html_url in artifacts for run %s (keys: %s)", run_id, list(artifacts.keys()))

        # Truncate to fit LLM context
        if len(text_content) > self._max_text_chars:
            text_content = text_content[: self._max_text_chars] + f"\n\n[...truncated at {self._max_text_chars} chars]"

        return ReportContext(
            run_id=run_id,
            template_id=run.get("templateId") or "",
            template_name=run.get("templateName") or "",
            template_kind=run.get("templateKind") or "pdf",
            connection_id=run.get("connectionId"),
            connection_name=run.get("connectionName"),
            start_date=run.get("startDate"),
            end_date=run.get("endDate"),
            status=run.get("status") or "unknown",
            created_at=run.get("createdAt"),
            html_content=html_content,
            text_content=text_content,
            tables=tables,
            artifact_urls={
                "html_url": artifacts.get("html_url"),
                "pdf_url": artifacts.get("pdf_url"),
                "docx_url": artifacts.get("docx_url"),
                "xlsx_url": artifacts.get("xlsx_url"),
            },
            key_values=run.get("keyValues") or {},
            metadata={
                "batch_ids": run.get("batchIds") or [],
                "schedule_id": run.get("scheduleId"),
                "schedule_name": run.get("scheduleName"),
            },
        )

    def get_report_text(self, run_id: str) -> str:
        """Get plain text content of a report (stripped HTML)."""
        ctx = self.get_report_context(run_id)
        return ctx.text_content if ctx else ""

    def get_report_tables(self, run_id: str) -> List[Dict[str, Any]]:
        """Get extracted data tables from a report."""
        ctx = self.get_report_context(run_id)
        return ctx.tables if ctx else []

    def list_recent_reports(
        self,
        template_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """List recent report runs, optionally filtered by template."""
        from backend.app.repositories.state import state_store

        runs = state_store.list_report_runs(
            template_id=template_id,
            limit=limit,
        )
        return [
            {
                "run_id": r.get("id"),
                "template_id": r.get("templateId"),
                "template_name": r.get("templateName"),
                "template_kind": r.get("templateKind"),
                "status": r.get("status"),
                "created_at": r.get("createdAt"),
                "start_date": r.get("startDate"),
                "end_date": r.get("endDate"),
            }
            for r in runs
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a report run record from the state store."""
        from backend.app.repositories.state import state_store
        return state_store.get_report_run(run_id)

    def _resolve_artifact_path(self, url: Optional[str]) -> Optional[Path]:
        """
        Convert an artifact URL (e.g. /uploads/template_id/file.html)
        back to a filesystem path.
        """
        if not url:
            return None

        from backend.legacy.core.config import UPLOAD_ROOT, EXCEL_UPLOAD_ROOT

        UPLOAD_ROOT_BASE = UPLOAD_ROOT.resolve()
        EXCEL_UPLOAD_ROOT_BASE = EXCEL_UPLOAD_ROOT.resolve()

        url = url.lstrip("/")

        if url.startswith("uploads/"):
            relative = url[len("uploads/"):]
            candidate = UPLOAD_ROOT_BASE / relative
        elif url.startswith("excel-uploads/"):
            relative = url[len("excel-uploads/"):]
            candidate = EXCEL_UPLOAD_ROOT_BASE / relative
        else:
            return None

        # Safety: ensure the relative path doesn't traverse upwards
        if ".." in str(relative):
            logger.warning("Artifact path contains traversal: %s", url)
            return None

        return candidate if candidate.is_file() else None

    def _extract_text_from_html(self, html: str) -> str:
        """Extract plain text from HTML using BeautifulSoup if available, else regex."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style", "head"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # Collapse multiple blank lines
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text.strip()
        except ImportError:
            # Fallback: regex-based stripping
            text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text)
            return text.strip()

    def _extract_tables_from_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract tables from HTML as list of dicts:
        [{"headers": [...], "rows": [[...], ...]}, ...]
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            result = []

            for table_tag in soup.find_all("table"):
                headers = []
                rows = []

                # Extract headers from <thead> or first <tr> with <th>
                thead = table_tag.find("thead")
                if thead:
                    for th in thead.find_all("th"):
                        headers.append(th.get_text(strip=True))
                else:
                    first_row = table_tag.find("tr")
                    if first_row:
                        ths = first_row.find_all("th")
                        if ths:
                            headers = [th.get_text(strip=True) for th in ths]

                # Extract data rows
                tbody = table_tag.find("tbody") or table_tag
                for tr in tbody.find_all("tr"):
                    tds = tr.find_all("td")
                    if tds:
                        rows.append([td.get_text(strip=True) for td in tds])

                if headers or rows:
                    result.append({"headers": headers, "rows": rows})

            return result
        except ImportError:
            return []
