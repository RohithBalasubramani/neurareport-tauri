from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from copy import deepcopy
from itertools import zip_longest
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft7Validator  # type: ignore
except ImportError:  # pragma: no cover
    Draft7Validator = None  # type: ignore

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"
JSON_SCHEMA_DIR = Path(__file__).resolve().parent / "json_schemas"


class SchemaValidationError(ValueError):
    pass


_DIRECT_COLUMN_RE = re.compile(r"^\s*(?P<table>[A-Za-z_][\w]*)\s*\.\s*(?P<column>[A-Za-z_][\w]*)\s*$")


def _infer_parent_table_from_mapping(mapping: Mapping[str, Any] | None) -> str | None:
    if not isinstance(mapping, Mapping):
        return None
    for expr in mapping.values():
        if not isinstance(expr, str):
            continue
        match = _DIRECT_COLUMN_RE.match(expr.strip())
        if not match:
            continue
        table_name = match.group("table").strip(' "`[]')
        if table_name and not table_name.lower().startswith("params"):
            return table_name
    return None


def _load_schema(name: str) -> dict:
    path = SCHEMA_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


MAPPING_SCHEMA = _load_schema("mapping_pdf_labels.schema.json")
CONTRACT_SCHEMA = _load_schema("contract.schema.json")


def _coerce_join_block(data: Mapping[str, Any]) -> dict[str, Any] | None:
    if not isinstance(data, Mapping):
        return None
    join_raw = data.get("join")
    join = dict(join_raw) if isinstance(join_raw, Mapping) else {}
    parent_table = str(join.get("parent_table") or "").strip()
    parent_key = str(join.get("parent_key") or "").strip()
    if not parent_table:
        inferred = _infer_parent_table_from_mapping(data.get("mapping"))
        if inferred:
            parent_table = inferred
    if not parent_table:
        return None
    if not parent_key:
        parent_key = "__rowid__"
    child_table = str(join.get("child_table") or "").strip()
    child_key = str(join.get("child_key") or "").strip()
    join.update(
        {
            "parent_table": parent_table,
            "parent_key": parent_key,
            "child_table": child_table,
            "child_key": child_key,
        }
    )
    return join


if Draft7Validator is not None:
    _MAPPING_INLINE_V4_SCHEMA = json.loads(
        (JSON_SCHEMA_DIR / "mapping_inline_v4.schema.json").read_text(encoding="utf-8")
    )
    _MAPPING_INLINE_V4_VALIDATOR = Draft7Validator(_MAPPING_INLINE_V4_SCHEMA)
    _LLM_CALL_3_5_SCHEMA = json.loads((JSON_SCHEMA_DIR / "llm_call_3_5.schema.json").read_text(encoding="utf-8"))
    _LLM_CALL_3_5_VALIDATOR = Draft7Validator(_LLM_CALL_3_5_SCHEMA)
    _CONTRACT_V2_SCHEMA = json.loads((JSON_SCHEMA_DIR / "contract_v2.schema.json").read_text(encoding="utf-8"))
    _CONTRACT_V2_VALIDATOR = Draft7Validator(_CONTRACT_V2_SCHEMA)
    _CONTRACT_V2_OPTIONAL_JOIN_SCHEMA = deepcopy(_CONTRACT_V2_SCHEMA)
    required_fields = _CONTRACT_V2_OPTIONAL_JOIN_SCHEMA.get("required")
    if isinstance(required_fields, list) and "join" in required_fields:
        _CONTRACT_V2_OPTIONAL_JOIN_SCHEMA["required"] = [field for field in required_fields if field != "join"]
    join_schema = _CONTRACT_V2_OPTIONAL_JOIN_SCHEMA.get("properties", {}).get("join")
    if isinstance(join_schema, dict):
        join_required = join_schema.get("required")
        if isinstance(join_required, list):
            join_schema["required"] = [field for field in join_required if field in ("parent_table", "parent_key")]
    _CONTRACT_V2_OPTIONAL_JOIN_VALIDATOR = Draft7Validator(_CONTRACT_V2_OPTIONAL_JOIN_SCHEMA)
    _STEP5_REQUIREMENTS_SCHEMA = json.loads(
        (JSON_SCHEMA_DIR / "step5_requirements.schema.json").read_text(encoding="utf-8")
    )
    _STEP5_REQUIREMENTS_VALIDATOR = Draft7Validator(_STEP5_REQUIREMENTS_SCHEMA)
    _GENERATOR_SQL_PACK_SCHEMA = json.loads(
        (JSON_SCHEMA_DIR / "generator_sql_pack.schema.json").read_text(encoding="utf-8")
    )
    _GENERATOR_SQL_PACK_VALIDATOR = Draft7Validator(_GENERATOR_SQL_PACK_SCHEMA)
    _GENERATOR_OUTPUT_SCHEMAS_SCHEMA = json.loads(
        (JSON_SCHEMA_DIR / "generator_output_schemas.schema.json").read_text(encoding="utf-8")
    )
    _GENERATOR_OUTPUT_SCHEMAS_VALIDATOR = Draft7Validator(_GENERATOR_OUTPUT_SCHEMAS_SCHEMA)
    _GENERATOR_LLM_RESPONSE_SCHEMA = json.loads(
        (JSON_SCHEMA_DIR / "generator_llm_response.schema.json").read_text(encoding="utf-8")
    )
    _GENERATOR_LLM_RESPONSE_VALIDATOR = Draft7Validator(_GENERATOR_LLM_RESPONSE_SCHEMA)
