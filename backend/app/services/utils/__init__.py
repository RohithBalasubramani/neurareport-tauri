"""
Utility helpers shared across backend services.

This package currently provides:
    - Atomic filesystem helpers (`fs`).
    - LLM call helpers with retries/backoff (`llm`).
"""

from .artifacts import compute_checksums, write_artifact_manifest
from .context import get_correlation_id, set_correlation_id

# Re-export convenience functions for tidy imports.
from backend.app.utils.fs import write_json_atomic, write_text_atomic
from .html import sanitize_html
from .llm import call_chat_completion, append_raw_llm_output
from .lock import TemplateLockError, acquire_template_lock
from .prompts import available_prompts, load_prompt
from .render import render_html_to_png
from .text import strip_code_fences
from .tokens import extract_tokens, normalize_token_braces
from .validation import (
    validate_contract_schema,
    validate_contract_v2,
    validate_generator_output_schemas,
    validate_generator_sql_pack,
    validate_llm_call_3_5,
    validate_mapping_inline_v4,
    validate_mapping_schema,
    validate_step5_requirements,
)

__all__ = [
    "write_text_atomic",
    "write_json_atomic",
    "call_chat_completion",
    "load_prompt",
    "available_prompts",
    "acquire_template_lock",
    "TemplateLockError",
    "write_artifact_manifest",
    "compute_checksums",
    "sanitize_html",
    "render_html_to_png",
    "strip_code_fences",
    "normalize_token_braces",
    "extract_tokens",
    "validate_contract_schema",
    "validate_contract_v2",
    "validate_mapping_schema",
    "validate_mapping_inline_v4",
    "validate_llm_call_3_5",
    "validate_step5_requirements",
    "validate_generator_sql_pack",
    "validate_generator_output_schemas",
    "get_correlation_id",
    "set_correlation_id",
]
