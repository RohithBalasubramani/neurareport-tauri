from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar, Union, Awaitable

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


def _maybe_await(value: Union[Awaitable[T], T]) -> Awaitable[T]:
    if hasattr(value, "__await__"):
        return value  # type: ignore[return-value]

    async def _wrap() -> T:
        return value  # type: ignore[return-value]

    return _wrap()


@dataclass(frozen=True)
class Result(Generic[T, E]):
    value: Optional[T] = None
    error: Optional[E] = None

    @property
    def is_ok(self) -> bool:
        return self.error is None

    @property
    def is_err(self) -> bool:
        return self.error is not None

    def unwrap(self) -> T:
        if self.error is not None:
            raise RuntimeError(f"Tried to unwrap Err result: {self.error}")
        return self.value  # type: ignore[return-value]

    def unwrap_err(self) -> E:
        if self.error is None:
            raise RuntimeError("Tried to unwrap_err on Ok result")
        return self.error

    def map(self, fn: Callable[[T], U]) -> "Result[U, E]":
        if self.is_err:
            return Result(error=self.error)
        return ok(fn(self.value))  # type: ignore[arg-type]

    def bind(self, fn: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        if self.is_err:
            return Result(error=self.error)
        return fn(self.value)  # type: ignore[arg-type]

    async def bind_async(self, fn: Callable[[T], Awaitable["Result[U, E]"]]) -> "Result[U, E]":
        if self.is_err:
            return Result(error=self.error)
        return await fn(self.value)  # type: ignore[arg-type]

    def map_err(self, fn: Callable[[E], U]) -> "Result[T, U]":
        if self.is_ok:
            return Result(value=self.value)
        return err(fn(self.error))  # type: ignore[arg-type]

    def unwrap_or(self, default: T) -> T:
        return self.value if self.error is None else default

    def tap(self, fn: Callable[[T], None]) -> "Result[T, E]":
        if self.is_ok:
            fn(self.value)  # type: ignore[arg-type]
        return self

    async def tap_async(self, fn: Callable[[T], Awaitable[None]]) -> "Result[T, E]":
        if self.is_ok:
            await _maybe_await(fn(self.value))  # type: ignore[arg-type]
        return self


def ok(value: T) -> Result[T, E]:
    return Result(value=value, error=None)


def err(error: E) -> Result[T, E]:
    return Result(value=None, error=error)
