# mypy: ignore-errors
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from ..prompts.llm_prompts import (
    get_prompt_generator_assets as get_pdf_prompt_generator_assets,
)
from ..templates.TemplateVerify import get_openai_client
from ..utils import write_artifact_manifest, write_json_atomic, write_text_atomic
from ..utils.llm import call_chat_completion
from ..utils.validation import (
    validate_contract_v2,
    validate_generator_output_schemas,
    validate_generator_sql_pack,
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "sonnet"


class GeneratorAssetsError(RuntimeError):
    """Raised when generator asset creation fails."""


def _ensure_iter(values: Iterable[Any] | None) -> list[Any]:
    if not values:
        return []
    return list(values)


def _normalized_tokens(tokens: Iterable[str] | None) -> list[str]:
    cleaned: list[str] = []
    if not tokens:
        return cleaned
    seen: set[str] = set()
    for raw in tokens:
        text = str(raw or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned


def _normalize_sql_dialect(value: str | None) -> str:
    """
    Normalize dialect names so the runtime consistently receives DuckDB-friendly SQL.
    Treat legacy "sqlite" declarations as DuckDB since the DB is now backed by pandas DataFrames.
    """
    text = str(value or "").strip().lower()
    if text in ("", "sqlite", "duckdb"):
        return "duckdb"
    if text in ("postgres", "postgresql"):
        return "postgres"
    return text or "duckdb"


_SQL_PLACEHOLDER_PATTERNS = (
    r"\.\.\.",
    r"\bTBD\b",
    r"\bTODO\b",
    r"ADD_SQL_HERE",
    r"<add_sql_here>",
)


def _extract_aliases(sql: str | None) -> list[str]:
    if not sql:
        return []
    pattern = re.compile(r"\bAS\s+([A-Za-z_][\w]*)", re.IGNORECASE)
    return pattern.findall(sql)


def _sql_contains_keyword(sql: str, keyword: str) -> bool:
    return bool(re.search(rf"\b{re.escape(keyword)}\b", sql, re.IGNORECASE))


def _sql_uses_table_reference(sql: str) -> bool:
    return bool(re.search(r"[A-Za-z_][\w]*\.[A-Za-z_][\w]*", sql))


def _validate_entrypoint_sql_shape(entrypoints: Mapping[str, str]) -> list[str]:
    issues: list[str] = []
    for section in ("header", "rows", "totals"):
        sql = (entrypoints.get(section) or "").strip()
        if not sql:
            continue
        if not _sql_contains_keyword(sql, "select"):
            issues.append(f"missing_select:{section}")
        needs_from = _sql_uses_table_reference(sql)
        if needs_from and not _sql_contains_keyword(sql, "from"):
            issues.append(f"missing_from:{section}")
        for pattern in _SQL_PLACEHOLDER_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                issues.append(f"incomplete_sql:{section}")
                break
    return issues


def _derive_output_schemas(contract: Mapping[str, Any] | None) -> dict[str, list[str]]:
    """
    Build header/rows/totals token lists from the contract when the LLM response
    omits explicit output_schemas.
    """
    contract = contract or {}
    tokens_section = contract.get("tokens") if isinstance(contract, Mapping) else {}

    header_tokens = _normalized_tokens(contract.get("header_tokens") if isinstance(contract, Mapping) else None)
    row_tokens = _normalized_tokens(contract.get("row_tokens") if isinstance(contract, Mapping) else None)
    totals_tokens = _normalized_tokens(
        list((contract.get("totals") or {}).keys()) if isinstance(contract, Mapping) else None
    )

    if isinstance(tokens_section, Mapping):
        header_tokens = header_tokens or _normalized_tokens(tokens_section.get("scalars"))
        row_tokens = row_tokens or _normalized_tokens(tokens_section.get("row_tokens"))
        totals_tokens = totals_tokens or _normalized_tokens(tokens_section.get("totals"))

    return {
        "header": header_tokens,
        "rows": row_tokens,
        "totals": totals_tokens,
    }


def _validate_entrypoints_against_schema(
    entrypoints: Mapping[str, str],
    output_schemas: Mapping[str, Sequence[str]],
) -> list[str]:
    issues: list[str] = []
    for section, expected in output_schemas.items():
        expected_tokens = [str(token) for token in expected or []]
        sql = entrypoints.get(section, "") or ""
        if expected_tokens:
            aliases = _extract_aliases(sql)
            if aliases:
                alias_set = {alias.strip() for alias in aliases if alias}
                mismatch = [token for token in expected_tokens if token not in alias_set]
                if mismatch:
                    issues.append(f"schema_mismatch:{section}")
            else:
                # If we cannot infer aliases but schema expects values, record a warning
                issues.append(f"schema_ambiguous:{section}")
    return issues


def _default_entrypoints(existing: Mapping[str, str] | None) -> dict[str, str]:
    normalized = {}
    existing = existing or {}
    for name in ("header", "rows", "totals"):
        sql = existing.get(name)
        if sql:
            normalized[name] = str(sql)
        else:
            normalized[name] = "SELECT 1;"
    return normalized


def _render_sql_script(script: str | None, entrypoints: Mapping[str, str]) -> str:
    if script and script.strip():
        return script.strip() + ("\n" if not script.strip().endswith("\n") else "")
    sections = []
    for name in ("header", "rows", "totals"):
        sql = entrypoints.get(name, "").strip() or "SELECT 1;"
        section = f"-- {name.upper()} --\n{sql.strip()}"
        sections.append(section)
    return "\n\n".join(sections) + "\n"


def _json_safe(value: Any) -> Any:
    """Convert Paths and other non-serialisable types into JSON-friendly shapes."""
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, set):
        return [_json_safe(v) for v in value]
    return value


def _prepare_step4_for_prompt(step4_output: Mapping[str, Any]) -> dict[str, Any]:
    allowed_keys = (
        "contract",
        "overview_md",
        "step5_requirements",
        "assumptions",
        "warnings",
        "validation",
    )
    payload: dict[str, Any] = {}
    for key in allowed_keys:
        if key in step4_output and step4_output[key] is not None:
            payload[key] = step4_output[key]
    return _json_safe(payload)


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL | re.IGNORECASE)
_JSON_ARRAY_CLOSURE_FIXES: tuple[tuple[str, str], ...] = (
    ('\n    },\n    "row_computed"', '\n    ],\n    "row_computed"'),
    ('\n    },\n    "header_tokens"', '\n    ],\n    "header_tokens"'),
    ('\n    },\n    "row_tokens"', '\n    ],\n    "row_tokens"'),
    ('\n    },\n    "row_order"', '\n    ],\n    "row_order"'),
)


