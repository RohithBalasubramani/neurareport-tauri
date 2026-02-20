import logging
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependencies
    import fitz  # type: ignore
except ImportError:  # pragma: no cover
    fitz = None  # type: ignore

try:  # pragma: no cover - optional dependencies
    import cv2  # type: ignore
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore

try:  # pragma: no cover - optional dependencies
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None  # type: ignore


logger = logging.getLogger("neura.layout_hints")

MM_PER_POINT = 25.4 / 72.0


def _estimate_table_columns(page) -> Optional[int]:
    if any(mod is None for mod in (cv2, np, fitz)):  # type: ignore[arg-type]
        return None

    try:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        img = np.frombuffer(pix.samples, dtype="uint8")  # type: ignore[call-arg]
        img = img.reshape(pix.height, pix.width, pix.n)
        if pix.n >= 3:
            rgb = img[:, :, :3]
        else:
            rgb = img
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)  # type: ignore[attr-defined]
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # type: ignore[attr-defined]
        edges = cv2.Canny(blurred, 50, 150)  # type: ignore[attr-defined]

        vertical_projection = edges.sum(axis=0)
        if not np.any(vertical_projection):  # type: ignore[attr-defined]
            return None

        threshold = float(vertical_projection.mean() * 1.5)  # type: ignore[attr-defined]
        indices = np.where(vertical_projection > threshold)[0]  # type: ignore[attr-defined]
        if indices.size == 0:
            return None

        min_gap = max(6, pix.width // 200)
        min_span = max(4, pix.width // 500)
        clusters: list[tuple[int, int]] = []
        start = int(indices[0])
        prev = int(indices[0])
        for raw_idx in indices[1:]:
            idx = int(raw_idx)
            if idx - prev > min_gap:
                clusters.append((start, prev))
                start = idx
            prev = idx
        clusters.append((start, prev))

        significant = [(lo, hi) for lo, hi in clusters if (hi - lo) >= min_span]
        line_count = len(significant)
        if line_count >= 2:
            return line_count - 1  # vertical dividers imply columns
    except Exception:  # pragma: no cover - heuristic best-effort
        logger.debug("layout_hints_column_estimate_failed", exc_info=True)
    return None


def get_layout_hints(pdf_path: Path, page_index: int = 0) -> Dict[str, Any]:
    """Best-effort geometry hints for prompts (page size, rough table columns)."""
    if fitz is None:
        return {}

    try:
        with fitz.open(str(pdf_path)) as doc:  # type: ignore[call-arg]
            if page_index < 0 or page_index >= len(doc):
                return {}
            page = doc[page_index]
            width_mm = round(page.rect.width * MM_PER_POINT, 2)
            height_mm = round(page.rect.height * MM_PER_POINT, 2)

            hints: Dict[str, Any] = {
                "page_mm": [width_mm, height_mm],
                "notes": "best-effort",
            }

            est_tables = []
            columns = _estimate_table_columns(page)
            if columns and columns > 1:
                est_tables.append({"id": "tbl-1", "cols": int(columns)})
            if est_tables:
                hints["est_tables"] = est_tables
            return hints
    except Exception:  # pragma: no cover - logging for diagnostics
        logger.debug(
            "layout_hints_failed",
            exc_info=True,
            extra={"event": "layout_hints_failed", "pdf_path": str(pdf_path), "page_index": page_index},
        )
    return {}
