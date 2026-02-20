from __future__ import annotations

import contextlib
import difflib
import json
import logging
from pathlib import Path
from typing import Any, Mapping, Optional

from fastapi import Request

logger = logging.getLogger(__name__)

from backend.app.services.templates.TemplateVerify import MODEL, get_openai_client
from backend.app.services.utils import (
    TemplateLockError,
    acquire_template_lock,
    get_correlation_id,
    write_text_atomic,
    write_json_atomic,
    call_chat_completion,
    strip_code_fences,
)
from backend.app.services.utils.text import extract_json_object
from backend.legacy.schemas.template_schema import (
    TemplateAiEditPayload,
    TemplateCreateFromChatPayload,
    TemplateManualEditPayload,
    TemplateChatPayload,
    TemplateChatResponse,
)
from backend.legacy.utils.template_utils import template_dir

from .helpers import (
    append_template_history_entry,
    http_error,
    load_template_generator_summary,
    read_template_history,
    resolve_template_kind,
    update_template_generator_summary_for_edit,
)


def _summarize_html_diff(before: str, after: str) -> str:
    before_lines = (before or "").splitlines()
    after_lines = (after or "").splitlines()
    matcher = difflib.SequenceMatcher(None, before_lines, after_lines, autojunk=False)
    added = 0
    removed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
        if tag in ("replace", "insert"):
            added += j2 - j1
    parts: list[str] = []
    if added:
        parts.append(f"+{added} line{'s' if added != 1 else ''}")
    if removed:
        parts.append(f"-{removed} line{'s' if removed != 1 else ''}")
    if not parts:
        return "no line changes"
    return ", ".join(parts)


def _snapshot_final_html(template_dir_path: Path, final_path: Path, base_path: Path) -> str:
    if final_path.exists():
        source_path = final_path
    elif base_path.exists():
        source_path = base_path
    else:
        raise http_error(
            404,
            "template_html_missing",
            "Template HTML not found (report_final.html or template_p1.html).",
        )

    current_html = source_path.read_text(encoding="utf-8", errors="ignore")

    if source_path is base_path and not final_path.exists():
        write_text_atomic(final_path, current_html, encoding="utf-8", step="template_edit_seed_final")

    prev_path = template_dir_path / "report_final_prev.html"
    write_text_atomic(prev_path, current_html, encoding="utf-8", step="template_edit_prev")
    return current_html


def _build_template_html_response(
    *,
    template_id: str,
    kind: str,
    html: str,
    source: str,
    template_dir_path: Path,
    history: Optional[list[dict]] = None,
    summary: Optional[Mapping[str, Any]] = None,
    ai_summary: Optional[list[str]] = None,
    correlation_id: str | None = None,
    diff_summary: str | None = None,
) -> dict:
    prev_path = template_dir_path / "report_final_prev.html"
    effective_history = history if history is not None else read_template_history(template_dir_path)
    summary_payload = dict(summary or {})
    metadata = {
        "lastEditType": summary_payload.get("lastEditType"),
        "lastEditAt": summary_payload.get("lastEditAt"),
        "lastEditNotes": summary_payload.get("lastEditNotes"),
        "historyCount": len(effective_history),
    }
    result: dict[str, Any] = {
        "status": "ok",
        "template_id": template_id,
        "kind": kind,
        "html": html,
        "source": source,
        "can_undo": prev_path.exists(),
        "metadata": metadata,
        "history": effective_history,
    }
    if diff_summary is not None:
        result["diff_summary"] = diff_summary
    if ai_summary:
        result["summary"] = ai_summary
    if correlation_id:
        result["correlation_id"] = correlation_id
    return result


def _resolve_template_html_paths(template_id: str, *, kind: str) -> tuple[Path, Path, Path, str]:
    template_dir_path = template_dir(template_id, kind=kind)
    final_path = template_dir_path / "report_final.html"
    base_path = template_dir_path / "template_p1.html"
    if final_path.exists():
        return template_dir_path, final_path, base_path, "report_final"
    if base_path.exists():
        return template_dir_path, final_path, base_path, "template_p1"
    raise http_error(
        404,
        "template_html_missing",
        "Template HTML not found (report_final.html or template_p1.html). Run template verification first.",
    )


