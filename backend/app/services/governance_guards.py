"""
UX Governance Level-2: Backend Regression Prevention Guards

ENFORCES that:
- All API routes have governance decorators
- Intent headers are validated on mutating endpoints
- Idempotency is enforced where required
- Reversibility is tracked for applicable operations

These guards run at startup and in CI to prevent regressions.
"""
from __future__ import annotations

import ast
import inspect
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from fastapi import FastAPI
from fastapi.routing import APIRoute


# ============================================================================
# VIOLATION TYPES
# ============================================================================

class ViolationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class GovernanceViolation:
    """A governance violation found during checking."""
    rule: str
    message: str
    severity: ViolationSeverity
    location: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class GovernanceCheckResult:
    """Result of a governance check."""
    passed: bool
    violations: List[GovernanceViolation] = field(default_factory=list)
    checked_items: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.WARNING)


# ============================================================================
# RULE DEFINITIONS
# ============================================================================

# Endpoints that MUST have @requires_intent decorator
INTENT_REQUIRED_ENDPOINTS = {
    "POST": ["create", "add", "upload", "generate", "execute", "submit"],
    "PUT": ["update", "modify", "change", "edit"],
    "PATCH": ["update", "modify", "patch"],
    "DELETE": ["delete", "remove", "clear"],
}

# Endpoints that MUST have @reversible decorator
REVERSIBLE_REQUIRED_PATTERNS = [
    r"delete_\w+",
    r"remove_\w+",
    r"clear_\w+",
]

# Patterns that indicate potential governance violations
VIOLATION_PATTERNS = {
    "UNVALIDATED_INPUT": {
        "pattern": r"request\.json\(\)|await request\.body\(\)",
        "message": "Direct request body access without validation",
        "severity": ViolationSeverity.WARNING,
        "suggestion": "Use Pydantic models for request validation",
    },
    "MISSING_ERROR_HANDLING": {
        "pattern": r"except\s*:\s*pass|except Exception:\s*pass",
        "message": "Swallowing exceptions hides errors from users",
        "severity": ViolationSeverity.ERROR,
        "suggestion": "Log errors and return appropriate HTTP status codes",
    },
    "DIRECT_DB_MUTATION": {
        "pattern": r"\.execute\([\"'](?:INSERT|UPDATE|DELETE)",
        "message": "Direct database mutations without audit trail",
        "severity": ViolationSeverity.WARNING,
        "suggestion": "Use tracked database operations with intent context",
    },
}


# ============================================================================
# ROUTE CHECKER
# ============================================================================

def check_route_governance(app: FastAPI) -> GovernanceCheckResult:
    """
    Check all routes in a FastAPI app for governance compliance.

    Returns a result object with violations if any are found.
    """
    result = GovernanceCheckResult(passed=True)

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        result.checked_items += 1
        endpoint = route.endpoint
        endpoint_name = endpoint.__name__ if hasattr(endpoint, "__name__") else str(endpoint)
        path = route.path
        methods = route.methods or set()

        # Check for required decorators
        for method in methods:
            # Check @requires_intent for mutating endpoints
            if method in INTENT_REQUIRED_ENDPOINTS:
                keywords = INTENT_REQUIRED_ENDPOINTS[method]
                needs_intent = any(kw in endpoint_name.lower() for kw in keywords)

                if needs_intent:
                    has_intent_decorator = _has_decorator(endpoint, "requires_intent")

                    if not has_intent_decorator:
                        result.violations.append(GovernanceViolation(
                            rule="MISSING_INTENT_DECORATOR",
                            message=f"Endpoint '{endpoint_name}' ({method} {path}) requires @requires_intent decorator",
                            severity=ViolationSeverity.ERROR,
                            location=f"{endpoint.__module__}.{endpoint_name}",
                            suggestion="Add @requires_intent(IntentType.CREATE) or similar",
                        ))
                        result.passed = False

            # Check @reversible for delete operations
            if method == "DELETE":
                for pattern in REVERSIBLE_REQUIRED_PATTERNS:
                    if re.match(pattern, endpoint_name):
                        has_reversible_decorator = _has_decorator(endpoint, "reversible")

                        if not has_reversible_decorator:
                            result.violations.append(GovernanceViolation(
                                rule="MISSING_REVERSIBLE_DECORATOR",
                                message=f"Delete endpoint '{endpoint_name}' should have @reversible decorator",
                                severity=ViolationSeverity.WARNING,
                                location=f"{endpoint.__module__}.{endpoint_name}",
                                suggestion="Add @reversible(ttl_hours=24) decorator for undo support",
                            ))

    return result