def _repair_generator_json(text: str) -> Mapping[str, Any] | None:
    """
    Attempt to repair simple LLM mistakes where arrays are closed with `}` instead of `]`.
    """
    working = text
    max_attempts = len(_JSON_ARRAY_CLOSURE_FIXES) + 1
    for _ in range(max_attempts):
        try:
            return json.loads(working)
        except json.JSONDecodeError:
            replaced = False
            for needle, replacement in _JSON_ARRAY_CLOSURE_FIXES:
                if needle in working:
                    working = working.replace(needle, replacement, 1)
                    replaced = True
                    break
            if not replaced:
                return None
    try:
        return json.loads(working)
    except json.JSONDecodeError:
        return None


def _ensure_reshape_rule_purpose(contract: Mapping[str, Any]) -> None:
    """
    Backfill reshape rule purpose strings when the LLM omits them.
    """
    reshape_rules = contract.get("reshape_rules")
    if not isinstance(reshape_rules, list):
        return
    for idx, rule in enumerate(reshape_rules):
        if not isinstance(rule, dict):
            continue
        purpose = rule.get("purpose")
        if isinstance(purpose, str) and purpose.strip():
            continue
        alias = str(rule.get("alias") or "").strip()
        strategy = str(rule.get("strategy") or "").strip()
        if alias and strategy:
            summary = f"{alias} {strategy} rule"
        elif alias:
            summary = f"{alias} reshape rule"
        elif strategy:
            summary = f"{strategy} reshape rule"
        else:
            summary = f"Reshape rule {idx + 1}"
        rule["purpose"] = summary[:120]


def _ensure_row_order(contract: Mapping[str, Any]) -> None:
    """
    Normalise row_order to a non-empty list, deriving it from order_by when omitted.
    """
    row_order_raw = contract.get("row_order")
    cleaned: list[str] = []
    if isinstance(row_order_raw, str):
        text = row_order_raw.strip()
        if text:
            cleaned = [text]
    elif isinstance(row_order_raw, list):
        cleaned = [str(item).strip() for item in row_order_raw if str(item or "").strip()]

    order_block = contract.get("order_by")
    rows_spec: Any = None
    if isinstance(order_block, Mapping):
        rows_spec = order_block.get("rows")
    elif isinstance(order_block, list):
        rows_spec = list(order_block)
        contract["order_by"] = {"rows": list(rows_spec)}
    elif isinstance(order_block, str) and order_block.strip():
        rows_spec = [order_block.strip()]
        contract["order_by"] = {"rows": list(rows_spec)}
    else:
        contract["order_by"] = {"rows": []}
    if isinstance(rows_spec, list):
        rows_order = [str(item).strip() for item in rows_spec if str(item or "").strip()]
    elif isinstance(rows_spec, str) and rows_spec.strip():
        rows_order = [rows_spec.strip()]
        contract["order_by"]["rows"] = rows_order
    else:
        rows_order = []

    contract["row_order"] = cleaned or rows_order or ["ROWID"]


