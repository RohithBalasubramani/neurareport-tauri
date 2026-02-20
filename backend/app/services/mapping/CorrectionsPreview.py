from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any, Collection, Mapping, Sequence

from ..prompts.llm_prompts import PROMPT_VERSION_3_5, build_llm_call_3_5_prompt
from ..templates.TemplateVerify import MODEL, get_openai_client
from ..utils import (
    call_chat_completion,
    extract_tokens,
    strip_code_fences,
    validate_llm_call_3_5,
    write_artifact_manifest,
    write_json_atomic,
    write_text_atomic,
)
from ..utils.validation import SchemaValidationError
from .HeaderMapping import INPUT_SAMPLE, REPORT_SELECTED_DISPLAY, REPORT_SELECTED_VALUE

logger = logging.getLogger("neura.mapping.corrections_preview")

_REPEAT_MARKER_RE = re.compile(r"<!--\s*(BEGIN:BLOCK_REPEAT|END:BLOCK_REPEAT)[^>]*-->", re.IGNORECASE)
_DATA_REGION_RE = re.compile(r'data-region\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_TBODY_RE = re.compile(r"<tbody\b", re.IGNORECASE)
_TR_RE = re.compile(r"<tr\b", re.IGNORECASE)
_SAMPLE_VALUE_TOKEN_RE = re.compile(r"[A-Za-z0-9%._-]+")

VALUE_SAMPLE = INPUT_SAMPLE
VALUE_LATER_SELECTED = REPORT_SELECTED_VALUE
_REPORT_DATE_PREFIXES = {
    "from",
    "to",
    "start",
    "end",
    "begin",
    "finish",
    "through",
    "thru",
}
_REPORT_DATE_KEYWORDS = {
    "date",
    "dt",
    "day",
    "period",
    "range",
    "time",
    "timestamp",
    "window",
    "month",
    "year",
}
_REPORT_SELECTED_EXACT = {
    "page_info",
    "page_number",
    "page_no",
    "page_num",
    "page_count",
    "page_total",
    "page_total_count",
}
_REPORT_SELECTED_KEYWORDS = {"page", "sheet"}
_REPORT_SELECTED_SUFFIXES = {"info", "number", "no", "num", "count", "total"}


class CorrectionsPreviewError(RuntimeError):
    """Raised when LLM Call 3.5 outputs invalid data."""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_path(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _count_repeat_markers(html: str) -> int:
    return len(_REPEAT_MARKER_RE.findall(html or ""))


def _count_tbody(html: str) -> int:
    return len(_TBODY_RE.findall(html or ""))


def _tbody_row_signature(html: str) -> list[int]:
    signatures: list[int] = []
    tbody_pattern = re.compile(r"(<tbody\b[^>]*>)(.*?)(</tbody>)", re.IGNORECASE | re.DOTALL)
    for match in tbody_pattern.finditer(html or ""):
        body = match.group(2)
        signatures.append(len(_TR_RE.findall(body)))
    return signatures


def _data_regions(html: str) -> set[str]:
    return {match.strip() for match in _DATA_REGION_RE.findall(html or "") if match.strip()}


def _normalize_token_parts(token: str) -> list[str]:
    token = (token or "").strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", token)
    return [part for part in normalized.split("_") if part]


def _is_report_generator_date_token(token: str) -> bool:
    if not token:
        return False
    low = token.strip().lower()
    if low in _REPORT_SELECTED_EXACT:
        return True
    parts = _normalize_token_parts(token)
    if not parts:
        return False
    if any(part in _REPORT_SELECTED_KEYWORDS for part in parts) and any(
        part in _REPORT_SELECTED_SUFFIXES for part in parts
    ):
        return True
    has_prefix = any(part in _REPORT_DATE_PREFIXES for part in parts)
    has_keyword = any(part in _REPORT_DATE_KEYWORDS for part in parts)
    if has_prefix and has_keyword:
        return True
    if parts[0] in _REPORT_DATE_KEYWORDS and any(part in _REPORT_DATE_PREFIXES for part in parts[1:]):
        return True
    if parts[-1] in _REPORT_DATE_KEYWORDS and any(part in _REPORT_DATE_PREFIXES for part in parts[:-1]):
        return True
    return False


def _is_sample_value(value: str) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.strip().lower()
    if not lowered:
        return False
    return lowered in {VALUE_SAMPLE.lower(), VALUE_LATER_SELECTED.lower()}


def _is_report_selected_value(value: str) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.strip().lower()
    if not lowered:
        return False
    if lowered == VALUE_LATER_SELECTED.lower():
        return True
    return lowered.startswith("to be selected")


def _display_mapping_value(token: str, value: str) -> str:
    if not isinstance(value, str):
        return value
    trimmed = value.strip()
    if not trimmed:
        return trimmed
    if _is_report_generator_date_token(token):
        if _is_report_selected_value(trimmed):
            return REPORT_SELECTED_DISPLAY
        if _is_sample_value(trimmed):
            return VALUE_SAMPLE
    return trimmed


def _ensure_invariants(
    original_html: str,
    final_html: str,
    expected_inline_tokens: Collection[str] | None = None,
    additional_constants: Collection[Mapping[str, Any]] | None = None,
    sample_values: Mapping[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    expected_inline_tokens = expected_inline_tokens or ()
    expected_inline = {str(tok) for tok in expected_inline_tokens if str(tok)}
    if additional_constants:
        for entry in additional_constants:
            token = str((entry or {}).get("token") or "").strip()
            if token:
                expected_inline.add(token)
    original_tokens = set(extract_tokens(original_html))
    final_tokens = set(extract_tokens(final_html))

    unexpected_tokens = final_tokens - original_tokens
    if unexpected_tokens:
        raise CorrectionsPreviewError("New tokens introduced in final template: " f"{sorted(unexpected_tokens)}")

    removed_tokens = original_tokens - final_tokens
    missing_expected = sorted(expected_inline - removed_tokens)
    unexpected_removed = sorted(removed_tokens - expected_inline)

    if _count_repeat_markers(original_html) != _count_repeat_markers(final_html):
        raise CorrectionsPreviewError("Repeat marker count changed between original and final HTML.")

    if _count_tbody(original_html) != _count_tbody(final_html):
        raise CorrectionsPreviewError("<tbody> element count changed between original and final HTML.")

    if _tbody_row_signature(original_html) != _tbody_row_signature(final_html):
        raise CorrectionsPreviewError("Row prototype counts differ between original and final HTML.")

    original_regions = _data_regions(original_html)
    final_regions = _data_regions(final_html)
    if original_regions != final_regions:
        raise CorrectionsPreviewError(
            f"data-region attributes changed. Expected {sorted(original_regions)}, got {sorted(final_regions)}"
        )

    for token, sample in (sample_values or {}).items():
        sample_text = str(sample or "").strip()
        if not sample_text:
            continue
        if sample_text in final_html:
            raise CorrectionsPreviewError(f"Sample value leaked into final template for token {token!r}.")

    return sorted(removed_tokens), missing_expected, unexpected_removed


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CorrectionsPreviewError(f"Failed to parse JSON file: {path.name}") from exc


def _default_schema(schema: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if schema is None:
        return {"scalars": [], "row_tokens": [], "totals": [], "notes": ""}
    payload = dict(schema)
    payload.setdefault("scalars", [])
    payload.setdefault("row_tokens", [])
    payload.setdefault("totals", [])
    payload.setdefault("notes", "")
    return payload


def run_corrections_preview(
    upload_dir: Path,
    template_html_path: Path,
    mapping_step3_path: Path,
    schema_ext_path: Path,
    user_input: str,
    page_png_path: Path | None = None,
    model_selector: str | None = None,
    mapping_override: Mapping[str, Any] | None = None,
    sample_tokens: Sequence[str] | None = None,
    *,
    prompt_builder=build_llm_call_3_5_prompt,
    prompt_version: str = PROMPT_VERSION_3_5,
) -> dict[str, Any]:
    upload_dir = upload_dir.resolve()
    template_html_path = template_html_path.resolve()
    mapping_step3_path = mapping_step3_path.resolve()
    mapping_labels_path = upload_dir / "mapping_pdf_labels.json"

    if not template_html_path.exists():
        raise CorrectionsPreviewError("template_p1.html not found. Run Step 3 before corrections preview.")
    if not mapping_step3_path.exists():
        raise CorrectionsPreviewError("mapping_step3.json not found. Run Step 3 before corrections preview.")

    template_html_original = template_html_path.read_text(encoding="utf-8", errors="ignore")
    mapping_payload = _load_json(mapping_step3_path)
    mapping_raw = mapping_payload.get("mapping") or {}
    if not isinstance(mapping_raw, Mapping):
        raise CorrectionsPreviewError("mapping_step3.json missing 'mapping' dictionary.")
    mapping_override = mapping_override or {}

    def _normalize_mapping(source: Mapping[str, Any]) -> dict[str, str]:
        cleaned: dict[str, str] = {}
        for key, value in source.items():
            token = str(key or "").strip()
            if not token:
                continue
            if value is None:
                cleaned[token] = ""
            else:
                cleaned[token] = str(value).strip()
        return cleaned

    mapping_clean = _normalize_mapping(mapping_raw)
    override_clean = _normalize_mapping(mapping_override) if isinstance(mapping_override, Mapping) else {}

    def _coerce_report_selected(values: dict[str, str]) -> None:
        for token, val in list(values.items()):
            if not _is_report_generator_date_token(token):
                continue
            normalized_val = str(val or "").strip()
            if not normalized_val:
                continue
            if _is_report_selected_value(normalized_val) or normalized_val.lower() == VALUE_SAMPLE.lower():
                values[token] = REPORT_SELECTED_VALUE

    _coerce_report_selected(mapping_clean)
    _coerce_report_selected(override_clean)

    if override_clean:
        mapping_clean.update(override_clean)

    sample_tokens_set = {str(tok).strip() for tok in (sample_tokens or []) if isinstance(tok, str) and str(tok).strip()}
    inline_expected_tokens: set[str] = {token for token, value in mapping_clean.items() if _is_sample_value(value)}
    sample_tokens_set.update(inline_expected_tokens)

    token_samples_raw = mapping_payload.get("token_samples")
    if not isinstance(token_samples_raw, Mapping):
        raw_payload_inner = mapping_payload.get("raw_payload")
        if isinstance(raw_payload_inner, Mapping):
            token_samples_raw = raw_payload_inner.get("token_samples")
    token_samples_clean: dict[str, str] | None = None
    if isinstance(token_samples_raw, Mapping):
        token_samples_clean = {
            str(key).strip(): str(value) for key, value in token_samples_raw.items() if str(key).strip()
        }
    else:
        token_samples_clean = None

    mapping_context = mapping_payload.get("raw_payload")
    if not isinstance(mapping_context, Mapping):
        mapping_context = {key: value for key, value in mapping_payload.items() if key not in {"mapping"}}
    mapping_context = dict(mapping_context)
    mapping_context["mapping"] = dict(mapping_clean)
    if override_clean:
        mapping_context["mapping_override"] = dict(override_clean)
    if sample_tokens_set:
        mapping_context["sample_tokens"] = sorted(sample_tokens_set)
    else:
        mapping_context.pop("sample_tokens", None)
    if inline_expected_tokens:
        mapping_context["inline_tokens"] = sorted(inline_expected_tokens)
    else:
        mapping_context.pop("inline_tokens", None)
    if token_samples_clean:
        mapping_context["token_samples"] = dict(token_samples_clean)
    else:
        mapping_context.pop("token_samples", None)

    if override_clean or sample_tokens_set or inline_expected_tokens:
        mapping_payload["mapping"] = mapping_clean
        mapping_payload["raw_payload"] = mapping_context
        if sample_tokens_set:
            mapping_payload["sample_tokens"] = sorted(sample_tokens_set)
        else:
            mapping_payload.pop("sample_tokens", None)
        if inline_expected_tokens:
            mapping_payload["inline_tokens"] = sorted(inline_expected_tokens)
        else:
            mapping_payload.pop("inline_tokens", None)
        write_json_atomic(
            mapping_step3_path,
            mapping_payload,
            ensure_ascii=False,
            indent=2,
            step="corrections_preview_mapping_update",
        )

    def _placeholder_for_token(token: str) -> str:
        token = token.strip()
        if not token:
            return token
        if token.startswith("{") and token.endswith("}"):
            return token
        if token.startswith("{{") and token.endswith("}}"):
            return token
        return f"{{{token}}}"

    def _load_existing_mapping_order(path: Path) -> list[str]:
        if not path.exists():
            return []
        try:
            existing_payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
        order: list[str] = []
        if isinstance(existing_payload, list):
            for entry in existing_payload:
                if not isinstance(entry, dict):
                    continue
                header = str((entry.get("header") or "")).strip()
                if header:
                    order.append(header)
        return order

    mapping_labels: list[dict[str, str]] = []
    seen_headers: set[str] = set()

    def _append_header(header: str) -> None:
        header_clean = str(header or "").strip()
        if not header_clean or header_clean in seen_headers:
            return
        raw_value = mapping_clean.get(header_clean, "")
        mapping_labels.append(
            {
                "header": header_clean,
                "placeholder": _placeholder_for_token(header_clean),
                "mapping": _display_mapping_value(header_clean, raw_value),
            }
        )
        seen_headers.add(header_clean)

    existing_order = _load_existing_mapping_order(mapping_labels_path)
    for header in existing_order:
        _append_header(header)
    for header in mapping_clean.keys():
        _append_header(header)

    if mapping_labels:
        write_json_atomic(
            mapping_labels_path,
            mapping_labels,
            ensure_ascii=False,
            indent=2,
            step="corrections_preview_mapping_labels",
        )
    schema_payload: Mapping[str, Any] | None = None
    if schema_ext_path.exists():
        try:
            schema_payload = _load_json(schema_ext_path)
        except CorrectionsPreviewError:
            schema_payload = None
    schema_payload = _default_schema(schema_payload)

    if page_png_path is None or not page_png_path.exists():
        raise CorrectionsPreviewError(
            "Reference PNG not found. Ensure template verification produced reference imagery."
        )

    mapping_bytes = mapping_step3_path.read_bytes()
    mapping_sha = hashlib.sha256(mapping_bytes).hexdigest()
    template_sha_before = _sha256_text(template_html_original)
    user_input_sha = _sha256_text(user_input or "")
    model_name = model_selector or MODEL

    cache_components = [
        template_sha_before,
        mapping_sha,
        user_input_sha,
        model_name,
        prompt_version,
    ]
    cache_key = hashlib.sha256("|".join(cache_components).encode("utf-8")).hexdigest()

    page_summary_path = upload_dir / "page_summary.txt"
    legacy_artifacts = [
        upload_dir / "report_preview.html",
        upload_dir / "edits_applied.json",
        upload_dir / "additional_constants_inlined.json",
    ]
    for legacy_path in legacy_artifacts:
        try:
            legacy_path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            logger.debug("legacy_artifact_cleanup_failed", extra={"path": str(legacy_path)})
    stage_path = upload_dir / "stage_3_5.json"

    if stage_path.exists():
        try:
            cached_stage = json.loads(stage_path.read_text(encoding="utf-8"))
        except Exception:
            cached_stage = None
        if cached_stage and cached_stage.get("cache_key") == cache_key:
            cached_final_sha = cached_stage.get("final_template_sha256")
            current_final_sha = _sha256_path(template_html_path)
            if cached_final_sha and cached_final_sha == current_final_sha:
                logger.info(
                    "corrections_preview_cache_hit",
                    extra={"event": "corrections_preview_cache_hit", "cache_key": cache_key},
                )
                result_payload = cached_stage.get("processed") or {}
                summary = cached_stage.get("summary") or {}
                artifacts = {
                    "template_html": str(template_html_path),
                    "stage": str(stage_path),
                }
                if page_summary_path.exists():
                    artifacts["page_summary"] = str(page_summary_path)
                return {
                    "cache_hit": True,
                    "cache_key": cache_key,
                    "summary": summary,
                    "processed": result_payload,
                    "artifacts": artifacts,
                }

    prompt_payload = prompt_builder(
        template_html=template_html_original,
        schema=schema_payload,
        user_input=user_input or "",
        page_png_path=str(page_png_path) if page_png_path else None,
        mapping_context=mapping_context,
    )

    system_text = prompt_payload.get("system", "")
    base_messages = prompt_payload.get("messages") or []
    if not base_messages:
        raise CorrectionsPreviewError("Prompt builder did not return messages for LLM Call 3.5.")

    client = get_openai_client()
    validation_feedback = None
    last_error: Exception | None = None
    llm_response_payload: dict[str, Any] | None = None
    for attempt in (1, 2):
        messages = [{"role": "system", "content": [{"type": "text", "text": system_text}]}]
        user_entry = json.loads(json.dumps(base_messages))  # deep copy
        if validation_feedback:
            user_entry[0]["content"].append(
                {
                    "type": "text",
                    "text": (
                        "VALIDATION_FEEDBACK:\n"
                        f"{validation_feedback}\n"
                        "Please correct the issues above and resend a compliant JSON response."
                    ),
                }
            )
        messages.extend(user_entry)

        try:
            logger.info(
                "corrections_preview_llm_start",
                extra={
                    "event": "corrections_preview_llm_start",
                    "attempt": attempt,
                    "cache_key": cache_key,
                },
            )
            response = call_chat_completion(
                client,
                model=model_name,
                messages=messages,
                description=prompt_version,
                response_format={"type": "json_object"},
                temperature=0.0,
            )
        except Exception as exc:
            logger.exception(
                "corrections_preview_llm_failure",
                extra={
                    "event": "corrections_preview_llm_failure",
                    "attempt": attempt,
                    "cache_key": cache_key,
                },
            )
            raise CorrectionsPreviewError("LLM Call 3.5 request failed.") from exc

        raw_text = (response.choices[0].message.content or "").strip()
        parsed_text = strip_code_fences(raw_text)
        try:
            payload = json.loads(parsed_text)
        except Exception as exc:
            last_error = exc
            validation_feedback = f"Invalid JSON payload: {exc}"
            continue

        try:
            validate_llm_call_3_5(payload)
        except SchemaValidationError as exc:
            last_error = exc
            validation_feedback = str(exc)
            logger.warning(
                "corrections_preview_schema_validation_failed",
                extra={
                    "event": "corrections_preview_schema_validation_failed",
                    "attempt": attempt,
                    "cache_key": cache_key,
                    "error": str(exc),
                },
            )
            continue

        final_html = str(payload.get("final_template_html") or "")
        page_summary = str(payload.get("page_summary") or "")
        if not page_summary.strip():
            last_error = CorrectionsPreviewError("page_summary cannot be blank.")
            validation_feedback = "page_summary must be a non-empty descriptive string."
            continue

        try:
            (
                inline_tokens_observed,
                missing_inline_tokens,
                unexpected_inline_tokens,
            ) = _ensure_invariants(
                original_html=template_html_original,
                final_html=final_html,
                expected_inline_tokens=inline_expected_tokens,
            )
        except CorrectionsPreviewError as exc:
            last_error = exc
            validation_feedback = str(exc)
            logger.warning(
                "corrections_preview_invariant_failed",
                extra={
                    "event": "corrections_preview_invariant_failed",
                    "attempt": attempt,
                    "cache_key": cache_key,
                    "error": str(exc),
                },
            )
            continue

        llm_response_payload = {
            "final_template_html": final_html,
            "page_summary": page_summary,
            "inline_constants": inline_tokens_observed,
            "missing_inline_tokens": missing_inline_tokens,
            "unexpected_inline_tokens": unexpected_inline_tokens,
        }
        break

    if llm_response_payload is None:
        assert last_error is not None
        raise CorrectionsPreviewError(str(last_error)) from last_error

    final_html = llm_response_payload["final_template_html"]
    page_summary = llm_response_payload["page_summary"]
    inline_constants = list(llm_response_payload.get("inline_constants") or [])
    missing_inline_tokens = list(llm_response_payload.get("missing_inline_tokens") or [])
    unexpected_inline_tokens = list(llm_response_payload.get("unexpected_inline_tokens") or [])

    write_text_atomic(template_html_path, final_html, step="corrections_preview_final_html")
    write_text_atomic(page_summary_path, page_summary, step="corrections_preview_page_summary")

    final_template_sha = _sha256_text(final_html)
    page_summary_sha = _sha256_text(page_summary)

    if missing_inline_tokens:
        logger.warning(
            "corrections_preview_missing_inline_tokens",
            extra={
                "event": "corrections_preview_missing_inline_tokens",
                "tokens": missing_inline_tokens,
            },
        )
    if unexpected_inline_tokens:
        logger.warning(
            "corrections_preview_unexpected_inline_tokens",
            extra={
                "event": "corrections_preview_unexpected_inline_tokens",
                "tokens": unexpected_inline_tokens,
            },
        )

    summary = {
        "constants_inlined": len(inline_constants),
        "unexpected_inline_tokens": len(unexpected_inline_tokens),
        "missing_inline_tokens": len(missing_inline_tokens),
        "page_summary_chars": len(page_summary),
    }

    processed_payload = {
        "inline_constants": inline_constants,
        "expected_inline_constants": sorted(inline_expected_tokens),
        "missing_inline_constants": missing_inline_tokens,
        "unexpected_inline_constants": unexpected_inline_tokens,
        "page_summary": page_summary,
        "final_template_sha256": final_template_sha,
        "page_summary_sha256": page_summary_sha,
    }

    stage_document = {
        "cache_key": cache_key,
        "prompt_version": prompt_version,
        "model": model_name,
        "input_template_sha256": template_sha_before,
        "mapping_sha256": mapping_sha,
        "user_input_sha256": user_input_sha,
        "final_template_sha256": final_template_sha,
        "page_summary_sha256": page_summary_sha,
        "summary": summary,
        "processed": processed_payload,
        "raw_response": llm_response_payload,
        "artifacts": {
            "template_html": template_html_path.name,
            "page_summary": page_summary_path.name,
        },
    }
    write_json_atomic(stage_path, stage_document, ensure_ascii=False, indent=2, step="corrections_preview_stage")

    manifest_inputs = [
        f"stage_3_5_cache_key={cache_key}",
        f"template_pre_sha256={template_sha_before}",
        f"template_post_sha256={final_template_sha}",
        f"mapping_sha256={mapping_sha}",
        f"user_input_sha256={user_input_sha}",
    ]
    write_artifact_manifest(
        upload_dir,
        step="mapping_corrections_preview",
        files={
            "template_p1.html": template_html_path,
            "page_summary.txt": page_summary_path,
            "stage_3_5.json": stage_path,
        },
        inputs=manifest_inputs,
        correlation_id=None,
    )

    artifacts = {
        "template_html": str(template_html_path),
        "page_summary": str(page_summary_path),
        "stage": str(stage_path),
    }

    logger.info(
        "corrections_preview_complete",
        extra={
            "event": "corrections_preview_complete",
            "cache_key": cache_key,
            "constants_inlined": summary["constants_inlined"],
        },
    )

    return {
        "cache_hit": False,
        "cache_key": cache_key,
        "summary": summary,
        "processed": processed_payload,
        "artifacts": artifacts,
    }
