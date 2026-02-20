from __future__ import annotations

import ast
import io
import json
import re
import subprocess
import tokenize
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

EXCEPTION_ALLOWLIST_PATH = REPO_ROOT / "scripts/architecture/architecture_exceptions.json"
EXCEPTION_ID_PATTERN = re.compile(r"ARCH-EXC-\d+")

LEGACY_ALLOWED_IN_APP_PREFIXES = (
    "backend/app/api/routes/",
    "backend/api.py",
)

# Deployment snapshot; do not treat as source code for architecture enforcement.
EXCLUDED_GIT_PY_PREFIXES = (
    "prodo/",
)

BACKEND_ALLOWED_PATHS = (
    "backend/api.py",
    "backend/__init__.py",
    "backend/app/",
    "backend/engine/",
    "backend/legacy/",
    "backend/tests/",
    "backend/scripts/",
)

APP_LAYERS = {
    "api",
    "application",
    "domain",
    "infrastructure",
    "services",
    "repositories",
    "schemas",
    "utils",
}

APP_LAYER_RULES = {
    # Presentation layer: routes + request/response wiring.
    "api": {"allow": {"api", "application", "services", "schemas"}},
    # Application layer: use-cases (commands/queries) orchestrating domain + ports.
    "application": {"allow": {"application", "domain", "repositories", "infrastructure", "services", "utils", "schemas"}},
    "services": {"allow": {"services", "domain", "repositories", "utils", "schemas"}},
    "domain": {"allow": {"domain", "utils"}},
    # Infrastructure layer: adapters for DB/files/external services. Must not import api.
    "infrastructure": {"allow": {"infrastructure", "domain", "repositories", "utils", "schemas", "application"}},
    "repositories": {"allow": {"repositories", "domain", "utils"}},
    "schemas": {"allow": {"schemas", "utils"}},
    "utils": {"allow": {"utils"}},
}

APP_LAYER_PREFIXES = {layer: f"backend.app.{layer}" for layer in APP_LAYERS}
APP_LAYER_DIR_PREFIXES = tuple(f"backend/app/{layer}/" for layer in APP_LAYERS)

RULE_BACKEND_PATHS = "BACKEND-PATHS"
RULE_APP_UNKNOWN_LAYER = "APP-UNKNOWN-LAYER"
RULE_APP_UNKNOWN_IMPORT_LAYER = "APP-UNKNOWN-IMPORT-LAYER"
RULE_APP_LAYER_IMPORT = "APP-LAYER-IMPORT"
RULE_APP_API_IMPORT_SCOPE = "APP-API-IMPORT-SCOPE"
RULE_ENGINE_IMPORT_APP = "ENGINE-IMPORT-APP"
RULE_ENGINE_IMPORT_LEGACY = "ENGINE-IMPORT-LEGACY"
RULE_LEGACY_IMPORT_ENGINE = "LEGACY-IMPORT-ENGINE"
RULE_APP_IMPORT_ENGINE = "APP-IMPORT-ENGINE"
RULE_APP_IMPORT_LEGACY = "APP-IMPORT-LEGACY"


@dataclass(frozen=True)
class ExceptionEntry:
    exception_id: str
    path: str
    rule_id: str
    imports: tuple[str, ...]


@dataclass
class Violation:
    file: str
    rule_id: str
    message: str
    forbidden_import: str | None = None
    allowed_layers: tuple[str, ...] | None = None
    exception_id: str | None = None


def _git_tracked_py_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "*.py"],
        cwd=REPO_ROOT,
        text=True,
    )
    paths: list[Path] = []
    for line in output.splitlines():
        rel = line.strip()
        if not rel:
            continue
        if any(rel.startswith(prefix) for prefix in EXCLUDED_GIT_PY_PREFIXES):
            continue
        paths.append(REPO_ROOT / rel)
    return paths


def _module_parts_for_path(path: Path) -> list[str]:
    rel = path.relative_to(REPO_ROOT).as_posix()
    if rel.endswith(".py"):
        rel = rel[:-3]
    parts = rel.split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    else:
        parts = parts[:-1]
    return parts


def _resolve_relative_base(path: Path, level: int) -> str:
    if level <= 0:
        return ""
    parts = _module_parts_for_path(path)
    up = max(level - 1, 0)
    if up:
        parts = parts[:-up]
    return ".".join(parts)


def _iter_imports(tree: ast.AST, path: Path) -> list[str]:
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = _resolve_relative_base(path, node.level)
                if node.module:
                    module = f"{base}.{node.module}" if base else node.module
                    imports.append(module)
                else:
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        module = f"{base}.{alias.name}" if base else alias.name
                        imports.append(module)
            elif node.module:
                imports.append(node.module)
    return imports


