# mypy: ignore-errors
"""
LLM Utilities for NeuraReport.

Uses Claude Code CLI as the exclusive LLM backend.
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

logger = logging.getLogger("neura.llm")

_LOG_PATH_ENV = os.getenv("LLM_RAW_OUTPUT_PATH")
if _LOG_PATH_ENV:
    _RAW_OUTPUT_PATH = Path(_LOG_PATH_ENV).expanduser()
else:
    _RAW_OUTPUT_PATH = Path(__file__).resolve().parents[3] / "llm_raw_outputs.md"

_RAW_OUTPUT_LOCK = threading.Lock()


# =============================================================================
# JSON Extraction from LLM Responses
# =============================================================================

def extract_json_from_llm_response(
    content: str,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Extract JSON from an LLM response that may contain markdown code blocks.

    Handles common LLM output patterns:
    - Raw JSON
    - JSON wrapped in ```json ... ``` or ``` ... ``` code blocks
    - JSON embedded in explanatory text
    - Partial/truncated JSON (returns default)

    Args:
        content: Raw LLM response text
        default: Default value to return if parsing fails (default: empty dict)

    Returns:
        Parsed JSON dict, or default if parsing fails
    """
    if default is None:
        default = {}

    if not content or not content.strip():
        return default

    cleaned = content.strip()

    # Handle ```json ... ``` or ``` ... ``` code blocks
    # Match both with and without 'json' language tag
    json_block_match = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", cleaned)
    if json_block_match:
        cleaned = json_block_match.group(1).strip()
    elif cleaned.startswith("```"):
        # Fallback: manually strip opening/closing fences
        parts = cleaned.split("```", 2)
        if len(parts) >= 2:
            cleaned = parts[1].strip()
            # Remove 'json' language tag if present at start
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()

    # Try direct parse first
    try:
        result = json.loads(cleaned)
        if isinstance(result, dict):
            return result
        # If we got a list or other type, wrap it if the caller expects a dict
        return {"data": result} if not isinstance(result, dict) else result
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the content
    # Look for outermost balanced braces
    start_idx = cleaned.find("{")
    if start_idx != -1:
        depth = 0
        in_string = False
        escape_next = False

        for i, char in enumerate(cleaned[start_idx:], start_idx):
            if escape_next:
                escape_next = False
                continue
            if char == "\\":
                escape_next = True
                continue
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    json_str = cleaned[start_idx:i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        break

    # Try regex patterns as fallback
    for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
        match = re.search(pattern, cleaned)
        if match:
            try:
                result = json.loads(match.group())
                if isinstance(result, dict):
                    return result
                return {"data": result}
            except json.JSONDecodeError:
                continue

    logger.debug(f"Failed to extract JSON from LLM response: {content[:200]}...")
    return default


def extract_json_array_from_llm_response(
    content: str,
    default: Optional[list] = None,
) -> list:
    """
    Extract a JSON array from an LLM response.

    Similar to extract_json_from_llm_response but expects and returns a list.

    Args:
        content: Raw LLM response text
        default: Default value to return if parsing fails (default: empty list)

    Returns:
        Parsed JSON array, or default if parsing fails
    """
    if default is None:
        default = []

    if not content or not content.strip():
        return default

    cleaned = content.strip()

    # Handle code blocks
    json_block_match = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", cleaned)
    if json_block_match:
        cleaned = json_block_match.group(1).strip()

    # Try direct parse
    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Try to find array in content
    match = re.search(r"\[[\s\S]*\]", cleaned)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    return default


# =============================================================================
# Raw Output Logging
# =============================================================================

def _coerce_jsonable(value: Any) -> Any:
    """Best-effort conversion of LLM responses to JSON-serialisable data."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, dict):
        return {str(k): _coerce_jsonable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_coerce_jsonable(v) for v in value]

    for attr in ("model_dump", "to_dict", "dict"):
        method = getattr(value, attr, None)
        if callable(method):
            try:
                return _coerce_jsonable(method())
            except Exception:
                continue

    json_method = getattr(value, "model_dump_json", None)
    if callable(json_method):
        try:
            return _coerce_jsonable(json.loads(json_method()))
        except Exception:
            pass

    return repr(value)


def _append_raw_output(description: str, response: Any) -> None:
    """Append the raw LLM response to a Markdown log file."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"
    entry = _coerce_jsonable(response)

    try:
        with _RAW_OUTPUT_LOCK:
            _RAW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with _RAW_OUTPUT_PATH.open("a", encoding="utf-8") as handle:
                handle.write(f"## {timestamp} - {description}\n\n")
                handle.write("```json\n")
                handle.write(json.dumps(entry, indent=2))
                handle.write("\n```\n\n")
    except Exception as exc:  # pragma: no cover - logging must not break execution
        logger.debug(
            "llm_raw_output_log_failed",
            extra={"event": "llm_raw_output_log_failed"},
            exc_info=(type(exc), exc, exc.__traceback__),
        )


# Public alias for use by other modules
append_raw_llm_output = _append_raw_output


# =============================================================================
# Chat Completion Functions
# =============================================================================

class DictAsObject:
    """Wrapper that allows dict access via both dict keys and object attributes."""

    def __init__(self, data: Any):
        if isinstance(data, dict):
            for key, value in data.items():
                setattr(self, key, DictAsObject(value) if isinstance(value, (dict, list)) else value)
            self._data = data
        elif isinstance(data, list):
            self._data = [DictAsObject(item) if isinstance(item, (dict, list)) else item for item in data]
        else:
            self._data = data

    def __getitem__(self, key):
        if isinstance(self._data, dict):
            value = self._data[key]
            return DictAsObject(value) if isinstance(value, (dict, list)) else value
        elif isinstance(self._data, list):
            value = self._data[key]
            return DictAsObject(value) if isinstance(value, (dict, list)) else value
        raise TypeError(f"Cannot index {type(self._data)}")

    def __iter__(self):
        if isinstance(self._data, list):
            for item in self._data:
                yield DictAsObject(item) if isinstance(item, (dict, list)) else item
        elif isinstance(self._data, dict):
            yield from self._data
        else:
            raise TypeError(f"Cannot iterate {type(self._data)}")

    def __len__(self):
        return len(self._data)

    def get(self, key, default=None):
        if isinstance(self._data, dict):
            value = self._data.get(key, default)
            return DictAsObject(value) if isinstance(value, (dict, list)) else value
        return default

    def __repr__(self):
        return f"DictAsObject({self._data!r})"


def call_chat_completion(
    client: Any,
    *,
    model: str,
    messages: Iterable[Dict[str, Any]],
    description: str,
    timeout: float | None = None,
    **kwargs: Any,
) -> Any:
    """
    Execute a chat completion using Claude Code CLI.

    Args:
        client: LLM client instance (or None to use the global client).
        model: Model name (sonnet, opus, haiku for Claude Code CLI).
        messages: Message payload (list/iterable of dicts).
        description: Short label used for logging (e.g., 'schema_inference').
        timeout: Optional timeout (seconds).
        **kwargs: Forwarded to the client's complete() call.

    Returns:
        Response object that supports both dict and attribute access.
    """
    # Use the unified LLM client
    from backend.app.services.llm.client import get_llm_client, LLMClient

    if isinstance(client, LLMClient):
        llm_client = client
    else:
        llm_client = get_llm_client()

    # Convert messages to list if needed
    messages_list = list(messages)

    response = llm_client.complete(
        messages=messages_list,
        model=model,
        description=description,
        **kwargs,
    )

    # Wrap dict response to support both dict and attribute access
    return DictAsObject(response) if isinstance(response, dict) else response


async def call_chat_completion_async(
    client: Any,
    *,
    model: str,
    messages: Iterable[Dict[str, Any]],
    description: str,
    timeout: float | None = None,
    **kwargs: Any,
) -> Any:
    """
    Async wrapper for call_chat_completion using Claude Code CLI.
    """
    import asyncio

    return await asyncio.to_thread(
        call_chat_completion,
        client,
        model=model,
        messages=messages,
        description=description,
        timeout=timeout,
        **kwargs,
    )
