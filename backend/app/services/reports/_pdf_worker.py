#!/usr/bin/env python3
"""Standalone Playwright PDF worker — runs in its own process.

This script is invoked as a subprocess by ReportGenerateExcel to isolate
Playwright's Chromium browser from the main uvicorn event loop.  Running
Playwright in its own process avoids the SIGCHLD / asyncio-subprocess
conflict that occurs when ``asyncio.run()`` is called from a non-main
thread inside the web server.

Usage:
    python _pdf_worker.py <json-args>

The JSON argument must contain:
    html_path   – absolute path to the source HTML file
    pdf_path    – absolute path for the output PDF
    base_dir    – absolute path used as Playwright's base_url
    pdf_scale   – optional float (0.1 – 2.0, default 1.0)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

# Configurable timeout for Playwright page operations (default: 2 minutes).
# Prevents indefinite hangs when HTML references broken external resources.
_PDF_RENDER_TIMEOUT_MS = int(os.environ.get("NEURA_PDF_RENDER_TIMEOUT_MS", "120000"))


async def _convert(html_path: str, pdf_path: str, base_dir: str, pdf_scale: float | None = None) -> None:
    from playwright.async_api import async_playwright

    html_source = Path(html_path).read_text(encoding="utf-8", errors="ignore")
    base_url = Path(base_dir).resolve().as_uri()

    scale_value = pdf_scale or 1.0
    if not isinstance(scale_value, (int, float)):
        scale_value = 1.0
    scale_value = max(0.1, min(float(scale_value), 2.0))

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(base_url=base_url)
        try:
            page = await context.new_page()
            page.set_default_timeout(_PDF_RENDER_TIMEOUT_MS)
            # Use "load" instead of "networkidle" to avoid hanging on
            # external resources. Local file:// content loads instantly.
            await page.set_content(html_source, wait_until="load", timeout=_PDF_RENDER_TIMEOUT_MS)
            await page.emulate_media(media="print")
            await page.pdf(
                path=pdf_path,
                format="A4",
                landscape=True,
                print_background=True,
                margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
                prefer_css_page_size=True,
                scale=scale_value,
            )
        finally:
            await context.close()
            await browser.close()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: _pdf_worker.py <json-args>", file=sys.stderr)
        sys.exit(1)

    args = json.loads(sys.argv[1])
    asyncio.run(
        _convert(
            html_path=args["html_path"],
            pdf_path=args["pdf_path"],
            base_dir=args["base_dir"],
            pdf_scale=args.get("pdf_scale"),
        )
    )


if __name__ == "__main__":
    main()
