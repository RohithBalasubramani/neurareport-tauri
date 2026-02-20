from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Tuple

try:
    from PIL import Image  # type: ignore
except ImportError:  # pragma: no cover
    Image = None  # type: ignore

try:
    from playwright.sync_api import sync_playwright  # type: ignore
except ImportError:  # pragma: no cover
    sync_playwright = None  # type: ignore

logger = logging.getLogger("neura.render")

_A4_MM: Tuple[float, float] = (210.0, 297.0)
_MM_PER_INCH = 25.4


def _page_viewport(page_size: str, dpi: int) -> Tuple[int, int]:
    """
    Compute integer viewport (width, height) for the requested page size at the given DPI.
    Currently supports A4 portrait which is our pipeline default.
    """
    size = page_size.upper()
    if size != "A4":
        raise ValueError(f"Unsupported page_size '{page_size}'. Only 'A4' is currently supported.")
    width_px = int(round((_A4_MM[0] / _MM_PER_INCH) * dpi))
    height_px = int(round((_A4_MM[1] / _MM_PER_INCH) * dpi))
    return width_px, height_px


def _ensure_dimensions(path: Path, target: Tuple[int, int]) -> None:
    """
    Pad/crop the rendered screenshot to exactly match the target dimensions.
    """
    if Image is None:  # pragma: no cover
        logger.debug(
            "render_image_adjust_skip",
            extra={"event": "render_image_adjust_skip", "path": str(path)},
        )
        return
    with Image.open(path) as img:
        if img.size == target:
            return
        width, height = target
        if img.width > width or img.height > height:
            img = img.crop((0, 0, width, height))
        if img.width < width or img.height < height:
            canvas = Image.new("RGB", target, "white")
            canvas.paste(img, (0, 0))
            img = canvas
        img.save(path)
        logger.info(
            "render_image_adjusted",
            extra={
                "event": "render_image_adjusted",
                "path": str(path),
                "target_width": width,
                "target_height": height,
            },
        )


def _ensure_playwright_browsers_path() -> None:
    """
    Patch in the system-level Playwright browser cache when packaging omits it.
    """
    if os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        return
    local_app = os.getenv("LOCALAPPDATA")
    if not local_app:
        return
    candidate = Path(local_app) / "ms-playwright"
    if candidate.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(candidate)


def render_html_to_png(
    html_path: Path,
    out_png_path: Path,
    *,
    page_size: str = "A4",
    dpi: int = 400,
    wait_until: str = "networkidle",
) -> None:
    """
    Render HTML to a PNG using Playwright's sync API.
    Ensures deterministic viewport sizing so that SSIM comparisons are meaningful.
    """
    if sync_playwright is None:  # pragma: no cover
        raise RuntimeError(
            "playwright is required for HTML rendering. Install with `pip install playwright` "
            "and run `playwright install chromium`."
        )

    _ensure_playwright_browsers_path()

    html_path = Path(html_path).resolve()
    out_png_path = Path(out_png_path).resolve()
    out_png_path.parent.mkdir(parents=True, exist_ok=True)

    viewport = _page_viewport(page_size, dpi)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(
                viewport={"width": viewport[0], "height": viewport[1]},
                device_scale_factor=1,
            )
            page.goto(f"file://{html_path}", wait_until=wait_until)
            page.screenshot(path=str(out_png_path), full_page=True)
        finally:
            browser.close()

    _ensure_dimensions(out_png_path, viewport)

    logger.info(
        "html_rendered_to_png",
        extra={
            "event": "html_rendered_to_png",
            "html_path": str(html_path),
            "png_path": str(out_png_path),
            "page_size": page_size,
            "dpi": dpi,
        },
    )


__all__ = ["render_html_to_png"]
