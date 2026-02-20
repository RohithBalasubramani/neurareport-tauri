"""
UX Governance Level-2: Backend Enforcement

ENFORCES that:
- Every mutating request has intent headers
- Idempotency keys are required for non-idempotent operations
- Reversibility metadata is tracked for all operations
- Requests without UX context are REJECTED (not just logged)

VIOLATIONS FAIL FAST - requests without proper UX context return 400.
"""
from __future__ import annotations

import hashlib
import json
import uuid
import collections
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

import logging

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# ============================================================================
# INTENT HEADERS
# ============================================================================

class IntentHeaders:
    """Required headers for UX governance compliance."""

    # Intent identification
    INTENT_ID = "X-Intent-Id"
    INTENT_TYPE = "X-Intent-Type"
    INTENT_LABEL = "X-Intent-Label"

    # Idempotency
    IDEMPOTENCY_KEY = "Idempotency-Key"

    # Reversibility
    REVERSIBILITY = "X-Reversibility"

    # User context
    USER_SESSION = "X-User-Session"
    USER_ACTION = "X-User-Action"

    # Workflow context
    WORKFLOW_ID = "X-Workflow-Id"
    WORKFLOW_STEP = "X-Workflow-Step"


class IntentType(str, Enum):
    """Valid intent types from frontend."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    GENERATE = "generate"
    ANALYZE = "analyze"
    EXECUTE = "execute"
    NAVIGATE = "navigate"
    LOGIN = "login"
    LOGOUT = "logout"


class Reversibility(str, Enum):
    """Reversibility levels."""
    FULLY_REVERSIBLE = "fully_reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"
    SYSTEM_MANAGED = "system_managed"


# ============================================================================
# INTENT VALIDATION
# ============================================================================

class IntentContext(BaseModel):
    """Parsed intent context from request headers."""
    intent_id: str
    intent_type: IntentType
    intent_label: Optional[str] = None
    idempotency_key: Optional[str] = None
    reversibility: Optional[Reversibility] = None
    user_session: Optional[str] = None
    workflow_id: Optional[str] = None
    workflow_step: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _get_idempotency_key(request: Request) -> Optional[str]:
    return (
        request.headers.get(IntentHeaders.IDEMPOTENCY_KEY)
        or request.headers.get("X-Idempotency-Key")
    )


def _parse_reversibility(value: Optional[str]) -> Optional[Reversibility]:
    if not value:
        return None
    try:
        return Reversibility(value)
    except ValueError:
        return None


def extract_intent_context(request: Request) -> Optional[IntentContext]:
    """Extract intent context from request headers."""
    intent_id = request.headers.get(IntentHeaders.INTENT_ID)
    intent_type_str = request.headers.get(IntentHeaders.INTENT_TYPE)

    if not intent_id or not intent_type_str:
        return None

    try:
        intent_type = IntentType(intent_type_str.lower())
    except ValueError:
        return None

    return IntentContext(
        intent_id=intent_id,
        intent_type=intent_type,
        intent_label=request.headers.get(IntentHeaders.INTENT_LABEL),
        idempotency_key=_get_idempotency_key(request),
        reversibility=_parse_reversibility(request.headers.get(IntentHeaders.REVERSIBILITY)),
        user_session=request.headers.get(IntentHeaders.USER_SESSION),
        workflow_id=request.headers.get(IntentHeaders.WORKFLOW_ID),
        workflow_step=request.headers.get(IntentHeaders.WORKFLOW_STEP),
    )


# ============================================================================
# GOVERNANCE ENFORCEMENT MIDDLEWARE
# ============================================================================

# Routes that require intent headers (mutating operations)
INTENT_REQUIRED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Routes that are exempt from intent requirements (health checks, etc.)
EXEMPT_PATHS = {
    "/health",
    "/api/health",
    "/docs",
    "/redoc",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/audit/frontend-error",
    "/api/v1/audit/frontend-error",
}


class UXGovernanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ENFORCES UX governance at the API level.

    Rejects requests that:
    - Are mutating (POST/PUT/PATCH/DELETE) without intent headers
    - Are non-idempotent without idempotency keys
    - Cannot be audited due to missing context
    """

    def __init__(self, app, strict_mode: bool = True):
        super().__init__(app)
        self.strict_mode = strict_mode

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip exempt paths
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        # Skip non-mutating methods
        if request.method not in INTENT_REQUIRED_METHODS:
            return await call_next(request)

        # Extract intent context
        intent = extract_intent_context(request)

        if not intent:
            if self.strict_mode:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "UX_GOVERNANCE_VIOLATION",
                        "message": "Request missing required intent headers",
                        "required_headers": [
                            IntentHeaders.INTENT_ID,
                            IntentHeaders.INTENT_TYPE,
                        ],
                        "hint": "All mutating requests must include X-Intent-Id and X-Intent-Type headers",
                    },
                )
            else:
                # Non-strict mode: log warning but allow
                logger.warning("Request to %s missing intent headers", request.url.path)

        # Validate idempotency for non-safe operations
        if intent and request.method in {"POST", "DELETE"}:
            if not intent.idempotency_key:
                if self.strict_mode:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "UX_GOVERNANCE_VIOLATION",
                            "message": f"{request.method} requests require idempotency key",
                            "required_headers": [IntentHeaders.IDEMPOTENCY_KEY],
                            "hint": "Include X-Idempotency-Key header for request deduplication",
                        },
                    )

        # Store intent in request state for downstream use
        if intent:
            request.state.intent = intent

        # Call the next middleware/handler
        response = await call_next(request)

        # Add governance headers to response
        if intent:
            response.headers["X-Intent-Processed"] = intent.intent_id

        return response