def _imports_with_prefix(imports: list[str], prefix: str) -> list[str]:
    return [imp for imp in imports if imp == prefix or imp.startswith(f"{prefix}.")]


def _load_exception_allowlist() -> list[ExceptionEntry]:
    if not EXCEPTION_ALLOWLIST_PATH.exists():
        return []
    raw = json.loads(EXCEPTION_ALLOWLIST_PATH.read_text(encoding="utf-8"))
    entries: list[ExceptionEntry] = []
    seen_ids: set[str] = set()
    for entry in raw.get("exceptions", []):
        exception_id = entry.get("id")
        path = entry.get("path")
        rule_id = entry.get("rule_id")
        imports = tuple(entry.get("imports", []))
        if not exception_id or not path or not rule_id:
            raise ValueError("Invalid exception allowlist entry: id/path/rule_id required")
        if not EXCEPTION_ID_PATTERN.fullmatch(exception_id):
            raise ValueError(f"Invalid exception id: {exception_id}")
        if exception_id in seen_ids:
            raise ValueError(f"Duplicate exception id: {exception_id}")
        seen_ids.add(exception_id)
        entries.append(ExceptionEntry(exception_id=exception_id, path=path, rule_id=rule_id, imports=imports))
    return entries


def _comment_exception_ids(source: str) -> set[str]:
    ids: set[str] = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    except tokenize.TokenError:
        return ids
    for tok_type, tok_str, *_ in tokens:
        if tok_type != tokenize.COMMENT:
            continue
        for match in EXCEPTION_ID_PATTERN.findall(tok_str):
            ids.add(match)
    return ids


def _app_layer_for_path(rel: str) -> str | None:
    for layer in APP_LAYERS:
        if rel.startswith(f"backend/app/{layer}/"):
            return layer
    return None


def _app_layer_for_import(module: str) -> str | None:
    for layer, prefix in APP_LAYER_PREFIXES.items():
        if module == prefix or module.startswith(f"{prefix}."):
            return layer
    return None


def _is_allowed_backend_path(rel: str) -> bool:
    if not rel.startswith("backend/"):
        return True
    for allowed in BACKEND_ALLOWED_PATHS:
        if allowed.endswith("/"):
            if rel.startswith(allowed):
                return True
        elif rel == allowed:
            return True
    return False


def _exception_for_violation(
    violation: Violation,
    exceptions: list[ExceptionEntry],
    comment_ids: set[str],
) -> str | None:
    for entry in exceptions:
        if entry.path != violation.file:
            continue
        if entry.rule_id != violation.rule_id:
            continue
        if entry.imports and violation.forbidden_import:
            if not any(
                violation.forbidden_import == allowed
                or violation.forbidden_import.startswith(f"{allowed}.")
                for allowed in entry.imports
            ):
                continue
        if entry.exception_id not in comment_ids:
            continue
        return entry.exception_id
    return None


