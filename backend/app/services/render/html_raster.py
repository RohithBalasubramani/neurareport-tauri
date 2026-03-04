from __future__ import annotations

import os
from typing import Literal

import fitz  # PyMuPDF
from playwright.sync_api import sync_playwright

MM_PER_INCH = 25.4

A4_MM_W = 210.0
A4_MM_H = 297.0


def _a4_enforcing_css() -> str:
    # Ensures one exact A4 page with white background for both methods
    return """
    @page { size: A4; margin: 0 }
    html, body { margin: 0; padding: 0; background: #fff; }
    .page { width: 210mm; min-height: 297mm; box-sizing: border-box; background: #fff; }
    """


def _wait_for_fonts(page) -> None:
    # Best-effort wait to ensure webfonts loaded
    try:
        page.wait_for_function("document.fonts && document.fonts.status === 'loaded'", timeout=10000)
    except Exception:
        pass


def _html_to_pdf_bytes_with_playwright(html: str) -> bytes:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.set_content(html, wait_until="networkidle")
        page.emulate_media(media="print")
        page.add_style_tag(content=_a4_enforcing_css())
        _wait_for_fonts(page)
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        ctx.close()
        browser.close()
        return pdf_bytes


def _rasterize_pdf_first_page_to_png(pdf_bytes: bytes, dpi: int) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    scale = dpi / 72.0  # PDF points are 72/in
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
    return pix.tobytes("png")


def _screenshot_element_to_png(html: str, selector: str, dpi: int) -> bytes:
    # Fallback if you need a direct DOM screenshot. Chromium may cap device_scale_factor.
    css_w = round(A4_MM_W / MM_PER_INCH * 96)  # ~794 px
    css_h = round(A4_MM_H / MM_PER_INCH * 96)  # ~1123 px
    dsf = dpi / 96.0  # 400/96 ≈ 4.1667 (may be clamped)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(
            device_scale_factor=dsf,
            viewport={"width": css_w, "height": css_h},
        )
        page = ctx.new_page()
        page.set_content(html, wait_until="networkidle")
        page.emulate_media(media="screen")
        page.add_style_tag(content=_a4_enforcing_css())
        _wait_for_fonts(page)
        locator = page.locator(selector)
        if locator.count() == 0:
            locator = page.locator("body")
        png = locator.screenshot(type="png")
        ctx.close()
        browser.close()
        return png


def rasterize_html_to_png(
    html: str,
    dpi: int = 400,
    method: Literal["pdf", "screenshot"] = "pdf",
    selector: str = ".page",
) -> bytes:
    """
    Returns a tightly-cropped A4 PNG at the requested DPI.
    Preferred: method='pdf' (uses print engine + PyMuPDF rasterize).
    Fallback: method='screenshot' crops selector ('.page').
    """
    if method == "pdf":
        pdf = _html_to_pdf_bytes_with_playwright(html)
        return _rasterize_pdf_first_page_to_png(pdf, dpi=dpi)
    return _screenshot_element_to_png(html, selector=selector, dpi=dpi)


def save_png(png_bytes: bytes, out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(png_bytes)
    return out_path