def _run_template_edit_llm(template_html: str, instructions: str, kind: str = "pdf") -> tuple[str, list[str]]:
    if not instructions or not str(instructions).strip():
        raise http_error(400, "missing_instructions", "instructions is required for AI template edit.")
    from backend.app.services.prompts.llm_prompts_template_edit import (
        TEMPLATE_EDIT_PROMPT_VERSION,
        build_template_edit_prompt,
    )

    prompt_payload = build_template_edit_prompt(template_html, instructions, kind=kind)
    messages = prompt_payload.get("messages") or []
    if not messages:
        raise http_error(500, "prompt_build_failed", "Failed to build template edit prompt.")
    try:
        client = get_openai_client()
    except Exception as exc:
        logger.exception("LLM client is unavailable")
        raise http_error(503, "llm_unavailable", "LLM client is unavailable")

    try:
        response = call_chat_completion(client, model=MODEL, messages=messages, description=TEMPLATE_EDIT_PROMPT_VERSION)
    except Exception as exc:
        logger.exception("Template edit LLM call failed")
        raise http_error(502, "llm_call_failed", "Template edit LLM call failed")

    raw_text = (response.choices[0].message.content or "").strip()
    payload = extract_json_object(raw_text)
    if payload is None:
        logger.error("LLM did not return valid JSON: %s", raw_text[:500])
        raise http_error(502, "llm_invalid_response", "LLM did not return valid JSON")

    if not isinstance(payload, dict):
        raise http_error(502, "llm_invalid_response", "LLM response was not a JSON object.")

    updated_html = payload.get("updated_html")
    if not isinstance(updated_html, str) or not updated_html.strip():
        raise http_error(502, "llm_invalid_response", "LLM response missing 'updated_html' string.")

    summary_raw = payload.get("summary")
    summary: list[str] = []
    if isinstance(summary_raw, list):
        for item in summary_raw:
            text = str(item).strip()
            if text:
                summary.append(text)
    elif isinstance(summary_raw, str):
        text = summary_raw.strip()
        if text:
            summary.append(text)

    return updated_html, summary


def get_template_html(template_id: str, request: Request):
    template_kind = resolve_template_kind(template_id)
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    template_dir_path, final_path, base_path, source = _resolve_template_html_paths(template_id, kind=template_kind)
    active_path = final_path if source == "report_final" else base_path
    html_text = active_path.read_text(encoding="utf-8", errors="ignore")
    history = read_template_history(template_dir_path)
    summary = load_template_generator_summary(template_id)
    return _build_template_html_response(
        template_id=template_id,
        kind=template_kind,
        html=html_text,
        source=source,
        template_dir_path=template_dir_path,
        history=history,
        summary=summary,
        correlation_id=correlation_id,
    )


def edit_template_manual(template_id: str, payload: TemplateManualEditPayload, request: Request):
    template_kind = resolve_template_kind(template_id)
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    template_dir_path, final_path, base_path, _ = _resolve_template_html_paths(template_id, kind=template_kind)
    try:
        lock_ctx = acquire_template_lock(template_dir_path, "template_edit_manual", correlation_id)
    except TemplateLockError:
        raise http_error(409, "template_locked", "Template is currently processing another request.")

    with lock_ctx:
        current_html = _snapshot_final_html(template_dir_path, final_path, base_path)

        new_html = payload.html or ""
        write_text_atomic(final_path, new_html, encoding="utf-8", step="template_edit_manual")
        diff_summary = _summarize_html_diff(current_html, new_html)

        notes = "Manual HTML edit via template editor"
        summary = update_template_generator_summary_for_edit(template_id, edit_type="manual", notes=notes)
        history_entry = {"timestamp": summary.get("lastEditAt") or None, "type": "manual", "notes": notes}
        history = append_template_history_entry(template_dir_path, history_entry)

    return _build_template_html_response(
        template_id=template_id,
        kind=template_kind,
        html=new_html,
        source="report_final",
        template_dir_path=template_dir_path,
        history=history,
        summary=summary,
        correlation_id=correlation_id,
        diff_summary=diff_summary,
    )


