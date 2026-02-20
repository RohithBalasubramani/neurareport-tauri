"""HTML rendering adapter."""

from __future__ import annotations

import html as html_mod
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List

from backend.engine.domain.reports import OutputFormat
from .base import BaseRenderer, RenderContext, RenderResult

logger = logging.getLogger("neura.adapters.rendering.html")


class HTMLRenderer(BaseRenderer):
    """Renderer that produces HTML output with token substitution."""

    @property
    def output_format(self) -> OutputFormat:
        return OutputFormat.HTML

    def render(self, context: RenderContext) -> RenderResult:
        """Render HTML with data substitution."""
        start = time.perf_counter()
        warnings: List[str] = []

        try:
            self._ensure_output_dir(context.output_path)

            # Perform token substitution
            html = self._substitute_tokens(context.template_html, context.data, warnings)

            # Write output
            context.output_path.write_text(html, encoding="utf-8")

            render_time = (time.perf_counter() - start) * 1000
            return RenderResult(
                success=True,
                output_path=context.output_path,
                format=OutputFormat.HTML,
                size_bytes=self._get_file_size(context.output_path),
                warnings=warnings,
                render_time_ms=render_time,
            )
        except Exception as e:
            logger.exception("html_render_failed")
            return RenderResult(
                success=False,
                output_path=None,
                format=OutputFormat.HTML,
                error="HTML rendering failed",
                render_time_ms=(time.perf_counter() - start) * 1000,
            )

    def _substitute_tokens(
        self,
        html: str,
        data: Dict[str, Any],
        warnings: List[str],
    ) -> str:
        """Substitute {{token}} placeholders with data values."""

        def replace_token(match: re.Match) -> str:
            token = match.group(1).strip()
            if token in data:
                value = data[token]
                if value is None:
                    return ""
                return html_mod.escape(str(value))
            else:
                warnings.append(f"Token '{token}' not found in data")
                return match.group(0)  # Keep original

        # Match {{token}} patterns
        pattern = r"\{\{([^}]+)\}\}"
        return re.sub(pattern, replace_token, html)


class TokenEngine:
    """Engine for processing tokens in HTML templates.

    Handles:
    - Scalar tokens (single values)
    - Row tokens (repeated rows)
    - Computed tokens (calculated values)
    - Conditional sections
    """

    SCALAR_PATTERN = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")
    ROW_PATTERN = re.compile(
        r"<!--\s*BEGIN_ROW\s*-->(.*?)<!--\s*END_ROW\s*-->",
        re.DOTALL,
    )
    CONDITIONAL_PATTERN = re.compile(
        r"<!--\s*IF\s+(\w+)\s*-->(.*?)<!--\s*ENDIF\s*-->",
        re.DOTALL,
    )

    def __init__(self) -> None:
        self._missing_tokens: List[str] = []

    @property
    def missing_tokens(self) -> List[str]:
        return list(self._missing_tokens)

    def process(
        self,
        html: str,
        scalars: Dict[str, Any],
        rows: List[Dict[str, Any]],
        totals: Dict[str, Any],
    ) -> str:
        """Process all tokens in the HTML template."""
        self._missing_tokens = []

        # Process conditionals first
        html = self._process_conditionals(html, scalars)

        # Process row sections
        html = self._process_rows(html, rows)

        # Process scalar tokens
        html = self._process_scalars(html, {**scalars, **totals})

        return html

    def _process_scalars(self, html: str, data: Dict[str, Any]) -> str:
        """Replace scalar tokens with values."""

        def replace(match: re.Match) -> str:
            token = match.group(1)
            if token in data:
                value = data[token]
                return "" if value is None else html_mod.escape(str(value))
            self._missing_tokens.append(token)
            return match.group(0)

        return self.SCALAR_PATTERN.sub(replace, html)

    def _process_rows(self, html: str, rows: List[Dict[str, Any]]) -> str:
        """Expand row templates for each data row."""

        def expand_row(match: re.Match) -> str:
            template = match.group(1)
            expanded = []
            for i, row_data in enumerate(rows):
                row_html = template
                # Add row index
                row_data = {**row_data, "ROWID": i + 1, "ROW_INDEX": i}
                row_html = self._process_scalars(row_html, row_data)
                expanded.append(row_html)
            return "".join(expanded)

        return self.ROW_PATTERN.sub(expand_row, html)

    def _process_conditionals(self, html: str, data: Dict[str, Any]) -> str:
        """Process conditional sections."""

        def evaluate(match: re.Match) -> str:
            condition = match.group(1)
            content = match.group(2)
            # Simple truthy check
            value = data.get(condition)
            if value:
                return content
            return ""

        return self.CONDITIONAL_PATTERN.sub(evaluate, html)
