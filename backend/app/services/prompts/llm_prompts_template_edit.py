# mypy: ignore-errors
from __future__ import annotations

import json
from textwrap import dedent
from typing import Any, Dict, List

TEMPLATE_EDIT_PROMPT_VERSION = "template_edit_v1"


TEMPLATE_EDIT_SYSTEM_PROMPT = dedent(
    """\
    You are an expert HTML template editor working inside the NeuraReport reporting engine.

    GOAL
    - Apply the user's natural-language instructions to the existing report template HTML.
    - Make only the requested changes; do not redesign the template unless explicitly asked.

    CONSTRAINTS
    - Preserve all dynamic tokens/placeholders exactly as written (examples: {token}, {{ token }}, {row_token}, etc.).
    - Preserve repeat markers and structural markers such as <!-- BEGIN:BLOCK_REPEAT ... --> / <!-- END:BLOCK_REPEAT -->.
    - Do not remove or rename IDs, classes, data-* attributes, or comments that look like implementation markers
      unless the user explicitly asks.
    - Keep the HTML self-contained: no external CSS/JS, no <script> tags, no external URLs.

    EDITING BEHAVIOUR
    - Work in-place on the provided HTML.
    - Prefer minimal structural changes: adjust text, styles, and small layout tweaks unless the instructions clearly
      request bigger changes.
    - If an instruction conflicts with token semantics (for example, replacing a token with fixed text) then only do so
      when the user explicitly asks.
    - Maintain valid HTML.

    OUTPUT FORMAT (STRICT JSON, no markdown fences, no commentary):
    {
      "updated_html": "<string>",          // full HTML after applying the instructions
      "summary": ["change 1", "change 2"]  // short, human-readable descriptions of the main changes
    }

    - Always return BOTH keys.
    - Ensure JSON is valid UTF-8 and properly escaped.
    """
).strip()


def build_template_edit_prompt(template_html: str, instructions: str, kind: str = "pdf") -> Dict[str, Any]:
    """
    Build a chat-completions payload for editing an existing template HTML using natural-language instructions.

    Args:
        template_html: The current HTML template content
        instructions: Natural-language editing instructions
        kind: Template kind — 'pdf' or 'excel'

    Returns a dict with:
        {
          "system": <system_prompt>,
          "messages": [ ... ],
          "version": TEMPLATE_EDIT_PROMPT_VERSION,
        }
    """
    system_prompt = TEMPLATE_EDIT_SYSTEM_PROMPT
    if kind == "excel":
        from backend.app.services.prompts.llm_prompts_template_chat import _EXCEL_GUIDANCE
        system_prompt = system_prompt + "\n\n" + _EXCEL_GUIDANCE

    payload: Dict[str, Any] = {
        "template_html": template_html or "",
        "instructions": instructions or "",
    }
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    user_text = "Apply the instructions in this JSON payload:\n" + payload_json

    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": [{"type": "text", "text": system_prompt}],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": user_text}],
        },
    ]

    return {
        "system": system_prompt,
        "messages": messages,
        "version": TEMPLATE_EDIT_PROMPT_VERSION,
    }


__all__ = [
    "TEMPLATE_EDIT_PROMPT_VERSION",
    "TEMPLATE_EDIT_SYSTEM_PROMPT",
    "build_template_edit_prompt",
]