def edit_template_ai(template_id: str, payload: TemplateAiEditPayload, request: Request):
    template_kind = resolve_template_kind(template_id)
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    template_dir_path, final_path, base_path, _ = _resolve_template_html_paths(template_id, kind=template_kind)
    try:
        lock_ctx = acquire_template_lock(template_dir_path, "template_edit_ai", correlation_id)
    except TemplateLockError:
        raise http_error(409, "template_locked", "Template is currently processing another request.")

    with lock_ctx:
        current_html = _snapshot_final_html(template_dir_path, final_path, base_path)

        llm_input_html = payload.html.strip() if isinstance(payload.html, str) and payload.html.strip() else current_html
        updated_html, change_summary = _run_template_edit_llm(llm_input_html, payload.instructions or "", kind=template_kind)
        write_text_atomic(final_path, updated_html, encoding="utf-8", step="template_edit_ai")
        diff_summary = _summarize_html_diff(current_html, updated_html)

        notes = "AI-assisted HTML edit via template editor"
        summary = update_template_generator_summary_for_edit(template_id, edit_type="ai", notes=notes)
        history_entry = {
            "timestamp": summary.get("lastEditAt") or None,
            "type": "ai",
            "notes": notes,
            "instructions": payload.instructions or "",
            "summary": change_summary,
        }
        history = append_template_history_entry(template_dir_path, history_entry)

    return _build_template_html_response(
        template_id=template_id,
        kind=template_kind,
        html=updated_html,
        source="report_final",
        template_dir_path=template_dir_path,
        history=history,
        summary=summary,
        ai_summary=change_summary,
        correlation_id=correlation_id,
        diff_summary=diff_summary,
    )


def undo_last_template_edit(template_id: str, request: Request):
    template_kind = resolve_template_kind(template_id)
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    template_dir_path = template_dir(template_id, kind=template_kind)
    final_path = template_dir_path / "report_final.html"
    prev_path = template_dir_path / "report_final_prev.html"

    if not prev_path.exists() or not prev_path.is_file():
        raise http_error(400, "no_previous_version", "No previous template version found to undo.")
    if not final_path.exists() or not final_path.is_file():
        raise http_error(404, "template_html_missing", "Current template HTML not found for undo.")

    try:
        lock_ctx = acquire_template_lock(template_dir_path, "template_edit_undo", correlation_id)
    except TemplateLockError:
        raise http_error(409, "template_locked", "Template is currently processing another request.")

    with lock_ctx:
        tmp_path = template_dir_path / "report_final_undo_tmp.html"
        tmp_path.unlink(missing_ok=True)

        current_html = final_path.read_text(encoding="utf-8", errors="ignore")
        try:
            final_path.rename(tmp_path)
            prev_path.rename(final_path)
            tmp_path.rename(prev_path)
        except Exception as exc:
            with contextlib.suppress(Exception):
                if tmp_path.exists() and not final_path.exists():
                    tmp_path.rename(final_path)
            logger.exception("Failed to restore previous template version")
            raise http_error(500, "undo_failed", "Failed to restore previous template version")

        restored_html = final_path.read_text(encoding="utf-8", errors="ignore")
        diff_summary = _summarize_html_diff(current_html, restored_html)

        notes = "Undo last template HTML edit"
        summary = update_template_generator_summary_for_edit(template_id, edit_type="undo", notes=notes)
        history_entry = {"timestamp": summary.get("lastEditAt") or None, "type": "undo", "notes": notes}
        history = append_template_history_entry(template_dir_path, history_entry)

    return _build_template_html_response(
        template_id=template_id,
        kind=template_kind,
        html=restored_html,
        source="report_final",
        template_dir_path=template_dir_path,
        history=history,
        summary=summary,
        correlation_id=correlation_id,
        diff_summary=diff_summary,
    )