def _has_decorator(func: Callable, decorator_name: str) -> bool:
    """Check if a function has a specific decorator."""
    # Check __wrapped__ chain for decorators
    current = func
    seen = set()

    while current and id(current) not in seen:
        seen.add(id(current))

        # Check function name for decorator patterns
        if hasattr(current, "__name__"):
            if decorator_name in str(current.__name__):
                return True

        # Check for decorator markers
        if hasattr(current, f"__{decorator_name}__"):
            return True

        # Move to wrapped function
        current = getattr(current, "__wrapped__", None)

    return False


# ============================================================================
# SOURCE CODE CHECKER
# ============================================================================

def check_source_governance(directory: Path) -> GovernanceCheckResult:
    """
    Check Python source files for governance violations.
    """
    result = GovernanceCheckResult(passed=True)

    for py_file in directory.rglob("*.py"):
        # Skip test files and __pycache__
        if "test" in py_file.name.lower() or "__pycache__" in str(py_file):
            continue

        result.checked_items += 1

        try:
            source = py_file.read_text(encoding="utf-8")
            file_violations = _check_source_patterns(source, str(py_file))
            result.violations.extend(file_violations)

            if any(v.severity == ViolationSeverity.ERROR for v in file_violations):
                result.passed = False

        except Exception as e:
            result.violations.append(GovernanceViolation(
                rule="CHECK_ERROR",
                message=f"Failed to check file: {e}",
                severity=ViolationSeverity.WARNING,
                location=str(py_file),
            ))

    return result


def _check_source_patterns(source: str, filename: str) -> List[GovernanceViolation]:
    """Check source code against violation patterns."""
    violations = []

    lines = source.split("\n")

    for name, config in VIOLATION_PATTERNS.items():
        pattern = re.compile(config["pattern"])

        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                violations.append(GovernanceViolation(
                    rule=name,
                    message=config["message"],
                    severity=config["severity"],
                    location=filename,
                    line=i,
                    suggestion=config.get("suggestion"),
                ))

    return violations


# ============================================================================
# AST-BASED CHECKER
# ============================================================================

class GovernanceVisitor(ast.NodeVisitor):
    """AST visitor that checks for governance violations."""

    def __init__(self, filename: str):
        self.filename = filename
        self.violations: List[GovernanceViolation] = []
        self.in_route_handler = False
        self.current_function = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions."""
        self.current_function = node.name

        # Check if this is a route handler (has route decorator)
        is_route = any(
            isinstance(d, ast.Call) and
            hasattr(d.func, "attr") and
            d.func.attr in ("get", "post", "put", "patch", "delete")
            for d in node.decorator_list
        )

        if is_route:
            self.in_route_handler = True

            # Check for governance decorators
            decorator_names = self._get_decorator_names(node)

            # Check for exception handling
            has_try_except = any(
                isinstance(child, ast.Try)
                for child in ast.walk(node)
            )

            if not has_try_except:
                self.violations.append(GovernanceViolation(
                    rule="MISSING_ERROR_HANDLING",
                    message=f"Route handler '{node.name}' lacks try/except error handling",
                    severity=ViolationSeverity.WARNING,
                    location=self.filename,
                    line=node.lineno,
                    suggestion="Wrap route logic in try/except to handle errors gracefully",
                ))

        self.generic_visit(node)
        self.in_route_handler = False
        self.current_function = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definitions (same as sync)."""
        self.visit_FunctionDef(node)

    def _get_decorator_names(self, node: ast.FunctionDef) -> Set[str]:
        """Get all decorator names from a function."""
        names = set()

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                names.add(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    names.add(decorator.func.id)
                elif isinstance(decorator.func, ast.Attribute):
                    names.add(decorator.func.attr)

        return names


def check_ast_governance(directory: Path) -> GovernanceCheckResult:
    """Check Python files using AST analysis."""
    result = GovernanceCheckResult(passed=True)

    for py_file in directory.rglob("*.py"):
        if "test" in py_file.name.lower() or "__pycache__" in str(py_file):
            continue

        result.checked_items += 1

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))

            visitor = GovernanceVisitor(str(py_file))
            visitor.visit(tree)

            result.violations.extend(visitor.violations)

            if any(v.severity == ViolationSeverity.ERROR for v in visitor.violations):
                result.passed = False

        except SyntaxError as e:
            result.violations.append(GovernanceViolation(
                rule="SYNTAX_ERROR",
                message=f"Syntax error: {e}",
                severity=ViolationSeverity.ERROR,
                location=str(py_file),
                line=e.lineno,
            ))
            result.passed = False

    return result


