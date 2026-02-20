from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from ..templates.TemplateVerify import get_openai_client
from ..utils import call_chat_completion, strip_code_fences

logger = logging.getLogger("neura.template_recommender")

DEFAULT_MODEL = "sonnet"


def _summarise_catalog(catalog: Sequence[Mapping[str, Any]]) -> list[dict]:
    """
    Convert the unified catalog into a compact form suitable for the LLM.

    Only include fields that are helpful for semantic matching.
    """
    summary: list[dict] = []
    for item in catalog:
        template_id = str(item.get("id") or "").strip()
        if not template_id:
            continue
        summary.append(
            {
                "id": template_id,
                "name": item.get("name") or "",
                "kind": item.get("kind") or "",
                "domain": item.get("domain") or "",
                "tags": list(item.get("tags") or []),
                "useCases": list(item.get("useCases") or []),
                "primaryMetrics": list(item.get("primaryMetrics") or []),
                "source": item.get("source") or "",
            }
        )
    return summary


def _build_messages(
    catalog: Sequence[Mapping[str, Any]],
    requirement: str,
    hints: Mapping[str, Any] | None,
    max_results: int,
) -> list[dict]:
    catalog_json = json.dumps(_summarise_catalog(catalog), ensure_ascii=False)
    hints = hints or {}
    hints_json = json.dumps(hints, ensure_ascii=False)

    system_text = (
        "You are a template recommendation engine for an automated reporting tool. "
        "Given a catalog of report templates and a user's free-text requirement, you "
        "must select the best matching templates.\n\n"
        "Return results as STRICT JSON with this shape:\n"
        "{\n"
        '  "recommendations": [\n'
        "    {\"id\": \"<template_id>\", \"explanation\": \"<short reason>\", \"score\": 0.0-1.0},\n"
        "    ... up to the requested max_results\n"
        "  ]\n"
        "}\n\n"
        "- score must be a number between 0 and 1 where higher means better match.\n"
        "- explanation must be a short, user-facing sentence fragment (no markdown).\n"
        "- Only use template IDs that appear in the catalog.\n"
        "- Use HINTS_JSON (domains, kinds, schema_snapshot, tables, etc.) to bias the ranking when relevant."
    )

    user_text = (
        "USER_REQUIREMENT:\n"
        f"{requirement.strip()}\n\n"
        f"MAX_RESULTS: {max_results}\n"
        f"HINTS_JSON: {hints_json}\n\n"
        "TEMPLATE_CATALOG_JSON:\n"
        f"{catalog_json}\n"
    )

    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text},
    ]


def _coerce_score(value: Any) -> float:
    """Coerce a value to a score between 0.0 and 1.0."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    # Handle NaN and inf
    if score != score or score == float('inf') or score == float('-inf'):
        return 0.0
    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return score


def _extract_json_object(text: str) -> str | None:
    """
    Extract the first complete JSON object from text.
    Uses bracket counting to find matching braces.
    """
    if not text:
        return None

    # Find the first opening brace
    start = text.find('{')
    if start == -1:
        return None

    # Count braces to find matching close
    depth = 0
    in_string = False
    escape_next = False

    for i, char in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue

        if char == '\\' and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]

    return None


def _parse_recommendations(raw_text: str) -> list[dict]:
    text = strip_code_fences(raw_text or "").strip()
    if not text:
        return []

    # Try direct JSON first.
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        # Attempt to extract the first complete JSON object
        json_str = _extract_json_object(text)
        if not json_str:
            return []
        try:
            payload = json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Failed to parse template recommendation JSON")
            return []

    if not isinstance(payload, dict):
        return []
    raw_recs = payload.get("recommendations")
    if not isinstance(raw_recs, Iterable):
        return []

    # Get catalog IDs for validation (if available)
    results: list[dict] = []
    for item in raw_recs:
        if not isinstance(item, Mapping):
            continue
        template_id = str(item.get("id") or "").strip()
        if not template_id:
            continue
        explanation = str(item.get("explanation") or "").strip()
        score = _coerce_score(item.get("score"))
        results.append(
            {
                "id": template_id,
                "explanation": explanation,
                "score": score,
            }
        )
    return results


def recommend_templates_from_catalog(
    catalog: Sequence[Mapping[str, Any]],
    *,
    requirement: str,
    hints: Mapping[str, Any] | None = None,
    max_results: int = 6,
) -> List[Dict[str, Any]]:
    """
    Call the LLM to obtain a ranked list of template IDs with explanations.

    Returns a list of dicts:
        { "id": ..., "explanation": ..., "score": float }
    """
    requirement = (requirement or "").strip()
    if not requirement or not catalog:
        return []

    messages = _build_messages(catalog, requirement=requirement, hints=hints, max_results=max_results)
    client = get_openai_client()

    try:
        response = call_chat_completion(
            client,
            model=DEFAULT_MODEL,
            messages=messages,
            description="template_recommendations",
            temperature=0.2,
            max_tokens=512,
        )
    except Exception as exc:  # pragma: no cover - network / quota failures
        logger.warning(
            "template_recommend_llm_failed",
            extra={"event": "template_recommend_llm_failed", "error": str(exc)},
        )
        return []

    try:
        # openai v1-style response
        content = response.choices[0].message.content or ""
    except Exception:  # pragma: no cover - unexpected SDK shape
        logger.warning(
            "template_recommend_response_shape_unexpected",
            extra={"event": "template_recommend_response_shape_unexpected"},
        )
        return []

    recommendations = _parse_recommendations(content)
    if not recommendations:
        logger.info(
            "template_recommend_no_results",
            extra={"event": "template_recommend_no_results"},
        )
        return []

    # Preserve ordering from the LLM and cap to max_results.
    return recommendations[:max_results]