else:  # pragma: no cover - optional dependency missing
    _MAPPING_INLINE_V4_SCHEMA = None
    _MAPPING_INLINE_V4_VALIDATOR = None
    _LLM_CALL_3_5_SCHEMA = None
    _LLM_CALL_3_5_VALIDATOR = None
    _CONTRACT_V2_SCHEMA = None
    _CONTRACT_V2_VALIDATOR = None
    _CONTRACT_V2_OPTIONAL_JOIN_SCHEMA = None
    _CONTRACT_V2_OPTIONAL_JOIN_VALIDATOR = None
    _STEP5_REQUIREMENTS_SCHEMA = None
    _STEP5_REQUIREMENTS_VALIDATOR = None
    _GENERATOR_SQL_PACK_SCHEMA = None
    _GENERATOR_SQL_PACK_VALIDATOR = None
    _GENERATOR_OUTPUT_SCHEMAS_SCHEMA = None
    _GENERATOR_OUTPUT_SCHEMAS_VALIDATOR = None
    _GENERATOR_LLM_RESPONSE_SCHEMA = None
    _GENERATOR_LLM_RESPONSE_VALIDATOR = None


def validate_mapping_schema(data: Any) -> None:
    if not isinstance(data, list):
        raise SchemaValidationError("mapping must be a list")
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise SchemaValidationError(f"mapping[{idx}] must be an object")
        for key in ("header", "placeholder", "mapping"):
            if key not in item or not isinstance(item[key], str) or not item[key].strip():
                raise SchemaValidationError(f"mapping[{idx}].{key} must be a non-empty string")


def _stringify_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _as_sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
        return list(value)
    return [value]


def _flatten_over_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, dict):
        flattened: list[str] = []
        for sub_key, sub_val in value.items():
            for item in _flatten_over_value(sub_val):
                entry = f"{sub_key}:{item}" if item else str(sub_key)
                entry = entry.strip()
                if entry:
                    flattened.append(entry)
        return flattened
    items: list[str] = []
    for item in _as_sequence(value):
        if isinstance(item, dict):
            items.extend(_flatten_over_value(item))
            continue
        entry = _stringify_scalar(item)
        if entry:
            items.append(entry)
    return items


