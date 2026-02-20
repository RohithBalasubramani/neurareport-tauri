"""Tests for RBAC module (Casbin-based role access control)."""
import pytest
from backend.app.services.rbac import (
    check_permission,
    get_enforcer,
    assign_role,
    remove_role,
    get_user_roles,
    list_all_roles,
)


class TestRBACEnforcer:
    """Test the RBAC enforcer initialization and default policies."""

    def test_enforcer_initializes(self):
        enforcer = get_enforcer()
        assert enforcer is not None

    def test_list_all_roles(self):
        roles = list_all_roles()
        assert "admin" in roles
        assert "editor" in roles
        assert "viewer" in roles
        assert "agent" in roles


class TestRBACPermissions:
    """Test role-based permission checks."""

    def test_admin_has_full_access(self):
        assert check_permission("admin", "/api/v1/connections/test", "GET")
        assert check_permission("admin", "/api/v1/connections/test", "POST")
        assert check_permission("admin", "/api/v1/connections/test", "DELETE")

    def test_editor_can_read_and_write(self):
        assert check_permission("editor", "/api/v1/templates/123", "GET")
        assert check_permission("editor", "/api/v1/templates/123", "POST")

    def test_viewer_can_only_read(self):
        assert check_permission("viewer", "/api/v1/connections/test", "GET")
        assert not check_permission("viewer", "/api/v1/connections/test", "DELETE")

    def test_viewer_can_export(self):
        assert check_permission("viewer", "/api/v1/export/pdf", "POST")

    def test_agent_limited_access(self):
        assert check_permission("agent", "/api/v1/agents/research", "POST")
        assert check_permission("agent", "/api/v1/health/ready", "GET")

    def test_unknown_role_denied(self):
        assert not check_permission("unknown_role", "/api/v1/connections/test", "GET")


class TestRBACRoleAssignment:
    """Test dynamic role assignment."""

    def test_assign_and_check_role(self):
        assign_role("user_123", "editor")
        roles = get_user_roles("user_123")
        assert "editor" in roles

    def test_remove_role(self):
        assign_role("user_456", "viewer")
        remove_role("user_456", "viewer")
        roles = get_user_roles("user_456")
        assert "viewer" not in roles

    def test_user_with_role_inherits_permissions(self):
        assign_role("user_789", "admin")
        # Admin inherits editor which inherits viewer
        assert check_permission("user_789", "/api/v1/connections/test", "GET")
        assert check_permission("user_789", "/api/v1/connections/test", "DELETE")