def _normalize_contract_join(contract: Mapping[str, Any]) -> None:
    """
    Drop or sanitise join blocks that the LLM emits with blank keys so schema validation
    is not tripped up by placeholder values.
    """
    join = contract.get("join")
    if not isinstance(join, Mapping):
        return

    parent_table = str(join.get("parent_table") or "").strip()
    parent_key = str(join.get("parent_key") or "").strip()
    child_table = str(join.get("child_table") or "").strip()
    child_key = str(join.get("child_key") or "").strip()

    if not parent_table or not parent_key:
        if any((parent_table, parent_key, child_table, child_key)):
            logger.info(
                "generator_contract_join_dropped",
                extra={
                    "event": "generator_contract_join_dropped",
                    "parent_table": parent_table,
                    "parent_key": parent_key,
                    "child_table": child_table,
                    "child_key": child_key,
                },
            )
        contract.pop("join", None)
        return

    normalized_join: dict[str, str] = {
        "parent_table": parent_table,
        "parent_key": parent_key,
    }
    if child_table and child_key:
        normalized_join["child_table"] = child_table
        normalized_join["child_key"] = child_key

    contract["join"] = normalized_join


def _parse_generator_response(raw_text: str) -> dict[str, Any]:
    text = (raw_text or "").strip()
    if not text:
        raise GeneratorAssetsError("Generator response was empty.")
    match = _JSON_FENCE_RE.search(text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        repaired_payload = _repair_generator_json(text)
        if repaired_payload is not None:
            return repaired_payload
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = text[start : end + 1]
            try:
                return json.loads(snippet)
            except Exception:
                pass
        raise GeneratorAssetsError(f"Generator response was not valid JSON: {exc}") from exc


def _prepare_messages(
    payload: dict[str, Any],
    prompt_getter: Callable[[], dict[str, str]],
) -> list[dict[str, str]]:
    prompts = prompt_getter() or {}
    system_text = prompts.get("system") or "You generate SQL packs."
    user_template = prompts.get("user")
    user_payload = json.dumps(payload, ensure_ascii=False, indent=2)
    if user_template and "{payload}" in user_template:
        user_text = user_template.replace("{payload}", user_payload)
    else:
        user_text = f"{user_template or ''}\n{user_payload}"
    user_text = (
        f"{user_text.strip()}\n\nIMPORTANT: Output strictly valid JSON. Use double quotes for every key and string "
        f"value. Do not include trailing commas or comments."
    )
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text.strip()},
    ]


def _write_outputs(
    template_dir: Path,
    contract: Mapping[str, Any],
    entrypoints: Mapping[str, str],
    output_schemas: Mapping[str, Sequence[str]],
    params: dict[str, list[str]],
    dialect: str,
    needs_user_fix: list[str],
    invalid: bool,
    summary: Mapping[str, Any],
    key_tokens: Iterable[str] | None,
    script: str | None,
) -> dict[str, Path]:
    generator_dir = template_dir / "generator"
    generator_dir.mkdir(parents=True, exist_ok=True)
    contract_path = template_dir / "contract.json"
    write_json_atomic(contract_path, contract, ensure_ascii=False, indent=2, step="generator_contract")

    sql_path = generator_dir / "sql_pack.sql"
    script_text = _render_sql_script(script, entrypoints)
    write_text_atomic(sql_path, script_text, encoding="utf-8", step="generator_sql_pack")

    output_schemas_path = generator_dir / "output_schemas.json"
    write_json_atomic(
        output_schemas_path,
        output_schemas,
        ensure_ascii=False,
        indent=2,
        step="generator_output_schemas",
    )

    meta_payload = {
        "dialect": dialect,
        "entrypoints": entrypoints,
        "params": params,
        "needs_user_fix": needs_user_fix,
        "invalid": invalid,
        "summary": summary,
        "cached": False,
        "key_tokens": _normalized_tokens(key_tokens),
    }
    meta_path = generator_dir / "generator_assets.json"
    write_json_atomic(meta_path, meta_payload, ensure_ascii=False, indent=2, step="generator_assets_meta")

    write_artifact_manifest(
        template_dir,
        step="generator_assets_v1",
        files={
            "contract.json": contract_path,
            "sql_pack.sql": sql_path,
            "output_schemas.json": output_schemas_path,
            "generator_assets.json": meta_path,
        },
        inputs=["generator_assets_v1"],
        correlation_id=None,
    )

    return {
        "contract": contract_path,
        "sql_pack": sql_path,
        "output_schemas": output_schemas_path,
        "generator_assets": meta_path,
    }


