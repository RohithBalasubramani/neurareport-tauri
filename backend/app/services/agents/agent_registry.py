"""
Agent Registry: Dynamic agent registration and discovery.

Replaces hardcoded agent dicts with decorator-based registration.
Based on: Temporal workflow/activity patterns + plugin architecture.
"""
from __future__ import annotations
import importlib
import logging
import pkgutil
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger("neura.agents.registry")


@dataclass
class AgentDescriptor:
    """Metadata about a registered agent."""
    name: str
    agent_class: type
    version: str = "1.0"
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    max_concurrent: int = 5
    timeout_seconds: int = 120
    _instance: Optional[Any] = field(default=None, repr=False)

    def get_instance(self):
        if self._instance is None:
            self._instance = self.agent_class()
        return self._instance


class AgentRegistry:
    """Central registry for all agent types with auto-discovery."""

    def __init__(self):
        self._agents: Dict[str, AgentDescriptor] = {}
        self._lock = threading.RLock()

    def register(self, name: str, agent_class: type, version: str = "1.0",
                 description: str = "", capabilities: Optional[List[str]] = None,
                 max_concurrent: int = 5, timeout_seconds: int = 120) -> None:
        with self._lock:
            self._agents[name] = AgentDescriptor(
                name=name, agent_class=agent_class, version=version,
                description=description or agent_class.__doc__ or "",
                capabilities=capabilities or [], max_concurrent=max_concurrent,
                timeout_seconds=timeout_seconds,
            )
            logger.info(f"Registered agent: {name} v{version}")

    def get(self, name: str):
        with self._lock:
            descriptor = self._agents.get(name)
        return descriptor.get_instance() if descriptor else None

    def get_descriptor(self, name: str) -> Optional[AgentDescriptor]:
        with self._lock:
            return self._agents.get(name)

    def find_by_capability(self, capability: str) -> List[AgentDescriptor]:
        with self._lock:
            return [d for d in self._agents.values() if capability in d.capabilities]

    def list_agents(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {"name": d.name, "version": d.version, "description": d.description,
                 "capabilities": d.capabilities, "timeout_seconds": d.timeout_seconds}
                for d in sorted(self._agents.values(), key=lambda d: d.name)
            ]

    def auto_discover(self, package_path: str = "backend.app.services.agents") -> int:
        before = len(self._agents)
        try:
            package = importlib.import_module(package_path)
            pkg_dir = getattr(package, "__path__", None)
            if pkg_dir:
                for _, modname, _ in pkgutil.iter_modules(pkg_dir):
                    if not modname.startswith("_"):
                        try:
                            importlib.import_module(f"{package_path}.{modname}")
                        except Exception as exc:
                            logger.warning(f"Failed to import agent module {modname}: {exc}")
        except Exception as exc:
            logger.error(f"Agent auto-discovery failed: {exc}")
        return len(self._agents) - before


_registry: Optional[AgentRegistry] = None
_registry_lock = threading.Lock()


def get_agent_registry() -> AgentRegistry:
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = AgentRegistry()
    return _registry


def register_agent(name: str, *, version: str = "1.0", capabilities: Optional[List[str]] = None,
                   max_concurrent: int = 5, timeout_seconds: int = 120):
    """Decorator to register an agent class."""
    def decorator(cls):
        get_agent_registry().register(
            name=name, agent_class=cls, version=version,
            capabilities=capabilities, max_concurrent=max_concurrent,
            timeout_seconds=timeout_seconds,
        )
        return cls
    return decorator
