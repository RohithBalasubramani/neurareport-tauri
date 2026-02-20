from __future__ import annotations

from typing import Dict

from ..prompts.llm_prompts import PROMPT_LIBRARY


def load_prompt(key: str, replacements: Dict[str, str] | None = None) -> str:
    """
    Load a prompt by key from the in-memory prompt library and optionally replace tokens.
    """
    if key not in PROMPT_LIBRARY:
        available = ", ".join(sorted(PROMPT_LIBRARY))
        raise KeyError(f"Prompt '{key}' not found. Available keys: {available}")

    prompt = PROMPT_LIBRARY[key]
    if replacements:
        for needle, value in replacements.items():
            prompt = prompt.replace(needle, value)
    return prompt


def available_prompts() -> Dict[str, str]:
    """
    Return a copy of the prompt library (key -> prompt text).
    """
    return dict(PROMPT_LIBRARY)
