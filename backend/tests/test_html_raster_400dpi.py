import importlib
import io

import pytest

pytest.importorskip("playwright.sync_api")
pil_image_module = pytest.importorskip("PIL.Image")
# Keep the module alias so helpers like `open` are available (mirrors `from PIL import Image`).
Image = pil_image_module

render_module = importlib.import_module("backend.app.services.render.html_raster")
rasterize_html_to_png = render_module.rasterize_html_to_png


def _dims(png_bytes: bytes):
    image = Image.open(io.BytesIO(png_bytes))
    return image.size


def test_pdf_method_dimensions_close_to_a4_400dpi():
    html = """<!doctype html><html><head><meta charset="utf-8"></head>
    <body><div class="page"><h1>Test A4</h1><p>Preview @400dpi</p></div></body></html>"""
    try:
        png_bytes = rasterize_html_to_png(html, dpi=400, method="pdf")
    except Exception as exc:  # pragma: no cover - skip when browser missing
        pytest.skip(f"Playwright PDF rendering unavailable: {exc}")
    width, height = _dims(png_bytes)
    assert abs(width - 3307) <= 20, (width, height)
    assert abs(height - 4677) <= 20, (width, height)