def _run_template_chat_llm(template_html: str, conversation_history: list[dict], kind: str = "pdf") -> dict:
    """
    Run the conversational template editing LLM.

    Returns a dict with:
        - message: str
        - ready_to_apply: bool
        - proposed_changes: list[str] | None
        - follow_up_questions: list[str] | None
        - updated_html: str | None
    """
    from backend.app.services.prompts.llm_prompts_template_chat import (
        TEMPLATE_CHAT_PROMPT_VERSION,
        build_template_chat_prompt,
    )

    prompt_payload = build_template_chat_prompt(template_html, conversation_history, kind=kind)
    messages = prompt_payload.get("messages") or []
    if not messages:
        raise http_error(500, "prompt_build_failed", "Failed to build template chat prompt.")

    try:
        client = get_openai_client()
    except Exception as exc:
        logger.exception("LLM client is unavailable")
        raise http_error(503, "llm_unavailable", "LLM client is unavailable")

    try:
        response = call_chat_completion(
            client, model=MODEL, messages=messages, description=TEMPLATE_CHAT_PROMPT_VERSION
        )
    except Exception as exc:
        logger.exception("Template chat LLM call failed")
        raise http_error(502, "llm_call_failed", "Template chat LLM call failed")

    raw_text = (response.choices[0].message.content or "").strip()
    payload = extract_json_object(raw_text)
    if payload is None:
        # If JSON parsing fails, return a friendly error response
        return {
            "message": "I apologize, but I encountered an issue processing your request. Could you please rephrase or try again?",
            "ready_to_apply": False,
            "proposed_changes": None,
            "follow_up_questions": ["Could you describe what changes you'd like to make to the template?"],
            "updated_html": None,
        }

    if not isinstance(payload, dict):
        return {
            "message": "I apologize, but I encountered an issue. Could you please try again?",
            "ready_to_apply": False,
            "proposed_changes": None,
            "follow_up_questions": None,
            "updated_html": None,
        }

    return {
        "message": payload.get("message", ""),
        "ready_to_apply": bool(payload.get("ready_to_apply", False)),
        "proposed_changes": payload.get("proposed_changes"),
        "follow_up_questions": payload.get("follow_up_questions"),
        "updated_html": payload.get("updated_html"),
    }


def chat_template_edit(template_id: str, payload: TemplateChatPayload, request: Request):
    """
    Handle a conversational template editing request.

    This endpoint maintains a conversation with the user to gather requirements
    before applying changes to the template. The LLM will ask clarifying questions
    if needed, and only apply changes when it has enough information.
    """
    template_kind = resolve_template_kind(template_id)
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    template_dir_path, final_path, base_path, _ = _resolve_template_html_paths(template_id, kind=template_kind)

    # Get current HTML - use provided HTML or load from disk
    if payload.html and payload.html.strip():
        current_html = payload.html.strip()
    else:
        active_path = final_path if final_path.exists() else base_path
        current_html = active_path.read_text(encoding="utf-8", errors="ignore")

    # Convert messages to the format expected by the prompt builder
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in payload.messages
    ]

    # Call the LLM
    llm_response = _run_template_chat_llm(current_html, conversation_history, kind=template_kind)

    result = {
        "status": "ok",
        "template_id": template_id,
        "message": llm_response["message"],
        "ready_to_apply": llm_response["ready_to_apply"],
        "proposed_changes": llm_response.get("proposed_changes"),
        "follow_up_questions": llm_response.get("follow_up_questions"),
        "correlation_id": correlation_id,
    }

    # If ready to apply, include the updated HTML
    if llm_response["ready_to_apply"] and llm_response.get("updated_html"):
        result["updated_html"] = llm_response["updated_html"]

    return result


