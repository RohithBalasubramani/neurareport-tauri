"""Auth service package.

Re-exports from the sibling auth module for backward compatibility.
"""
from backend.app.services.auth._core import (
    User,
    UserRead,
    UserCreate,
    UserUpdate,
    UserManager,
    get_user_db,
    get_user_manager,
    bearer_transport,
    get_jwt_strategy,
    auth_backend,
    fastapi_users,
    current_active_user,
    current_optional_user,
    init_auth_db,
    Base,
)

__all__ = [
    "User",
    "UserRead",
    "UserCreate",
    "UserUpdate",
    "UserManager",
    "get_user_db",
    "get_user_manager",
    "bearer_transport",
    "get_jwt_strategy",
    "auth_backend",
    "fastapi_users",
    "current_active_user",
    "current_optional_user",
    "init_auth_db",
    "Base",
]