# ============================================================================
# REVERSIBILITY TRACKING
# ============================================================================

class ReversibilityRecord(BaseModel):
    """Record of an operation's reversibility state."""
    operation_id: str
    intent_id: str
    operation_type: str
    reversibility: Reversibility
    created_at: datetime
    expires_at: Optional[datetime] = None
    reversed_at: Optional[datetime] = None
    reverse_data: Optional[Dict[str, Any]] = None
    reverse_endpoint: Optional[str] = None


# In-memory store (replace with database in production)
_REVERSIBILITY_STORE: Dict[str, ReversibilityRecord] = {}


def record_reversible_operation(
    operation_id: str,
    intent: IntentContext,
    operation_type: str,
    reverse_data: Optional[Dict[str, Any]] = None,
    reverse_endpoint: Optional[str] = None,
    ttl_hours: int = 24,
) -> ReversibilityRecord:
    """Record an operation that can be reversed."""
    record = ReversibilityRecord(
        operation_id=operation_id,
        intent_id=intent.intent_id,
        operation_type=operation_type,
        reversibility=intent.reversibility or Reversibility.SYSTEM_MANAGED,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
        reverse_data=reverse_data,
        reverse_endpoint=reverse_endpoint,
    )
    _REVERSIBILITY_STORE[operation_id] = record

    # Evict entries if store exceeds size limit
    if len(_REVERSIBILITY_STORE) > 10000:
        now = datetime.now(timezone.utc)
        expired = [k for k, v in _REVERSIBILITY_STORE.items() if v.expires_at and v.expires_at <= now]
        for k in expired:
            del _REVERSIBILITY_STORE[k]
        # If still over limit, evict oldest entries
        if len(_REVERSIBILITY_STORE) > 10000:
            sorted_keys = sorted(_REVERSIBILITY_STORE.keys(), key=lambda k: _REVERSIBILITY_STORE[k].created_at)
            excess = len(_REVERSIBILITY_STORE) - 10000
            for k in sorted_keys[:excess]:
                del _REVERSIBILITY_STORE[k]

    return record


def get_reversibility_record(operation_id: str) -> Optional[ReversibilityRecord]:
    """Get reversibility record for an operation."""
    record = _REVERSIBILITY_STORE.get(operation_id)
    if record and record.expires_at and record.expires_at < datetime.now(timezone.utc):
        del _REVERSIBILITY_STORE[operation_id]
        return None
    return record


def mark_operation_reversed(operation_id: str) -> bool:
    """Mark an operation as reversed."""
    record = _REVERSIBILITY_STORE.get(operation_id)
    if not record:
        return False
    record.reversed_at = datetime.now(timezone.utc)
    return True


def can_reverse_operation(operation_id: str) -> tuple[bool, Optional[str]]:
    """Check if an operation can be reversed."""
    record = get_reversibility_record(operation_id)

    if not record:
        return False, "Operation not found or expired"

    if record.reversed_at:
        return False, "Operation already reversed"

    if record.reversibility == Reversibility.IRREVERSIBLE:
        return False, "Operation is marked as irreversible"

    if record.expires_at and record.expires_at < datetime.now(timezone.utc):
        return False, "Reversal window has expired"

    return True, None


# ============================================================================
# DECORATORS FOR ROUTE HANDLERS
# ============================================================================

