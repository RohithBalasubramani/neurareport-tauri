from __future__ import annotations

from typing import Callable, Dict, Generic, Optional, TypeVar

S = TypeVar("S")


class StrategyRegistry(Generic[S]):
    def __init__(self, *, default_factory: Optional[Callable[[], S]] = None) -> None:
        self._registry: Dict[str, S] = {}
        self._default_factory = default_factory

    def register(self, name: str, strategy: S) -> None:
        self._registry[name] = strategy

    def get(self, name: str) -> Optional[S]:
        return self._registry.get(name)

    def resolve(self, name: str) -> S:
        if name in self._registry:
            return self._registry[name]
        if self._default_factory:
            return self._default_factory()
        raise KeyError(f"No strategy registered for '{name}'")