def apply_chat_template_edit(template_id: str, html: str, request: Request):
    """
    Apply the HTML changes from a chat conversation.

    This is called after the user confirms they want to apply the proposed changes.
    """
    template_kind = resolve_template_kind(template_id)
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    template_dir_path, final_path, base_path, _ = _resolve_template_html_paths(template_id, kind=template_kind)

    try:
        lock_ctx = acquire_template_lock(template_dir_path, "template_edit_chat_apply", correlation_id)
    except TemplateLockError:
        raise http_error(409, "template_locked", "Template is currently processing another request.")

    with lock_ctx:
        current_html = _snapshot_final_html(template_dir_path, final_path, base_path)

        new_html = html or ""
        write_text_atomic(final_path, new_html, encoding="utf-8", step="template_edit_chat_apply")
        diff_summary = _summarize_html_diff(current_html, new_html)

        notes = "AI chat-assisted HTML edit via template editor"
        summary = update_template_generator_summary_for_edit(template_id, edit_type="chat", notes=notes)
        history_entry = {
            "timestamp": summary.get("lastEditAt") or None,
            "type": "chat",
            "notes": notes,
        }
        history = append_template_history_entry(template_dir_path, history_entry)

    return _build_template_html_response(
        template_id=template_id,
        kind=template_kind,
        html=new_html,
        source="report_final",
        template_dir_path=template_dir_path,
        history=history,
        summary=summary,
        correlation_id=correlation_id,
        diff_summary=diff_summary,
    )


def _convert_sample_pdf_to_b64(pdf_bytes: bytes) -> str | None:
    """Convert raw PDF bytes to a base64-encoded PNG of the first page."""
    import tempfile
    import base64

    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF not available — cannot render sample PDF")
        return None

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = Path(tmp.name)

        doc = fitz.open(tmp_path)
        zoom = 300 / 72.0  # 300 DPI
        mat = fitz.Matrix(zoom, zoom)
        page = doc[0]
        pix = page.get_pixmap(matrix=mat, alpha=False)
        png_bytes = pix.tobytes("png")
        doc.close()
        tmp_path.unlink(missing_ok=True)

        return base64.b64encode(png_bytes).decode("utf-8")
    except Exception:
        logger.exception("Failed to convert sample PDF to image")
        return None


def _run_template_chat_create_llm(
    conversation_history: list[dict],
    current_html: str | None = None,
    sample_image_b64: str | None = None,
    kind: str = "pdf",
) -> dict:
    """
    Run the conversational template creation LLM.

    Returns same shape as _run_template_chat_llm.
    """
    from backend.app.services.prompts.llm_prompts_template_chat import (
        TEMPLATE_CHAT_CREATE_PROMPT_VERSION,
        build_template_chat_create_prompt,
    )

    prompt_payload = build_template_chat_create_prompt(
        conversation_history, current_html, sample_image_b64=sample_image_b64, kind=kind,
    )
    messages = prompt_payload.get("messages") or []
    if not messages:
        raise http_error(500, "prompt_build_failed", "Failed to build template chat create prompt.")

    try:
        client = get_openai_client()
    except Exception:
        logger.exception("LLM client is unavailable")
        raise http_error(503, "llm_unavailable", "LLM client is unavailable")

    try:
        response = call_chat_completion(
            client, model=MODEL, messages=messages, description=TEMPLATE_CHAT_CREATE_PROMPT_VERSION
        )
    except Exception:
        logger.exception("Template chat create LLM call failed")
        raise http_error(502, "llm_call_failed", "Template chat create LLM call failed")

    raw_text = (response.choices[0].message.content or "").strip()
    payload = extract_json_object(raw_text)
    if not isinstance(payload, dict):
        # Log the raw text so we can debug JSON parse failures
        logger.warning(
            "template_chat_create_json_parse_failed",
            extra={
                "event": "template_chat_create_json_parse_failed",
                "raw_text_length": len(raw_text),
                "raw_text_preview": raw_text[:500],
            },
        )
        # Fallback: if the LLM returned plain text (not JSON), use it as the message
        # This is better than showing "I apologize" — the LLM's text is still useful
        if raw_text and len(raw_text) > 20:
            return {
                "message": raw_text,
                "ready_to_apply": False,
                "proposed_changes": None,
                "follow_up_questions": None,
                "updated_html": None,
            }
        return {
            "message": "I apologize, but I encountered an issue processing your request. Could you please rephrase or try again?",
            "ready_to_apply": False,
            "proposed_changes": None,
            "follow_up_questions": ["Could you describe what kind of report template you need?"],
            "updated_html": None,
        }

    return {
        "message": payload.get("message", ""),
        "ready_to_apply": bool(payload.get("ready_to_apply", False)),
        "proposed_changes": payload.get("proposed_changes"),
        "follow_up_questions": payload.get("follow_up_questions"),
        "updated_html": payload.get("updated_html"),
    }