def build_generator_assets_from_payload(
    *,
    template_dir: Path,
    step4_output: Mapping[str, Any],
    final_template_html: str,
    reference_pdf_image: Any = None,
    reference_worksheet_html: str | None = None,
    catalog_allowlist: Iterable[str] | None = None,
    params_spec: Sequence[str] | None = None,
    sample_params: Mapping[str, Any] | None = None,
    force_rebuild: bool = False,
    dialect: str | None = None,
    key_tokens: Iterable[str] | None = None,
    prompt_getter: Optional[Callable[[], dict[str, str]]] = None,
    require_contract_join: bool = True,
) -> dict[str, Any]:
    template_dir = Path(template_dir)
    template_dir.mkdir(parents=True, exist_ok=True)

    catalog_list = [str(item) for item in (catalog_allowlist or []) if str(item).strip()]
    params_list = list(params_spec or [])
    sample_params_dict = dict(sample_params or {})

    step4_prompt_payload = _prepare_step4_for_prompt(step4_output)

    request_payload = {
        "final_template_html": final_template_html,
        # For PDF-driven flows, this conveys the raster reference. For Excel flows,
        # callers may supply `reference_worksheet_html` instead (preferred).
        "reference_pdf_image": reference_pdf_image,
        "step4_output": step4_prompt_payload,
        "catalog_allowlist": catalog_list,
        "params_spec": params_list,
        "sample_params": _json_safe(sample_params_dict),
        "force_rebuild": bool(force_rebuild),
        "key_tokens": _normalized_tokens(key_tokens),
    }
    if isinstance(reference_worksheet_html, str) and reference_worksheet_html.strip():
        request_payload["reference_worksheet_html"] = reference_worksheet_html

    client = get_openai_client()
    if client is None:
        raise GeneratorAssetsError("OpenAI client is not configured.")

    prompt_factory = prompt_getter or get_pdf_prompt_generator_assets
    messages = _prepare_messages(request_payload, prompt_factory)
    try:
        raw_response = call_chat_completion(
            client,
            model=DEFAULT_MODEL,
            messages=messages,
            description="generator_assets_v1",
        )
    except Exception as exc:  # pragma: no cover - network failures bubble up
        raise GeneratorAssetsError(f"Generator LLM call failed: {exc}") from exc

    try:
        content = raw_response.choices[0].message.content or ""
        response_payload = _parse_generator_response(content)
    except GeneratorAssetsError:
        raise
    except Exception as exc:  # pragma: no cover - malformed response
        raise GeneratorAssetsError(f"Generator response was not valid JSON: {exc}") from exc

    sql_pack_raw = response_payload.get("sql_pack") or {}
    contract = response_payload.get("contract")
    if not isinstance(contract, Mapping) or not contract:
        raise GeneratorAssetsError("Generator LLM response did not include a contract payload.")
    try:
        _ensure_reshape_rule_purpose(contract)
        _ensure_row_order(contract)
        _normalize_contract_join(contract)
        validate_contract_v2(contract, require_join=require_contract_join)
    except Exception as exc:
        raise GeneratorAssetsError(f"Generator contract failed validation: {exc}") from exc

    output_schemas_payload = response_payload.get("output_schemas")
    if isinstance(output_schemas_payload, Mapping):
        output_schemas = {
            "header": _normalized_tokens(output_schemas_payload.get("header")),
            "rows": _normalized_tokens(output_schemas_payload.get("rows")),
            "totals": _normalized_tokens(output_schemas_payload.get("totals")),
        }
    else:
        output_schemas = _derive_output_schemas(contract)

    # Validate generator structures
    try:
        validate_generator_output_schemas(output_schemas)
    except Exception as exc:
        raise GeneratorAssetsError(f"Invalid output schemas: {exc}") from exc

    # Normalise entrypoints and params
    entrypoints_raw = sql_pack_raw.get("entrypoints")
    if isinstance(entrypoints_raw, Mapping) and entrypoints_raw:
        entrypoints = _default_entrypoints(entrypoints_raw)
    else:
        legacy_entrypoints = {
            key: value
            for key, value in {
                "header": sql_pack_raw.get("header"),
                "rows": sql_pack_raw.get("rows"),
                "totals": sql_pack_raw.get("totals"),
            }.items()
            if isinstance(value, str)
        }
        entrypoints = _default_entrypoints(legacy_entrypoints)

    script_text = sql_pack_raw.get("script")
    if isinstance(script_text, str) and script_text.strip():
        script_for_validation = script_text
    else:
        script_for_validation = _render_sql_script(script_text, entrypoints)

    params_section = sql_pack_raw.get("params")
    required_params: list[str] = []
    optional_params: list[str] = []
    if isinstance(params_section, Mapping):
        required_params.extend(params_section.get("required") or [])
        optional_params.extend(params_section.get("optional") or [])
    elif isinstance(params_section, Sequence):
        required_params.extend(params_section)

    base_params = _normalized_tokens(params_list)
    key_param_tokens = _normalized_tokens(key_tokens)
    for token in key_param_tokens:
        if token not in base_params:
            base_params.append(token)
    for item in base_params:
        if item not in required_params:
            required_params.append(item)
    optional_params = [p for p in optional_params if p not in required_params]
    params_normalized = {"required": required_params, "optional": optional_params}

    sql_pack_normalized = {
        "dialect": _normalize_sql_dialect(sql_pack_raw.get("dialect") or response_payload.get("dialect") or dialect),
        "script": script_for_validation,
        "entrypoints": entrypoints,
        "params": params_normalized,
    }

    try:
        validate_generator_sql_pack(sql_pack_normalized)
    except Exception as exc:
        raise GeneratorAssetsError(f"Invalid SQL pack: {exc}") from exc

    schema_issues = _validate_entrypoints_against_schema(entrypoints, output_schemas)
    shape_issues = _validate_entrypoint_sql_shape(entrypoints)
    if schema_issues:
        logger.warning(
            "generator_assets_schema_issues", extra={"event": "generator_assets_schema_issues", "issues": schema_issues}
        )
    if shape_issues:
        logger.warning(
            "generator_assets_sql_shape_issues",
            extra={"event": "generator_assets_sql_shape_issues", "issues": shape_issues},
        )

    needs_user_fix = _ensure_iter(response_payload.get("needs_user_fix")) + schema_issues + shape_issues
    invalid = bool(response_payload.get("invalid")) or bool(schema_issues) or bool(shape_issues)
    summary = response_payload.get("summary") or {}
    selected_dialect = _normalize_sql_dialect(response_payload.get("dialect") or dialect)

    artifacts = _write_outputs(
        template_dir=template_dir,
        contract=contract,
        entrypoints=entrypoints,
        output_schemas=output_schemas,
        params=params_normalized,
        dialect=selected_dialect,
        needs_user_fix=needs_user_fix,
        invalid=invalid,
        summary=summary,
        key_tokens=key_param_tokens,
        script=script_text,
    )

    result = {
        "artifacts": artifacts,
        "needs_user_fix": needs_user_fix,
        "invalid": invalid,
        "dialect": selected_dialect,
        "params": params_normalized,
        "dry_run": response_payload.get("dry_run"),
        "summary": summary,
        "cached": False,
    }
    return result


def load_generator_assets_bundle(template_dir: Path) -> dict[str, Any] | None:
    generator_dir = Path(template_dir) / "generator"
    meta_path = generator_dir / "generator_assets.json"
    if not meta_path.exists():
        return None

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    sql_path = generator_dir / "sql_pack.sql"
    output_schemas_path = generator_dir / "output_schemas.json"
    contract_path = Path(template_dir) / "contract.json"

    artifacts: dict[str, Path] = {}
    if contract_path.exists():
        artifacts["contract"] = contract_path
    if sql_path.exists():
        artifacts["sql_pack"] = sql_path
    if output_schemas_path.exists():
        artifacts["output_schemas"] = output_schemas_path
    if meta_path.exists():
        artifacts["generator_assets"] = meta_path

    bundle = {
        "artifacts": artifacts,
        "meta": meta,
        "needs_user_fix": _ensure_iter(meta.get("needs_user_fix")),
        "invalid": bool(meta.get("invalid")),
        "dialect": meta.get("dialect"),
        "params": meta.get("params") or {"required": [], "optional": []},
        "summary": meta.get("summary") or {},
        "dry_run": None,
        "cached": True,
        "key_tokens": meta.get("key_tokens") or [],
    }
    return bundle