def _normalize_string_list(values: Any) -> list[str]:
    items = _as_sequence(values)
    normalized: list[str] = []
    seen: set[str] = set()
    for item in items:
        if isinstance(item, str):
            text = item.strip()
        else:
            text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def _normalize_hint_value(raw_hint: Any) -> dict[str, Any]:
    if not isinstance(raw_hint, dict):
        op = _stringify_scalar(raw_hint) or "UNKNOWN"
        return {"op": op, "over": []}

    op = _stringify_scalar(raw_hint.get("op")) or "UNKNOWN"
    over_entries: list[str] = []

    over_entries.extend(_flatten_over_value(raw_hint.get("over")))

    if "over_a" in raw_hint or "over_b" in raw_hint:
        seq_a = [_stringify_scalar(item) for item in _as_sequence(raw_hint.get("over_a"))]
        seq_b = [_stringify_scalar(item) for item in _as_sequence(raw_hint.get("over_b"))]
        for a, b in zip_longest(seq_a, seq_b, fillvalue=""):
            a = a.strip()
            b = b.strip()
            if a and b:
                over_entries.append(f"{a} - {b}")
            elif a:
                over_entries.append(a)
            elif b:
                over_entries.append(f"- {b}")

    for key in ("num_ref", "den_ref", "formula"):
        val = raw_hint.get(key)
        text = _stringify_scalar(val)
        if text:
            over_entries.append(f"{key}:{text}")

    allowed_keys = {"op", "over", "over_a", "over_b", "num_ref", "den_ref", "formula"}
    for extra_key, extra_value in raw_hint.items():
        if extra_key in allowed_keys or extra_value is None:
            continue
        if isinstance(extra_value, dict):
            for sub_key, sub_value in extra_value.items():
                for item in _flatten_over_value({sub_key: sub_value}):
                    over_entries.append(f"{extra_key}.{item}")
        else:
            for item in _flatten_over_value(extra_value):
                over_entries.append(f"{extra_key}:{item}")

    cleaned: list[str] = []
    seen: set[str] = set()
    for entry in over_entries:
        normalized = entry.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(normalized)

    return {"op": op, "over": cleaned}


def normalize_mapping_inline_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload

    # LLMs sometimes return a top-level "constants" key for tokens they
    # consider static.  Merge those entries into "mapping" so the pipeline
    # handles them correctly, then drop the key before schema validation.
    constants = payload.pop("constants", None)
    if isinstance(constants, dict):
        mapping = payload.setdefault("mapping", {})
        for key, value in constants.items():
            if key not in mapping:
                mapping[str(key)] = str(value)

    meta = payload.get("meta")
    if not isinstance(meta, dict):
        return payload

    hints = meta.get("hints")
    if not isinstance(hints, dict):
        return payload

    normalized: dict[str, dict[str, Any]] = {}
    for key, value in hints.items():
        normalized[str(key)] = _normalize_hint_value(value)

    meta["hints"] = normalized
    return payload


def validate_contract_schema(data: Any) -> None:
    if not isinstance(data, dict):
        raise SchemaValidationError("contract must be an object")
    if "literals" not in data:
        data["literals"] = {}
    coerced_join = _coerce_join_block(data)
    if coerced_join is not None:
        data["join"] = coerced_join
    required = CONTRACT_SCHEMA["required"]
    for key in required:
        if key not in data:
            raise SchemaValidationError(f"contract missing key '{key}'")
    if not isinstance(data["mapping"], dict):
        raise SchemaValidationError("contract.mapping must be an object")
    if not isinstance(data["join"], dict):
        raise SchemaValidationError("contract.join must be an object")
    join = data["join"]
    for key in ("parent_table", "parent_key"):
        value = join.get(key)
        if not isinstance(value, str) or not value.strip():
            raise SchemaValidationError(f"contract.join.{key} must be a non-empty string")

    child_table_raw = join.get("child_table")
    if child_table_raw is not None and not isinstance(child_table_raw, str):
        raise SchemaValidationError("contract.join.child_table must be a string or null")
    child_key_raw = join.get("child_key")
    if child_key_raw is not None and not isinstance(child_key_raw, str):
        raise SchemaValidationError("contract.join.child_key must be a string or null")

    child_table_text = child_table_raw.strip() if isinstance(child_table_raw, str) else ""
    child_key_text = child_key_raw.strip() if isinstance(child_key_raw, str) else ""
    if child_table_text and not child_key_text:
        raise SchemaValidationError("contract.join.child_key must be a non-empty string when child_table is provided")
    for key in ("date_columns", "totals", "literals"):
        if not isinstance(data[key], dict):
            raise SchemaValidationError(f"contract.{key} must be an object")
    for key in ("header_tokens", "row_tokens", "row_order"):
        arr = data.get(key)
        if not isinstance(arr, list) or not all(isinstance(item, str) for item in arr):
            raise SchemaValidationError(f"contract.{key} must be an array of strings")