def requires_intent(*allowed_types: IntentType):
    """
    Decorator that ENFORCES intent headers on a route.

    Usage:
        @router.post("/items")
        @requires_intent(IntentType.CREATE)
        async def create_item(request: Request, ...):
            intent = request.state.intent
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                raise HTTPException(
                    status_code=500,
                    detail="Internal error: Request object not found"
                )

            intent = getattr(request.state, "intent", None)

            if not intent:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "INTENT_REQUIRED",
                        "message": "This endpoint requires intent headers",
                        "allowed_types": [t.value for t in allowed_types],
                    }
                )

            if allowed_types and intent.intent_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "INVALID_INTENT_TYPE",
                        "message": f"Intent type '{intent.intent_type.value}' not allowed",
                        "allowed_types": [t.value for t in allowed_types],
                    }
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def reversible(ttl_hours: int = 24, reverse_endpoint: Optional[str] = None):
    """
    Decorator that marks an operation as reversible and tracks it.

    Usage:
        @router.delete("/items/{item_id}")
        @reversible(ttl_hours=48, reverse_endpoint="/items/{item_id}/restore")
        async def delete_item(request: Request, item_id: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            intent = getattr(request.state, "intent", None) if request else None

            # Execute the operation
            result = await func(*args, **kwargs)

            # Record for reversibility
            if intent:
                operation_id = str(uuid.uuid4())
                record_reversible_operation(
                    operation_id=operation_id,
                    intent=intent,
                    operation_type=func.__name__,
                    reverse_data={"kwargs": kwargs},
                    reverse_endpoint=reverse_endpoint,
                    ttl_hours=ttl_hours,
                )

                # Add operation ID to response if it's a dict
                if isinstance(result, dict):
                    result["_operation_id"] = operation_id
                    result["_can_reverse"] = True
                    result["_reverse_until"] = (
                        datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
                    ).isoformat()

            return result

        return wrapper
    return decorator


# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AuditEntry(BaseModel):
    """Audit log entry for UX governance."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    intent_id: str
    intent_type: str
    user_session: Optional[str] = None
    endpoint: str
    method: str
    status_code: int
    duration_ms: int
    workflow_id: Optional[str] = None
    workflow_step: Optional[str] = None
    error: Optional[str] = None


# Audit log storage (replace with database in production)
_MAX_AUDIT_ENTRIES = 10000
_AUDIT_LOG: collections.deque[AuditEntry] = collections.deque(maxlen=_MAX_AUDIT_ENTRIES)


def audit_log(entry: AuditEntry):
    """Add an entry to the audit log."""
    _AUDIT_LOG.append(entry)


def get_audit_log(
    intent_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    limit: int = 100,
) -> List[AuditEntry]:
    """Get audit log entries."""
    entries = _AUDIT_LOG

    if intent_id:
        entries = [e for e in entries if e.intent_id == intent_id]

    if workflow_id:
        entries = [e for e in entries if e.workflow_id == workflow_id]

    return entries[-limit:]


# ============================================================================
# GOVERNANCE VALIDATION UTILITIES
# ============================================================================

def validate_governance_compliance(request: Request) -> tuple[bool, Optional[str]]:
    """
    Validate that a request is fully UX governance compliant.
    Returns (is_compliant, error_message).
    """
    # Check intent headers
    intent_id = request.headers.get(IntentHeaders.INTENT_ID)
    intent_type = request.headers.get(IntentHeaders.INTENT_TYPE)

    if not intent_id:
        return False, f"Missing required header: {IntentHeaders.INTENT_ID}"

    if not intent_type:
        return False, f"Missing required header: {IntentHeaders.INTENT_TYPE}"

    # Validate intent type
    try:
        IntentType(intent_type.lower())
    except ValueError:
        return False, f"Invalid intent type: {intent_type}"

    # Check idempotency for mutating requests
    if request.method in {"POST", "DELETE"}:
        idempotency_key = _get_idempotency_key(request)
        if not idempotency_key:
            return False, f"Missing required header for {request.method}: {IntentHeaders.IDEMPOTENCY_KEY}"

    return True, None


def generate_governance_report() -> Dict[str, Any]:
    """Generate a governance compliance report."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_operations": len(_AUDIT_LOG),
        "reversible_operations": len(_REVERSIBILITY_STORE),
        "operations_by_type": _count_by_field(_AUDIT_LOG, "intent_type"),
        "operations_by_status": _count_by_field(_AUDIT_LOG, "status_code"),
        "recent_violations": [
            e for e in _AUDIT_LOG[-100:] if e.error
        ],
    }


def _count_by_field(entries: List[AuditEntry], field: str) -> Dict[str, int]:
    """Count entries by a field value."""
    counts: Dict[str, int] = {}
    for entry in entries:
        value = str(getattr(entry, field, "unknown"))
        counts[value] = counts.get(value, 0) + 1
    return counts
