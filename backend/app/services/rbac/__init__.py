"""Casbin RBAC authorization layer."""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import casbin

logger = logging.getLogger("neura.rbac")

RBAC_DIR = Path(__file__).parent
MODEL_PATH = RBAC_DIR / "model.conf"
POLICY_PATH = RBAC_DIR / "policy.csv"


@lru_cache
def get_enforcer() -> casbin.Enforcer:
    """Create and cache the Casbin enforcer."""
    enforcer = casbin.Enforcer(str(MODEL_PATH), str(POLICY_PATH))
    logger.info("rbac_enforcer_initialized", extra={
        "event": "rbac_enforcer_initialized",
        "model": str(MODEL_PATH),
        "policy": str(POLICY_PATH),
    })
    return enforcer


def check_permission(role: str, resource: str, action: str) -> bool:
    """Check if a role has permission to perform an action on a resource."""
    enforcer = get_enforcer()
    return enforcer.enforce(role, resource, action)


def assign_role(user: str, role: str) -> bool:
    """Assign a role to a user."""
    enforcer = get_enforcer()
    added = enforcer.add_grouping_policy(user, role)
    if added:
        logger.info("rbac_role_assigned", extra={"event": "rbac_role_assigned", "user": user, "role": role})
    return added


def remove_role(user: str, role: str) -> bool:
    """Remove a role from a user."""
    enforcer = get_enforcer()
    removed = enforcer.remove_grouping_policy(user, role)
    if removed:
        logger.info("rbac_role_removed", extra={"event": "rbac_role_removed", "user": user, "role": role})
    return removed


def get_user_roles(user: str) -> list[str]:
    """Get all roles assigned to a user."""
    enforcer = get_enforcer()
    return enforcer.get_roles_for_user(user)


def list_all_roles() -> list[str]:
    """List all defined roles (from both policy and grouping rules)."""
    enforcer = get_enforcer()
    roles: set[str] = set(enforcer.get_all_roles())
    # get_all_roles() only returns targets of grouping policies;
    # also include subjects from policy rules (p lines) to capture all roles.
    for policy in enforcer.get_policy():
        if policy:
            roles.add(policy[0])
    # Include subjects from grouping rules (g lines).
    for gpolicy in enforcer.get_grouping_policy():
        if gpolicy:
            roles.add(gpolicy[0])
    # Exclude pseudo-roles that aren't real roles.
    roles.discard("anonymous")
    return sorted(roles)
