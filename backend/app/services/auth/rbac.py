"""
Role-Based Access Control (RBAC) service.

Implements a permission system with role hierarchy and resource-level checks.
Based on: ivan-borovets/fastapi-clean-example authorization patterns.
"""
from __future__ import annotations
import logging
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from fastapi import Depends, HTTPException, status

from backend.app.services.auth import current_active_user

logger = logging.getLogger("neura.auth.rbac")


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


# Role hierarchy: each role can manage the roles listed
ROLE_HIERARCHY: dict[UserRole, set[UserRole]] = {
    UserRole.SUPER_ADMIN: {UserRole.ADMIN, UserRole.EDITOR, UserRole.VIEWER},
    UserRole.ADMIN: {UserRole.EDITOR, UserRole.VIEWER},
    UserRole.EDITOR: {UserRole.VIEWER},
    UserRole.VIEWER: set(),
}

# Permission definitions per role
ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.SUPER_ADMIN: {
        "users:read", "users:write", "users:delete",
        "reports:read", "reports:write", "reports:delete",
        "connections:read", "connections:write", "connections:delete",
        "templates:read", "templates:write", "templates:delete",
        "agents:read", "agents:write", "agents:delete",
        "dashboards:read", "dashboards:write", "dashboards:delete",
        "settings:read", "settings:write",
        "admin:read", "admin:write",
    },
    UserRole.ADMIN: {
        "users:read", "users:write",
        "reports:read", "reports:write", "reports:delete",
        "connections:read", "connections:write", "connections:delete",
        "templates:read", "templates:write", "templates:delete",
        "agents:read", "agents:write",
        "dashboards:read", "dashboards:write", "dashboards:delete",
        "settings:read", "settings:write",
    },
    UserRole.EDITOR: {
        "reports:read", "reports:write",
        "connections:read",
        "templates:read", "templates:write",
        "agents:read", "agents:write",
        "dashboards:read", "dashboards:write",
        "settings:read",
    },
    UserRole.VIEWER: {
        "reports:read",
        "connections:read",
        "templates:read",
        "dashboards:read",
        "settings:read",
    },
}


def has_permission(role: UserRole, permission: str) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


def can_manage_role(actor_role: UserRole, target_role: UserRole) -> bool:
    """Check if an actor can manage users with the target role."""
    return target_role in ROLE_HIERARCHY.get(actor_role, set())


def _resolve_user_role(user) -> UserRole:
    """Determine the effective role for a user object.

    If the user has ``is_superuser`` set, treat them as SUPER_ADMIN regardless
    of any explicit ``role`` attribute.  When no ``role`` attribute exists on
    the model, regular users default to VIEWER.
    """
    if getattr(user, "is_superuser", False):
        return UserRole.SUPER_ADMIN

    raw_role = getattr(user, "role", None)
    if raw_role is None:
        return UserRole.VIEWER
    if isinstance(raw_role, UserRole):
        return raw_role
    if isinstance(raw_role, str):
        try:
            return UserRole(raw_role)
        except ValueError:
            return UserRole.VIEWER
    return UserRole.VIEWER


def require_permission(permission: str):
    """FastAPI dependency that enforces a permission check."""
    async def checker(user=Depends(current_active_user)):
        user_role = _resolve_user_role(user)
        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        return user
    return checker


def require_role(minimum_role: UserRole):
    """FastAPI dependency that enforces a minimum role level."""
    role_order = [UserRole.VIEWER, UserRole.EDITOR, UserRole.ADMIN, UserRole.SUPER_ADMIN]
    min_idx = role_order.index(minimum_role) if minimum_role in role_order else 0

    async def checker(user=Depends(current_active_user)):
        user_role = _resolve_user_role(user)
        user_idx = role_order.index(user_role) if user_role in role_order else 0
        if user_idx < min_idx:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{minimum_role.value}' or higher required",
            )
        return user
    return checker
