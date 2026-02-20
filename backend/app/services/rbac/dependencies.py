"""RBAC dependency injection for FastAPI routes."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from backend.app.services.auth import User, current_active_user
from . import check_permission

logger = logging.getLogger("neura.rbac")


class RequireRole:
    """Dependency that checks if the current user has a required role."""

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: User = Depends(current_active_user)) -> User:
        user_role = getattr(user, "role", "viewer")
        if hasattr(user_role, "value"):
            user_role = user_role.value

        if user_role not in self.allowed_roles:
            logger.warning("rbac_denied_role", extra={
                "event": "rbac_denied_role",
                "user_id": str(user.id),
                "user_role": user_role,
                "required_roles": self.allowed_roles,
            })
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' does not have access. Required: {self.allowed_roles}",
            )
        return user


class RequirePermission:
    """Dependency that uses Casbin to check route-level permissions."""

    def __init__(self, resource: Optional[str] = None):
        self.resource = resource

    async def __call__(
        self,
        request: Request,
        user: User = Depends(current_active_user),
    ) -> User:
        user_role = getattr(user, "role", "viewer")
        if hasattr(user_role, "value"):
            user_role = user_role.value

        resource = self.resource or request.url.path
        action = request.method

        if not check_permission(user_role, resource, action):
            logger.warning("rbac_denied_casbin", extra={
                "event": "rbac_denied_casbin",
                "user_id": str(user.id),
                "user_role": user_role,
                "resource": resource,
                "action": action,
            })
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {user_role} cannot {action} {resource}",
            )
        return user


# Convenience instances
require_admin = RequireRole(["admin"])
require_editor = RequireRole(["admin", "editor"])
require_viewer = RequireRole(["admin", "editor", "viewer"])
require_permission = RequirePermission()
