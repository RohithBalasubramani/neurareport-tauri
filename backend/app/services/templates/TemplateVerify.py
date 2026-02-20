import asyncio
import base64
import json
import logging
import os
import re
import shutil
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..prompts.llm_prompts import LLM_CALL_PROMPTS
from ..render.html_raster import rasterize_html_to_png, save_png
from ..utils import call_chat_completion, extract_tokens, normalize_token_braces
from ..utils import render_html_to_png as _render_html_to_png_sync
from ..utils import sanitize_html, write_json_atomic, write_text_atomic
from .css_merge import merge_css_into_html, replace_table_colgroup

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None  # type: ignore

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None  # type: ignore

try:
    from skimage.metrics import structural_similarity as ssim
except ImportError:  # pragma: no cover
    ssim = None  # type: ignore

from backend.app.services.config import get_settings

logger = logging.getLogger("neura.template_verify")


def _get_model() -> str:
    """Use centralized config for model selection (Claude Code CLI)."""
    return get_settings().claude_code_model


# Lazy evaluation - will be called when needed, not at import time
MODEL = None


def _ensure_model() -> str:
    global MODEL
    if MODEL is None:
        MODEL = _get_model()
    return MODEL


# Unified LLM client (lazily initialized)
_llm_client = None


@dataclass
class InitialHtmlResult:
    html: str
    schema: Optional[Dict[str, Any]]
    schema_text: Optional[str]


@lru_cache(maxsize=1)
def _load_llm_call1_prompt() -> str:
    try:
        return LLM_CALL_PROMPTS["llm_call_1"]
    except KeyError as exc:  # pragma: no cover
        raise RuntimeError("Prompt 'llm_call_1' missing from LLM_CALL_PROMPTS") from exc


@lru_cache(maxsize=1)
def _load_llm_call2_prompt() -> str:
    try:
        return LLM_CALL_PROMPTS["llm_call_2"]
    except KeyError as exc:  # pragma: no cover
        raise RuntimeError("Prompt 'llm_call_2' missing from LLM_CALL_PROMPTS") from exc


def _extract_marked_section(text: str, begin: str, end: str) -> Optional[str]:
    pattern = re.compile(re.escape(begin) + r"([\s\S]*?)" + re.escape(end))
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def _strip_braces(token: str) -> str:
    token = normalize_token_braces(token or "").strip()
    if token.startswith("{") and token.endswith("}"):
        return token[1:-1].strip()
    return token


def _dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen: Dict[str, None] = {}
    for item in items:
        if item not in seen:
            seen[item] = None
    return list(seen.keys())


_BEGIN_REPEAT_RE = re.compile(r"<!--\s*BEGIN:BLOCK_REPEAT\b", re.IGNORECASE)
_REPEAT_BLOCK_RE = re.compile(
    r"<!--\s*BEGIN:BLOCK_REPEAT\b.*?-->(.*?)<!--\s*END:BLOCK_REPEAT\b.*?-->",
    re.IGNORECASE | re.DOTALL,
)
_TR_PATTERN = re.compile(r"<tr\b", re.IGNORECASE)


def _extract_tokens(html_text: str) -> set[str]:
    return set(extract_tokens(normalize_token_braces(html_text or "")))


def _repeat_marker_counts(html_text: str) -> int:
    return len(_BEGIN_REPEAT_RE.findall(html_text or ""))


def _prototype_row_counts(html_text: str) -> List[int]:
    counts: List[int] = []
    for block in _REPEAT_BLOCK_RE.finditer(html_text or ""):
        segment = block.group(1) or ""
        counts.append(len(_TR_PATTERN.findall(segment)))
    return counts


def _write_fix_metrics(tdir: Path, payload: Dict[str, Any]) -> Path:
    metrics_path = Path(tdir) / "fix_metrics.json"
    write_json_atomic(
        metrics_path,
        payload,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
        step="template_verify_fix_metrics",
    )
    return metrics_path