def validate_mapping_inline_v4(data: Any) -> None:
    """
    Validate LLM Call 3 output against the mapping_inline_v4 schema.
    """
    if _MAPPING_INLINE_V4_VALIDATOR is None:
        raise RuntimeError(
            "jsonschema is required to validate mapping inline payloads. Install the 'jsonschema' dependency."
        )

    data = normalize_mapping_inline_payload(data)

    errors = sorted(_MAPPING_INLINE_V4_VALIDATOR.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        err = errors[0]
        path = ".".join(str(p) for p in err.path)
        location = f" at {path}" if path else ""
        raise SchemaValidationError(f"mapping_inline_v4 validation error{location}: {err.message}")


def validate_llm_call_3_5(data: Any) -> None:
    """
    Validate LLM Call 3.5 response against the schema.
    """
    if _LLM_CALL_3_5_VALIDATOR is None:
        raise RuntimeError(
            "jsonschema is required to validate corrections preview payloads. Install the 'jsonschema' dependency."
        )

    errors = sorted(_LLM_CALL_3_5_VALIDATOR.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        err = errors[0]
        path = ".".join(str(p) for p in err.path)
        location = f" at {path}" if path else ""
        raise SchemaValidationError(f"llm_call_3_5 validation error{location}: {err.message}")


def validate_contract_v2(data: Any, *, require_join: bool = True) -> None:
    """
    Validate contract.json produced by LLM Call 4.
    """
    if _CONTRACT_V2_VALIDATOR is None:
        raise RuntimeError(
            "jsonschema is required to validate contract v2 payloads. Install the 'jsonschema' dependency."
        )

    if require_join or _CONTRACT_V2_OPTIONAL_JOIN_VALIDATOR is None:
        validator = _CONTRACT_V2_VALIDATOR
    else:
        validator = _CONTRACT_V2_OPTIONAL_JOIN_VALIDATOR

    errors = sorted(validator.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        err = errors[0]
        path = ".".join(str(p) for p in err.path)
        location = f" at {path}" if path else ""
        raise SchemaValidationError(f"contract_v2 validation error{location}: {err.message}")

    reshape_rules = data.get("reshape_rules")
    if isinstance(reshape_rules, list) and reshape_rules:
        column_rule_found = False
        for idx, rule in enumerate(reshape_rules):
            if not isinstance(rule, Mapping):
                continue
            columns = rule.get("columns")
            if columns is None:
                continue
            if not isinstance(columns, list) or not columns:
                raise SchemaValidationError(
                    f"contract.reshape_rules[{idx}].columns must be a non-empty array when provided"
                )
            for col_idx, column in enumerate(columns):
                if not isinstance(column, Mapping):
                    raise SchemaValidationError(f"contract.reshape_rules[{idx}].columns[{col_idx}] must be an object")
                alias = column.get("as")
                if not isinstance(alias, str) or not alias.strip():
                    raise SchemaValidationError(
                        f"contract.reshape_rules[{idx}].columns[{col_idx}].as must be a non-empty string"
                    )
            column_rule_found = True
        if not column_rule_found:
            raise SchemaValidationError("contract.reshape_rules must include at least one rule with column definitions")

    join = data.get("join")
    if isinstance(join, dict):
        parent_table = join.get("parent_table")
        if not isinstance(parent_table, str) or not parent_table.strip():
            raise SchemaValidationError("contract.join.parent_table must be a non-empty string")
        parent_key = join.get("parent_key")
        if not isinstance(parent_key, str) or not parent_key.strip():
            raise SchemaValidationError("contract.join.parent_key must be a non-empty string")

        child_table = join.get("child_table")
        child_key = join.get("child_key")
        child_table_text = child_table.strip() if isinstance(child_table, str) else ""
        if child_table_text and (not isinstance(child_key, str) or not child_key.strip()):
            raise SchemaValidationError(
                "contract.join.child_key must be a non-empty string when child_table is provided"
            )


def validate_step5_requirements(data: Any) -> None:
    """
    Validate step5_requirements.json produced by LLM Call 4.
    """
    if _STEP5_REQUIREMENTS_VALIDATOR is None:
        raise RuntimeError(
            "jsonschema is required to validate step5 requirements payloads. Install the 'jsonschema' dependency."
        )
    errors = sorted(_STEP5_REQUIREMENTS_VALIDATOR.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        err = errors[0]
        path = ".".join(str(p) for p in err.path)
        location = f" at {path}" if path else ""
        raise SchemaValidationError(f"step5_requirements validation error{location}: {err.message}")


def validate_generator_sql_pack(data: Any) -> None:
    """
    Validate the sql_pack section returned by LLM Call 5.
    """
    if _GENERATOR_SQL_PACK_VALIDATOR is None:
        raise RuntimeError(
            "jsonschema is required to validate generator sql pack payloads. Install the 'jsonschema' dependency."
        )
    errors = sorted(_GENERATOR_SQL_PACK_VALIDATOR.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        err = errors[0]
        path = ".".join(str(p) for p in err.path)
        location = f" at {path}" if path else ""
        raise SchemaValidationError(f"generator_sql_pack validation error{location}: {err.message}")
    dialect = str(data.get("dialect") or "").strip().lower()
    if not dialect or dialect == "sqlite":
        raise SchemaValidationError(
            "generator_sql_pack.dialect must be 'duckdb' or 'postgres' (SQLite SQL is no longer supported)"
        )
    if dialect not in {"duckdb", "postgres"}:
        raise SchemaValidationError(f"generator_sql_pack.dialect '{data.get('dialect')}' is not supported")


def validate_generator_output_schemas(data: Any) -> None:
    """
    Validate the output_schemas section returned by LLM Call 5.
    """
    if _GENERATOR_OUTPUT_SCHEMAS_VALIDATOR is None:
        raise RuntimeError(
            "jsonschema is required to validate generator output schemas payloads. Install the 'jsonschema' dependency."
        )
    errors = sorted(_GENERATOR_OUTPUT_SCHEMAS_VALIDATOR.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        err = errors[0]
        path = ".".join(str(p) for p in err.path)
        location = f" at {path}" if path else ""
        raise SchemaValidationError(f"generator_output_schemas validation error{location}: {err.message}")


def validate_generator_llm_response(data: Any) -> None:
    """
    Validate the full LLM Call 5 response payload before deeper inspection.
    """
    if _GENERATOR_LLM_RESPONSE_VALIDATOR is None:
        raise RuntimeError(
            "jsonschema is required to validate generator LLM responses. Install the 'jsonschema' dependency."
        )

    errors = sorted(_GENERATOR_LLM_RESPONSE_VALIDATOR.iter_errors(data), key=lambda err: list(err.path))
    if errors:
        err = errors[0]
        path = ".".join(str(p) for p in err.path)
        location = f" at {path}" if path else ""
        raise SchemaValidationError(f"generator_llm_response validation error{location}: {err.message}")

    if "key_tokens" in data:
        tokens = data.get("key_tokens")
        if not isinstance(tokens, list):
            raise SchemaValidationError("generator_llm_response.key_tokens must be an array of strings")
        cleaned = _normalize_string_list(tokens)
        if len(cleaned) != len(tokens):
            raise SchemaValidationError("generator_llm_response.key_tokens must contain unique, non-empty strings")
        for idx, token in enumerate(tokens):
            if not isinstance(token, str):
                raise SchemaValidationError(f"generator_llm_response.key_tokens[{idx}] must be a string")
            if token.strip() != token:
                raise SchemaValidationError(
                    f"generator_llm_response.key_tokens[{idx}] must not contain leading or trailing whitespace"
                )