def _violations_for_file(
    path: Path,
    imports: list[str],
    exceptions: list[ExceptionEntry],
    comment_ids: set[str],
) -> list[Violation]:
    rel = path.relative_to(REPO_ROOT).as_posix()
    violations: list[Violation] = []

    def add_violation(
        rule_id: str,
        message: str,
        *,
        forbidden_import: str | None = None,
        allowed_layers: tuple[str, ...] | None = None,
    ) -> None:
        violation = Violation(
            file=rel,
            rule_id=rule_id,
            message=message,
            forbidden_import=forbidden_import,
            allowed_layers=allowed_layers,
        )
        exception_id = _exception_for_violation(violation, exceptions, comment_ids)
        if exception_id:
            violation.exception_id = exception_id
            return
        violations.append(violation)

    if not _is_allowed_backend_path(rel):
        add_violation(
            RULE_BACKEND_PATHS,
            "Python files under backend/ must live in app/, engine/, legacy/, tests/, scripts/ or backend/api.py",
            allowed_layers=tuple(sorted(APP_LAYERS)),
        )

    # Global rule: only backend/app/api/* (and tests) may import backend.app.api.*
    # Tests are exempt because they must import routers/middleware to test them.
    if "backend/app/api/" not in rel and not rel.startswith("backend/tests/"):
        for imp in _imports_with_prefix(imports, "backend.app.api"):
            add_violation(
                RULE_APP_API_IMPORT_SCOPE,
                "Only backend/app/api/* may import backend.app.api.*",
                forbidden_import=imp,
                allowed_layers=("backend/app/api/*",),
            )

    # Engine isolation.
    if rel.startswith("backend/engine/"):
        for imp in _imports_with_prefix(imports, "backend.app"):
            add_violation(
                RULE_ENGINE_IMPORT_APP,
                "backend/engine/* must not import backend.app.*",
                forbidden_import=imp,
                allowed_layers=("backend/engine/* (no backend.app imports)",),
            )
        for imp in _imports_with_prefix(imports, "backend.legacy"):
            add_violation(
                RULE_ENGINE_IMPORT_LEGACY,
                "backend/engine/* must not import backend.legacy.*",
                forbidden_import=imp,
                allowed_layers=("backend/engine/* (no backend.legacy imports)",),
            )

    # Legacy isolation (allowed to depend on backend.app).
    if rel.startswith("backend/legacy/"):
        for imp in _imports_with_prefix(imports, "backend.engine"):
            add_violation(
                RULE_LEGACY_IMPORT_ENGINE,
                "backend/legacy/* must not import backend.engine.*",
                forbidden_import=imp,
                allowed_layers=("backend/legacy/* (no backend.engine imports)",),
            )

    # App isolation (legacy only in compatibility entrypoints).
    if rel.startswith("backend/app/"):
        # Allow backend.engine usage from application/services only (domain logic).
        # Presentation/repositories/schemas/utils must not reach into engine directly.
        allow_engine = rel.startswith(("backend/app/application/", "backend/app/services/"))
        if not allow_engine:
            for imp in _imports_with_prefix(imports, "backend.engine"):
                add_violation(
                    RULE_APP_IMPORT_ENGINE,
                    "backend/app/* may only import backend.engine.* from application/ or services/",
                    forbidden_import=imp,
                    allowed_layers=("backend/app/application/*", "backend/app/services/*"),
                )
        for imp in _imports_with_prefix(imports, "backend.legacy"):
            if not rel.startswith(LEGACY_ALLOWED_IN_APP_PREFIXES):
                add_violation(
                    RULE_APP_IMPORT_LEGACY,
                    "backend/app/* may only import backend.legacy.* from api routes / backend.api.py",
                    forbidden_import=imp,
                    allowed_layers=("backend/app/api/routes/*", "backend/api.py"),
                )

    # backend/app sub-layer placement rule.
    if rel.startswith("backend/app/") and rel.endswith(".py"):
        if rel == "backend/app/__init__.py":
            pass
        elif not rel.startswith(APP_LAYER_DIR_PREFIXES):
            add_violation(
                RULE_APP_UNKNOWN_LAYER,
                "backend/app/* code must live under api/, domain/, services/, repositories/, schemas/, utils/",
                allowed_layers=tuple(sorted(APP_LAYERS)),
            )

    # backend/app sub-layer import rules.
    app_layer = _app_layer_for_path(rel)
    if app_layer:
        allowed_layers = APP_LAYER_RULES[app_layer]["allow"]
        for imp in imports:
            if not imp.startswith("backend.app."):
                continue
            target_layer = _app_layer_for_import(imp)
            if target_layer is None:
                add_violation(
                    RULE_APP_UNKNOWN_IMPORT_LAYER,
                    "backend/app imports must target api/domain/services/repositories/schemas/utils only",
                    forbidden_import=imp,
                    allowed_layers=tuple(sorted(APP_LAYERS)),
                )
                continue
            if target_layer not in allowed_layers:
                add_violation(
                    RULE_APP_LAYER_IMPORT,
                    f"backend/app/{app_layer} may only import {', '.join(sorted(allowed_layers))}",
                    forbidden_import=imp,
                    allowed_layers=tuple(sorted(allowed_layers)),
                )

    return violations


def _format_violation(violation: Violation) -> str:
    allowed = "n/a"
    if violation.allowed_layers:
        allowed = ", ".join(violation.allowed_layers)
    lines = [
        f"- {violation.file}",
        f"  rule: {violation.rule_id}",
        f"  message: {violation.message}",
        f"  forbidden: {violation.forbidden_import or 'n/a'}",
        f"  allowed: {allowed}",
    ]
    if violation.exception_id:
        lines.append(f"  exception: {violation.exception_id}")
    return "\n".join(lines)


def main() -> int:
    files = _git_tracked_py_files()
    try:
        exceptions = _load_exception_allowlist()
    except ValueError as exc:
        print(f"Architecture exception allowlist error: {exc}")
        return 1

    all_violations: list[Violation] = []

    for path in files:
        try:
            source = path.read_text(encoding="utf-8-sig")
        except OSError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            all_violations.append(
                Violation(
                    file=path.relative_to(REPO_ROOT).as_posix(),
                    rule_id="SYNTAX-ERROR",
                    message=f"invalid syntax ({exc})",
                )
            )
            continue

        imports = _iter_imports(tree, path)
        comment_ids = _comment_exception_ids(source)
        all_violations.extend(_violations_for_file(path, imports, exceptions, comment_ids))

    if all_violations:
        print("Architecture violations detected:")
        for violation in all_violations:
            print(_format_violation(violation))
        return 1

    print("Architecture checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