def _parse_schema_ext(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception as exc:
        logger.warning(
            "schema_ext_json_parse_failed",
            extra={
                "event": "schema_ext_json_parse_failed",
                "error": str(exc),
                "snippet": raw[:200],
            },
        )
        return None
    if not isinstance(data, dict):
        logger.warning(
            "schema_ext_invalid_type",
            extra={"event": "schema_ext_invalid_type", "snippet": raw[:200]},
        )
        return None

    try:
        scalars_raw = data.get("scalars", [])
        row_tokens_raw = data.get("row_tokens", [])
        totals_raw = data.get("totals", [])
        notes_raw = data.get("notes", "")

        scalars = _dedupe_preserve_order(
            [_strip_braces(str(tok)) for tok in list(scalars_raw or []) if str(tok).strip()]
        )
        rows = _dedupe_preserve_order(
            [_strip_braces(str(tok)) for tok in list(row_tokens_raw or []) if str(tok).strip()]
        )
        totals = _dedupe_preserve_order([_strip_braces(str(tok)) for tok in list(totals_raw or []) if str(tok).strip()])

        if not isinstance(notes_raw, str):
            notes = str(notes_raw)
        else:
            notes = notes_raw
    except Exception as exc:
        logger.warning(
            "schema_ext_validation_failed",
            extra={
                "event": "schema_ext_validation_failed",
                "error": str(exc),
            },
        )
        return None

    return {
        "scalars": scalars,
        "row_tokens": rows,
        "totals": totals,
        "notes": notes,
    }


def get_openai_client():
    """
    Return a cached LLM client using Claude Code CLI.

    This function is named get_openai_client for backward compatibility,
    but uses Claude Code CLI as the backend.
    """
    global _llm_client
    if _llm_client is not None:
        return _llm_client
    from backend.app.services.llm.client import get_llm_client
    _llm_client = get_llm_client()
    return _llm_client


def pdf_page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF without rendering anything."""
    if fitz is None:
        raise RuntimeError("PyMuPDF (install via `pip install pymupdf`) is required for PDF operations.")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count


def pdf_to_pngs(pdf_path: Path, out_dir: Path, dpi=400, *, page: int = 0):
    """Render a single page of the PDF to PNG.

    Args:
        pdf_path: Path to the source PDF.
        out_dir: Directory for the output PNG.
        dpi: Resolution for rasterisation.
        page: Zero-based page index to render (default 0 = first page).

    Returns:
        List containing a single Path to the rendered PNG.

    Raises:
        ValueError: If *page* is out of range for the document.
    """
    if fitz is None:
        raise RuntimeError("PyMuPDF (install via `pip install pymupdf`) is required for PDF rendering.")
    assert pdf_path.exists(), f"PDF not found: {pdf_path}"
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    if page < 0 or page >= total_pages:
        doc.close()
        raise ValueError(
            f"Page index {page} out of range for PDF with {total_pages} page(s). "
            f"Valid range: 0–{total_pages - 1}."
        )
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pg = doc[page]
    pix = pg.get_pixmap(matrix=mat, alpha=False)
    out_png = out_dir / "reference_p1.png"
    pix.save(out_png)
    doc.close()
    logger.info(
        "pdf_page_rendered",
        extra={
            "event": "pdf_page_rendered",
            "pdf_path": str(pdf_path),
            "png_path": str(out_png),
            "page": page,
            "total_pages": total_pages,
            "dpi": dpi,
        },
    )
    return [out_png]


def b64_image(path: Path):
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def strip_code_fences(text: str) -> str:
    m = re.search(r"```(?:html|HTML)?\s*([\s\S]*?)```", text)
    return m.group(1).strip() if m else text.strip()


CSS_PATCH_RE = re.compile(r"<!--BEGIN_CSS_PATCH-->([\s\S]*?)<!--END_CSS_PATCH-->", re.I)
HTML_BLOCK_RE = re.compile(r"<!--BEGIN_HTML-->([\s\S]*?)<!--END_HTML-->", re.I)
STYLE_BLOCK_RE = re.compile(r"(?is)<style\b[^>]*>(.*?)</style>")
TABLE_COMMENT_RE = re.compile(
    r"<!--\s*TABLE:(?P<table>[\w\-\.:]+)\s*-->\s*(?P<colgroup><colgroup\b[^>]*>.*?</colgroup>)",
    re.I | re.S,
)
COLGROUP_SNIPPET_RE = re.compile(r"(<colgroup\b[^>]*>.*?</colgroup>)", re.I | re.S)
COLGROUP_ATTR_TARGET_RE = re.compile(
    r"(data-(?:target|table|table-id|for)|table-id|for)\s*=\s*['\"](?P<value>[^'\"]+)['\"]",
    re.I,
)


def normalize_schema_for_initial_html(schema_json: Dict[str, Any]) -> Dict[str, Any]:
    """Return a legacy-compatible schema shape for initial HTML prompts."""
    scalars: Dict[str, str] = {}
    raw_scalars = schema_json.get("scalars", {})
    if isinstance(raw_scalars, dict):
        for key, value in raw_scalars.items():
            token = key
            label: str
            if isinstance(value, dict):
                token = str(value.get("token") or token)
                label = str(value.get("label") or value.get("token") or token)
            elif isinstance(value, str):
                label = value
            else:
                label = str(value)
            scalars[token] = label
    elif isinstance(raw_scalars, list):
        for entry in raw_scalars:
            if isinstance(entry, str):
                scalars[entry] = entry
            elif isinstance(entry, dict):
                token = entry.get("token") or entry.get("name") or entry.get("id")
                if token:
                    scalars[str(token)] = str(entry.get("label") or token)

    blocks_raw = schema_json.get("blocks") or {}
    rows: list[str] = []
    headers: list[str] = []
    repeat_regions = None
    if isinstance(blocks_raw, dict):
        raw_rows = blocks_raw.get("rows")
        if isinstance(raw_rows, list):
            for entry in raw_rows:
                if isinstance(entry, str):
                    rows.append(entry)
                elif isinstance(entry, dict):
                    token = entry.get("token") or entry.get("name") or entry.get("id")
                    if token:
                        rows.append(str(token))
        raw_headers = blocks_raw.get("headers")
        if isinstance(raw_headers, list):
            headers = [str(item) for item in raw_headers]
        repeat_regions = blocks_raw.get("repeat_regions")

    normalized_blocks: Dict[str, Any] = {}
    if rows:
        normalized_blocks["rows"] = rows
    if headers:
        normalized_blocks["headers"] = headers
    if repeat_regions:
        normalized_blocks["repeat_regions"] = repeat_regions

    normalized: Dict[str, Any] = {
        "scalars": scalars,
        "blocks": normalized_blocks,
    }
    notes = schema_json.get("notes")
    if isinstance(notes, str) and notes:
        normalized["notes"] = notes

    page_tokens = schema_json.get("page_tokens_protect") or schema_json.get("pageTokensProtect")
    if isinstance(page_tokens, list) and page_tokens:
        normalized["page_tokens_protect"] = page_tokens

    return normalized


def _iter_colgroup_updates(patch_body: str):
    seen: set[tuple[str, str]] = set()
    for match in TABLE_COMMENT_RE.finditer(patch_body):
        table_id = match.group("table").strip()
        colgroup_html = match.group("colgroup").strip()
        key = (table_id, colgroup_html)
        if table_id and colgroup_html and key not in seen:
            seen.add(key)
            yield table_id, colgroup_html

    for match in COLGROUP_SNIPPET_RE.finditer(patch_body):
        snippet = match.group(1).strip()
        attr_match = COLGROUP_ATTR_TARGET_RE.search(snippet)
        if not attr_match:
            continue
        table_id = attr_match.group("value").strip()
        key = (table_id, snippet)
        if table_id and key not in seen:
            seen.add(key)
            yield table_id, snippet


def apply_fix_response(html_before: str, llm_output: str) -> str:
    """Merge LLM fix output into the existing HTML."""
    output = llm_output.strip()
    css_match = CSS_PATCH_RE.search(output)
    if css_match:
        patch_body = css_match.group(1).strip()
        style_match = STYLE_BLOCK_RE.search(patch_body)
        css_rules = style_match.group(1).strip() if style_match else patch_body
        merged = merge_css_into_html(html_before, css_rules)
        for table_id, colgroup_html in _iter_colgroup_updates(patch_body):
            merged = replace_table_colgroup(merged, table_id, colgroup_html)
        return merged

    html_match = HTML_BLOCK_RE.search(output)
    if html_match:
        return html_match.group(1).strip()

    return output


def render_panel_preview(
    html_path: Path,
    dest_png: Path,
    *,
    fallback_png: Optional[Path] = None,
    dpi: int = 144,
) -> Path:
    """
    Generate a template snapshot that matches the front-end preview
    (CSS-sized A4 at ~96 DPI, optionally with a device scale factor).
    Falls back to the existing PNG if rasterisation fails.
    """
    html_path = Path(html_path)
    dest_png = Path(dest_png)
    fallback_png = Path(fallback_png) if fallback_png else None
    try:
        html_text = html_path.read_text(encoding="utf-8")
        png_bytes = rasterize_html_to_png(html_text, dpi=dpi, method="screenshot")
        save_png(png_bytes, str(dest_png))
    except Exception:
        logger.warning(
            "render_panel_preview_failed",
            exc_info=True,
            extra={"event": "render_panel_preview_failed", "html_path": str(html_path)},
        )
        if fallback_png and fallback_png.exists():
            dest_png.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(fallback_png, dest_png)
    return dest_png


def render_html_to_png(html_path: Path, out_png: Path, *, page_size: str = "A4") -> None:
    """
    Render HTML to PNG using the shared utils helper for compatibility with existing imports.
    """
    _render_html_to_png_sync(html_path, out_png, page_size=page_size)


def compare_images(ref_img_path: Path, test_img_path: Path, out_diff: Path):
    if None in (Image, np, cv2, ssim):
        raise RuntimeError("Image comparison requires Pillow, numpy, opencv-python, and scikit-image.")
    A = Image.open(ref_img_path).convert("RGB")
    B = Image.open(test_img_path).convert("RGB")
    # Resize both to the same target (e.g., width of reference)
    target = (A.width, A.height)
    B = B.resize(target)
    A_arr = np.array(A).astype("uint8")
    B_arr = np.array(B).astype("uint8")
    A_g = cv2.cvtColor(A_arr, cv2.COLOR_RGB2GRAY)
    B_g = cv2.cvtColor(B_arr, cv2.COLOR_RGB2GRAY)
    score, diff = ssim(A_g, B_g, full=True, data_range=255)
    heat = ((1 - diff) * 255).astype("uint8")
    heat_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(A_arr, 0.6, heat_color, 0.4, 0)
    cv2.imwrite(str(out_diff), cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    return float(score)


def save_html(path: Path, html: str):
    normalized_html = sanitize_html(normalize_token_braces(html))
    write_text_atomic(path, normalized_html, encoding="utf-8", step="template_verify_save")
    logger.info(
        "html_saved",
        extra={"event": "html_saved", "path": str(path)},
    )


# LLM client initialised lazily via get_openai_client() (uses Claude Code CLI)


def request_initial_html(
    page_png: Path,
    schema_json: Optional[dict],
    layout_hints: Optional[Dict[str, Any]] = None,
) -> InitialHtmlResult:
    """Ask the LLM to synthesize the first-pass HTML photocopy and optional schema."""
    prompt_template = _load_llm_call1_prompt()
    schema_str = ""
    if schema_json:
        schema_str = json.dumps(schema_json, ensure_ascii=False, separators=(",", ":"))
    prompt = prompt_template.replace("{schema_str}", schema_str)
    hints_json = json.dumps(layout_hints or {}, ensure_ascii=False, separators=(",", ":"))

    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    if hints_json and hints_json != "{}":
        content.append({"type": "text", "text": "HINTS_JSON:\n" + hints_json})
    content.append(
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64_image(page_png)}"},
        }
    )

    client = get_openai_client()
    resp = call_chat_completion(
        client,
        model=_ensure_model(),
        messages=[{"role": "user", "content": content}],
        description="template_initial_html",
    )

    raw_content = strip_code_fences(resp.choices[0].message.content or "")

    html_section = _extract_marked_section(raw_content, "<!--BEGIN_HTML-->", "<!--END_HTML-->")
    if html_section is None:
        logger.warning(
            "initial_html_marker_missing",
            extra={
                "event": "initial_html_marker_missing",
                "marker": "HTML",
            },
        )
        html_section = raw_content
    html_clean = normalize_token_braces(html_section.strip())

    schema_section = _extract_marked_section(raw_content, "<!--BEGIN_SCHEMA_JSON-->", "<!--END_SCHEMA_JSON-->")
    schema_payload = None
    if schema_section:
        schema_payload = _parse_schema_ext(schema_section)
        if schema_payload is None:
            logger.warning(
                "initial_schema_ext_invalid",
                extra={
                    "event": "initial_schema_ext_invalid",
                    "snippet": schema_section[:200],
                },
            )

    return InitialHtmlResult(
        html=html_clean,
        schema=schema_payload,
        schema_text=schema_section,
    )


def request_fix_html(
    pdf_dir: Path,
    html_path: Path,
    schema_path_or_none: Optional[Path],
    reference_png_path: Path,
    render_png_path: Path,
    ssim_value: float,
) -> Dict[str, Any]:
    """
    Execute the single-pass HTML refinement call (LLM CALL 2) and enforce strict invariants.

    Returns a payload with acceptance metadata and artifact paths:
        {
            "accepted": bool,
            "rejected_reason": Optional[str],
            "render_after_path": Optional[Path],
            "metrics_path": Path,
            "raw_response": str,
        }
    """
    pdf_dir = Path(pdf_dir)
    html_path = Path(html_path)
    schema_path = Path(schema_path_or_none) if schema_path_or_none else None
    reference_png_path = Path(reference_png_path)
    render_png_path = Path(render_png_path)

    current_html = html_path.read_text(encoding="utf-8")

    schema_text = "{}"
    if schema_path and schema_path.exists():
        try:
            schema_payload = json.loads(schema_path.read_text(encoding="utf-8"))
            schema_text = json.dumps(schema_payload, ensure_ascii=False, indent=2, sort_keys=True)
        except Exception as exc:
            logger.warning(
                "template_fix_html_schema_load_failed",
                extra={
                    "event": "template_fix_html_schema_load_failed",
                    "path": str(schema_path),
                    "error": str(exc),
                },
            )
            schema_text = "{}"

    prompt_template = _load_llm_call2_prompt()
    prompt_text = prompt_template.replace("{{ssim_value:.4f}}", "0.0000")
    prompt_text = prompt_text.replace("{schema_str}", schema_text)
    prompt_text = prompt_text.replace("{current_html}", current_html)
    prompt_text = prompt_text.replace("(embedded image URL)", "").strip()

    client = get_openai_client()
    response = call_chat_completion(
        client,
        model=_ensure_model(),
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_image(reference_png_path)}",
                            "detail": "high",
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_image(render_png_path)}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        description="template_fix_html_call2",
    )
    raw_response = (response.choices[0].message.content or "").strip()

    refined_html = _extract_marked_section(raw_response, "<!--BEGIN_HTML-->", "<!--END_HTML-->")
    metrics: Dict[str, Any] = {
        "accepted": False,
        "rejected_reason": None,
    }
    render_after_path: Optional[Path] = None

    if refined_html is None:
        logger.warning(
            "template_fix_html_missing_markers",
            extra={
                "event": "template_fix_html_missing_markers",
                "snippet": raw_response[:300],
            },
        )
        metrics["rejected_reason"] = "missing_markers"
        save_html(html_path, current_html)
        metrics_path = _write_fix_metrics(pdf_dir, metrics)
        return {
            "accepted": False,
            "rejected_reason": "missing_markers",
            "render_after_path": render_after_path,
            "render_after_full_path": None,
            "metrics_path": metrics_path,
            "raw_response": raw_response,
        }

    tokens_before = _extract_tokens(current_html)
    tokens_after = _extract_tokens(refined_html)
    if tokens_before != tokens_after:
        logger.warning(
            "template_fix_html_token_drift",
            extra={
                "event": "template_fix_html_token_drift",
                "tokens_missing": sorted(tokens_before - tokens_after),
                "tokens_added": sorted(tokens_after - tokens_before),
            },
        )
        metrics["rejected_reason"] = "token_drift"
        save_html(html_path, current_html)
        metrics_path = _write_fix_metrics(pdf_dir, metrics)
        return {
            "accepted": False,
            "rejected_reason": "token_drift",
            "render_after_path": render_after_path,
            "render_after_full_path": None,
            "metrics_path": metrics_path,
            "raw_response": raw_response,
        }

    repeats_before = _repeat_marker_counts(current_html)
    repeats_after = _repeat_marker_counts(refined_html)
    if repeats_before != repeats_after:
        logger.warning(
            "template_fix_html_repeat_marker_drift",
            extra={
                "event": "template_fix_html_repeat_marker_drift",
                "before": repeats_before,
                "after": repeats_after,
            },
        )
        metrics["rejected_reason"] = "repeat_marker_drift"
        save_html(html_path, current_html)
        metrics_path = _write_fix_metrics(pdf_dir, metrics)
        return {
            "accepted": False,
            "rejected_reason": "repeat_marker_drift",
            "render_after_path": render_after_path,
            "render_after_full_path": None,
            "metrics_path": metrics_path,
            "raw_response": raw_response,
        }

    prototype_before = _prototype_row_counts(current_html)
    prototype_after = _prototype_row_counts(refined_html)
    if prototype_before != prototype_after:
        logger.warning(
            "template_fix_html_prototype_row_drift",
            extra={
                "event": "template_fix_html_prototype_row_drift",
                "before": prototype_before,
                "after": prototype_after,
            },
        )
        metrics["rejected_reason"] = "prototype_row_drift"
        save_html(html_path, current_html)
        metrics_path = _write_fix_metrics(pdf_dir, metrics)
        return {
            "accepted": False,
            "rejected_reason": "prototype_row_drift",
            "render_after_path": render_after_path,
            "render_after_full_path": None,
            "metrics_path": metrics_path,
            "raw_response": raw_response,
        }

    save_html(html_path, refined_html)
    metrics["accepted"] = True

    render_after_full_path = pdf_dir / "render_p1_after_full.png"
    render_html_to_png(html_path, render_after_full_path)
    render_after_path = pdf_dir / "render_p1_after.png"
    render_panel_preview(html_path, render_after_path, fallback_png=render_after_full_path)
    metrics_path = _write_fix_metrics(pdf_dir, metrics)

    logger.info(
        "template_fix_html_complete",
        extra={
            "event": "template_fix_html_complete",
            "accepted": metrics["accepted"],
        },
    )

    return {
        "accepted": True,
        "rejected_reason": None,
        "render_after_path": render_after_path,
        "render_after_full_path": render_after_full_path,
        "metrics_path": metrics_path,
        "raw_response": raw_response,
    }


async def main():
    raise RuntimeError("Legacy CLI entrypoint removed. Use the API verify flow instead.")


if __name__ == "__main__":
    asyncio.run(main())
