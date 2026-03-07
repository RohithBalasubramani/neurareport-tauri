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
import re
import sys
import tempfile
from pathlib import Path

# Configurable timeout for Playwright page operations (default: 2 minutes).
# Prevents indefinite hangs when HTML references broken external resources.
_PDF_RENDER_TIMEOUT_MS = int(os.environ.get("NEURA_PDF_RENDER_TIMEOUT_MS", "120000"))

# Maximum number of <tr> rows before we switch to chunked PDF generation.
_CHUNK_THRESHOLD = int(os.environ.get("NEURA_PDF_CHUNK_THRESHOLD", "8000"))
# Rows per chunk when chunking.
_CHUNK_SIZE = int(os.environ.get("NEURA_PDF_CHUNK_SIZE", "5000"))


def _count_tr(html: str) -> int:
    """Fast count of <tr> tags in the HTML."""
    return html.lower().count("<tr")


def _split_html_chunks(html: str, chunk_size: int) -> list[str]:
    """Split a large HTML table into multiple smaller HTML documents.

    Preserves <head>, header elements, <thead>, and <tfoot> in each chunk.
    Splits only the <tbody> rows.
    """
    # Extract everything before <tbody> and after </tbody>
    tbody_match = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", html, re.DOTALL | re.IGNORECASE)
    if not tbody_match:
        return [html]

    pre_tbody = html[: tbody_match.start(2)]   # everything up to and including <tbody>
    tbody_content = tbody_match.group(2)
    post_tbody = html[tbody_match.end(2):]      # </tbody> and everything after

    # Split tbody content into individual <tr>...</tr> blocks
    rows = re.findall(r"<tr[\s>].*?</tr>", tbody_content, re.DOTALL | re.IGNORECASE)
    if not rows:
        return [html]

    chunks = []
    for i in range(0, len(rows), chunk_size):
        chunk_rows = rows[i : i + chunk_size]
        chunk_html = pre_tbody + "\n".join(chunk_rows) + post_tbody
        chunks.append(chunk_html)

    return chunks


async def _render_single(page, pdf_path: str, scale: float) -> None:
    """Render a single page to PDF."""
    await page.emulate_media(media="print")
    await page.pdf(
        path=pdf_path,
        format="A4",
        landscape=True,
        print_background=True,
        margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
        prefer_css_page_size=True,
        scale=scale,
    )


def _merge_pdfs(pdf_paths: list[str], output_path: str) -> None:
    """Merge multiple PDF files into one using pikepdf (or PyPDF2 fallback)."""
    try:
        import pikepdf
        merged = pikepdf.Pdf.new()
        for p in pdf_paths:
            src = pikepdf.open(p)
            merged.pages.extend(src.pages)
        merged.save(output_path)
        merged.close()
    except ImportError:
        from PyPDF2 import PdfMerger
        merger = PdfMerger()
        for p in pdf_paths:
            merger.append(p)
        merger.write(output_path)
        merger.close()


async def _launch_browser(p):
    """Launch a Chromium-based browser, preferring system Chrome/Edge.

    Strategy:
    1. Try system Edge (pre-installed on all Windows 10/11)
    2. Try system Chrome (commonly installed)
    3. Fall back to Playwright's own Chromium (downloaded at first launch)
    """
    launch_args = [
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--no-sandbox",
    ]

    # Try system browsers first — no download needed, no AV issues
    for channel in ("msedge", "chrome"):
        try:
            browser = await p.chromium.launch(channel=channel, args=launch_args)
            print(f"[pdf_worker] Using system browser: {channel}", file=sys.stderr)
            return browser
        except Exception:
            continue

    # Fall back to Playwright's bundled/downloaded Chromium
    browser = await p.chromium.launch(args=launch_args)
    print("[pdf_worker] Using Playwright Chromium", file=sys.stderr)
    return browser


async def _convert(html_path: str, pdf_path: str, base_dir: str, pdf_scale: float | None = None) -> None:
    from playwright.async_api import async_playwright

    html_source = Path(html_path).read_text(encoding="utf-8", errors="ignore")
    base_url = Path(base_dir).resolve().as_uri()

    scale_value = pdf_scale or 1.0
    if not isinstance(scale_value, (int, float)):
        scale_value = 1.0
    scale_value = max(0.1, min(float(scale_value), 2.0))

    tr_count = _count_tr(html_source)
    needs_chunking = tr_count > _CHUNK_THRESHOLD

    async with async_playwright() as p:
        browser = await _launch_browser(p)

        if not needs_chunking:
            # Standard single-pass rendering
            context = await browser.new_context(base_url=base_url)
            try:
                page = await context.new_page()
                page.set_default_timeout(_PDF_RENDER_TIMEOUT_MS)
                await page.set_content(html_source, wait_until="load", timeout=_PDF_RENDER_TIMEOUT_MS)
                await _render_single(page, pdf_path, scale_value)
            finally:
                await context.close()
                await browser.close()
            return

        # Chunked rendering for large documents
        print(f"[pdf_worker] Large document ({tr_count} rows), using chunked rendering", file=sys.stderr)
        chunks = _split_html_chunks(html_source, _CHUNK_SIZE)
        print(f"[pdf_worker] Split into {len(chunks)} chunks", file=sys.stderr)

        tmp_dir = tempfile.mkdtemp(prefix="neura_pdf_chunks_")
        chunk_paths: list[str] = []

        try:
            for idx, chunk_html in enumerate(chunks):
                chunk_pdf = os.path.join(tmp_dir, f"chunk_{idx:04d}.pdf")
                context = await browser.new_context(base_url=base_url)
                try:
                    page = await context.new_page()
                    page.set_default_timeout(_PDF_RENDER_TIMEOUT_MS)
                    await page.set_content(chunk_html, wait_until="load", timeout=_PDF_RENDER_TIMEOUT_MS)
                    await _render_single(page, chunk_pdf, scale_value)
                    chunk_paths.append(chunk_pdf)
                    print(f"[pdf_worker] Chunk {idx + 1}/{len(chunks)} done", file=sys.stderr)
                finally:
                    await context.close()

            # Merge all chunks into the final PDF
            _merge_pdfs(chunk_paths, pdf_path)
            print(f"[pdf_worker] Merged {len(chunk_paths)} chunks into {pdf_path}", file=sys.stderr)
        finally:
            await browser.close()
            # Cleanup temp files
            for cp in chunk_paths:
                try:
                    os.unlink(cp)
                except OSError:
                    pass
            try:
                os.rmdir(tmp_dir)
            except OSError:
                pass


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