def chat_template_create(
    payload: TemplateChatPayload,
    request: Request,
    sample_pdf_bytes: bytes | None = None,
    kind: str = "pdf",
):
    """
    Handle a conversational template creation request (no template_id needed).

    The LLM will guide the user through creating a template from scratch.
    Optionally accepts a sample PDF (as raw bytes) for visual reference.
    """
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()

    current_html = (payload.html or "").strip() or None

    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in payload.messages
    ]

    # Convert sample PDF to base64 image if provided
    sample_image_b64 = None
    if sample_pdf_bytes:
        sample_image_b64 = _convert_sample_pdf_to_b64(sample_pdf_bytes)

    llm_response = _run_template_chat_create_llm(
        conversation_history, current_html, sample_image_b64=sample_image_b64, kind=kind,
    )

    result = {
        "status": "ok",
        "message": llm_response["message"],
        "ready_to_apply": llm_response["ready_to_apply"],
        "proposed_changes": llm_response.get("proposed_changes"),
        "follow_up_questions": llm_response.get("follow_up_questions"),
        "correlation_id": correlation_id,
    }

    if llm_response["ready_to_apply"] and llm_response.get("updated_html"):
        result["updated_html"] = llm_response["updated_html"]

    return result


def create_template_from_chat(payload: TemplateCreateFromChatPayload, request: Request):
    """
    Persist a template created from the chat conversation.

    Creates the template directory, writes the HTML, and registers it in state.
    """
    import re
    import backend.app.services.state_access as state_access
    from backend.legacy.utils.template_utils import normalize_template_id

    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()

    name = (payload.name or "").strip()
    if not name:
        raise http_error(400, "missing_name", "Template name is required.")

    html = payload.html or ""
    kind = (payload.kind or "pdf").lower()
    if kind not in ("pdf", "excel"):
        raise http_error(400, "invalid_kind", "kind must be 'pdf' or 'excel'.")

    # Slugify name to template_id
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        slug = "chat-template"
    template_id = normalize_template_id(slug)

    # Create directory
    template_dir_path = template_dir(template_id, kind=kind, must_exist=False, create=True)

    final_path = template_dir_path / "report_final.html"
    write_text_atomic(final_path, html, encoding="utf-8", step="create_template_from_chat")

    # Also write template_p1.html so the mapping pipeline can find it
    # (mapping preview/approve expect template_p1.html from the verify step)
    p1_path = template_dir_path / "template_p1.html"
    if not p1_path.exists():
        write_text_atomic(p1_path, html, encoding="utf-8", step="create_template_from_chat_p1")

    # Extract tokens from the HTML for metadata
    import re as _re
    _TOKEN_RE = _re.compile(r"\{\{?\s*([A-Za-z0-9_\-\.]+)\s*\}\}?")
    _BLOCK_RE = _re.compile(r"<!--\s*BEGIN:BLOCK_REPEAT\b", _re.IGNORECASE)
    tokens_found = sorted(set(_TOKEN_RE.findall(html)))
    has_block_repeat = bool(_BLOCK_RE.search(html))

    # --- Build schema_ext.json by classifying tokens from HTML structure ---
    # Tokens inside <table> rows (between <tr>...</tr>) → row_tokens
    # Tokens near totals (tfoot, or rows with "total" in nearby text) → totals
    # Everything else → scalars
    scalars, row_tokens, totals = [], [], []

    # Identify tokens that appear inside table body rows
    _TR_RE = _re.compile(r"<tr\b[^>]*>(.*?)</tr>", _re.IGNORECASE | _re.DOTALL)
    _THEAD_RE = _re.compile(r"<thead\b[^>]*>.*?</thead>", _re.IGNORECASE | _re.DOTALL)
    _TFOOT_RE = _re.compile(r"<tfoot\b[^>]*>(.*?)</tfoot>", _re.IGNORECASE | _re.DOTALL)
    _TABLE_RE = _re.compile(r"<table\b[^>]*>(.*?)</table>", _re.IGNORECASE | _re.DOTALL)

    table_row_tokens = set()
    totals_tokens = set()

    # Check tokens in tfoot first (these are totals)
    for tfoot_match in _TFOOT_RE.finditer(html):
        tfoot_text = tfoot_match.group(1)
        for tok in _TOKEN_RE.findall(tfoot_text):
            totals_tokens.add(tok)

    # Check tokens in table rows (excluding thead, tfoot)
    for table_match in _TABLE_RE.finditer(html):
        table_html = table_match.group(1)
        # Strip thead and tfoot to get tbody content
        body_html = _THEAD_RE.sub("", table_html)
        body_html = _TFOOT_RE.sub("", body_html)
        for tr_match in _TR_RE.finditer(body_html):
            row_text = tr_match.group(1)
            row_lower = row_text.lower()
            for tok in _TOKEN_RE.findall(row_text):
                if tok in totals_tokens:
                    continue
                # If row contains "total" text, classify as totals
                if "total" in row_lower or "grand" in row_lower or "sum" in row_lower:
                    totals_tokens.add(tok)
                else:
                    table_row_tokens.add(tok)

    # Also check for BLOCK_REPEAT tokens → row_tokens
    _BLOCK_SECTION_RE = _re.compile(
        r"<!--\s*BEGIN:BLOCK_REPEAT\b.*?-->(.+?)<!--\s*END:BLOCK_REPEAT\s*-->",
        _re.IGNORECASE | _re.DOTALL,
    )
    for block_match in _BLOCK_SECTION_RE.finditer(html):
        block_text = block_match.group(1)
        for tok in _TOKEN_RE.findall(block_text):
            if tok not in totals_tokens:
                table_row_tokens.add(tok)

    for tok in tokens_found:
        if tok in totals_tokens:
            totals.append(tok)
        elif tok in table_row_tokens:
            row_tokens.append(tok)
        else:
            scalars.append(tok)

    schema_ext = {"scalars": scalars, "row_tokens": row_tokens, "totals": totals}
    schema_path = template_dir_path / "schema_ext.json"
    write_json_atomic(schema_path, schema_ext, indent=2, ensure_ascii=False, step="create_template_schema_ext")

    # --- Build page_summary.txt for the contract builder ---
    page_summary_lines = [
        f"Template: {name}",
        f"Type: {kind}",
        f"Created from: AI chat conversation",
        f"Total tokens: {len(tokens_found)}",
        f"  Scalars: {', '.join(scalars[:20]) if scalars else '(none)'}",
        f"  Row tokens: {', '.join(row_tokens[:20]) if row_tokens else '(none)'}",
        f"  Totals: {', '.join(totals[:10]) if totals else '(none)'}",
        f"Has block repeat: {has_block_repeat}",
    ]
    page_summary_path = template_dir_path / "page_summary.txt"
    write_text_atomic(
        page_summary_path,
        "\n".join(page_summary_lines),
        encoding="utf-8",
        step="create_template_page_summary",
    )

    # Register in state
    state_access.upsert_template(
        template_id,
        name=name,
        status="draft",
        artifacts={},
        template_type=kind,
    )

    # Write initial history
    notes = "Template created from AI chat conversation"
    summary = update_template_generator_summary_for_edit(template_id, edit_type="chat", notes=notes)
    history_entry = {
        "timestamp": summary.get("lastEditAt"),
        "type": "chat",
        "notes": notes,
    }
    append_template_history_entry(template_dir_path, history_entry)

    return {
        "status": "ok",
        "template_id": template_id,
        "name": name,
        "kind": kind,
        "tokens": tokens_found,
        "has_block_repeat": has_block_repeat,
        "schema": schema_ext,
        "correlation_id": correlation_id,
    }
