"""PDF rendering adapter using Playwright."""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional

from backend.engine.domain.reports import OutputFormat
from .base import BaseRenderer, RenderContext, RenderResult

logger = logging.getLogger("neura.adapters.rendering.pdf")


class PDFRenderer(BaseRenderer):
    """Renderer that produces PDF output using Playwright."""

    def __init__(
        self,
        *,
        browser_type: str = "chromium",
        headless: bool = True,
    ) -> None:
        self._browser_type = browser_type
        self._headless = headless

    @property
    def output_format(self) -> OutputFormat:
        return OutputFormat.PDF

    def render(self, context: RenderContext) -> RenderResult:
        """Render PDF from HTML using Playwright."""
        start = time.perf_counter()

        try:
            self._ensure_output_dir(context.output_path)

            # Run async rendering
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    pool.submit(asyncio.run, self._render_async(context)).result()
            else:
                asyncio.run(self._render_async(context))

            if not context.output_path.exists():
                return RenderResult(
                    success=False,
                    output_path=None,
                    format=OutputFormat.PDF,
                    error="PDF file was not created",
                    render_time_ms=(time.perf_counter() - start) * 1000,
                )

            render_time = (time.perf_counter() - start) * 1000
            return RenderResult(
                success=True,
                output_path=context.output_path,
                format=OutputFormat.PDF,
                size_bytes=self._get_file_size(context.output_path),
                render_time_ms=render_time,
            )
        except Exception as e:
            logger.exception("pdf_render_failed")
            return RenderResult(
                success=False,
                output_path=None,
                format=OutputFormat.PDF,
                error="PDF rendering failed",
                render_time_ms=(time.perf_counter() - start) * 1000,
            )

    async def _render_async(self, context: RenderContext) -> None:
        """Async PDF rendering with Playwright."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError(
                "Playwright is required for PDF rendering. "
                "Install with: pip install playwright && playwright install chromium"
            )

        async with async_playwright() as p:
            browser = await getattr(p, self._browser_type).launch(
                headless=self._headless
            )
            try:
                page = await browser.new_page()

                # Load HTML content
                await page.set_content(context.template_html, wait_until="networkidle")

                # Configure PDF options
                pdf_options = {
                    "path": str(context.output_path),
                    "format": context.page_size,
                    "print_background": True,
                    "landscape": context.landscape,
                }

                if context.margins:
                    pdf_options["margin"] = context.margins

                # Generate PDF
                await page.pdf(**pdf_options)

            finally:
                await browser.close()


class PDFRendererSync:
    """Synchronous wrapper for PDF rendering.

    Use this when you need to render from synchronous code.
    """

    def __init__(self, renderer: Optional[PDFRenderer] = None) -> None:
        self._renderer = renderer or PDFRenderer()

    def render_from_html_file(
        self,
        html_path: Path,
        output_path: Path,
        *,
        landscape: bool = False,
        page_size: str = "A4",
    ) -> RenderResult:
        """Render PDF from an HTML file."""
        html_content = html_path.read_text(encoding="utf-8")

        context = RenderContext(
            template_html=html_content,
            data={},
            output_format=OutputFormat.PDF,
            output_path=output_path,
            landscape=landscape,
            page_size=page_size,
        )

        return self._renderer.render(context)

    def render_from_html_string(
        self,
        html: str,
        output_path: Path,
        *,
        landscape: bool = False,
        page_size: str = "A4",
    ) -> RenderResult:
        """Render PDF from an HTML string."""
        context = RenderContext(
            template_html=html,
            data={},
            output_format=OutputFormat.PDF,
            output_path=output_path,
            landscape=landscape,
            page_size=page_size,
        )

        return self._renderer.render(context)