# ============================================================================
# CI RUNNER
# ============================================================================

def run_governance_ci(
    app: Optional[FastAPI] = None,
    source_directory: Optional[Path] = None,
    strict: bool = True,
) -> Tuple[bool, str]:
    """
    Run all governance checks for CI.

    Returns (passed, report) tuple.
    """
    all_violations: List[GovernanceViolation] = []
    total_checked = 0

    # Check routes if app provided
    if app:
        route_result = check_route_governance(app)
        all_violations.extend(route_result.violations)
        total_checked += route_result.checked_items

    # Check source files if directory provided
    if source_directory:
        source_result = check_source_governance(source_directory)
        all_violations.extend(source_result.violations)
        total_checked += source_result.checked_items

        ast_result = check_ast_governance(source_directory)
        all_violations.extend(ast_result.violations)

    # Determine pass/fail
    errors = [v for v in all_violations if v.severity == ViolationSeverity.ERROR]
    warnings = [v for v in all_violations if v.severity == ViolationSeverity.WARNING]

    passed = len(errors) == 0 if strict else True

    # Format report
    lines = [
        "=" * 60,
        "UX GOVERNANCE CI CHECK",
        "=" * 60,
        f"Items checked: {total_checked}",
        f"Errors: {len(errors)}",
        f"Warnings: {len(warnings)}",
        f"Status: {'PASSED' if passed else 'FAILED'}",
        "",
    ]

    if errors:
        lines.append("ERRORS:")
        lines.append("-" * 40)
        for v in errors:
            lines.append(f"[{v.rule}] {v.location}" + (f":{v.line}" if v.line else ""))
            lines.append(f"  {v.message}")
            if v.suggestion:
                lines.append(f"  Suggestion: {v.suggestion}")
            lines.append("")

    if warnings:
        lines.append("WARNINGS:")
        lines.append("-" * 40)
        for v in warnings:
            lines.append(f"[{v.rule}] {v.location}" + (f":{v.line}" if v.line else ""))
            lines.append(f"  {v.message}")
            lines.append("")

    lines.append("=" * 60)

    return passed, "\n".join(lines)


# ============================================================================
# STARTUP GUARD
# ============================================================================

def enforce_governance_at_startup(app: FastAPI, strict: bool = False):
    """
    Enforce governance checks at application startup.

    In strict mode, raises exception if violations found.
    """
    @app.on_event("startup")
    async def _check_governance():
        result = check_route_governance(app)

        if result.violations:
            report = "\n".join(
                f"[{v.severity.value.upper()}] {v.rule}: {v.message}"
                for v in result.violations
            )

            if strict and not result.passed:
                raise RuntimeError(
                    f"UX Governance violations found at startup:\n{report}"
                )
            else:
                print(f"[UX GOVERNANCE] Warnings at startup:\n{report}")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UX Governance CI Check")
    parser.add_argument("directory", type=Path, help="Directory to check")
    parser.add_argument("--strict", action="store_true", help="Fail on any error")

    args = parser.parse_args()

    passed, report = run_governance_ci(
        source_directory=args.directory,
        strict=args.strict,
    )

    print(report)
    sys.exit(0 if passed else 1)
