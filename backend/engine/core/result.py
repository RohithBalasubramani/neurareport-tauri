"""Result type for explicit error handling without exceptions.

Inspired by Rust's Result<T, E> and functional programming patterns.
Use this for operations that can fail in expected ways.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Callable,
    Generic,
    TypeVar,
    Union,
    overload,
)

from .errors import NeuraError

T = TypeVar("T")
E = TypeVar("E", bound=NeuraError)
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Success variant of Result."""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value

    def unwrap_or_else(self, f: Callable[[NeuraError], T]) -> T:
        return self.value

    def map(self, f: Callable[[T], U]) -> Result[U, NeuraError]:
        return Ok(f(self.value))

    def map_err(self, f: Callable[[NeuraError], NeuraError]) -> Result[T, NeuraError]:
        return self

    def and_then(self, f: Callable[[T], Result[U, NeuraError]]) -> Result[U, NeuraError]:
        return f(self.value)

    def or_else(self, f: Callable[[NeuraError], Result[T, NeuraError]]) -> Result[T, NeuraError]:
        return self


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Error variant of Result."""

    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise self.error

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, f: Callable[[E], T]) -> T:
        return f(self.error)

    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        return self

    def map_err(self, f: Callable[[E], NeuraError]) -> Result[T, NeuraError]:
        return Err(f(self.error))

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return self

    def or_else(self, f: Callable[[E], Result[T, E]]) -> Result[T, E]:
        return f(self.error)


Result = Union[Ok[T], Err[E]]


def result_from_exception(f: Callable[[], T]) -> Result[T, NeuraError]:
    """Execute a function and wrap its result in a Result type."""
    try:
        return Ok(f())
    except NeuraError as e:
        return Err(e)
    except Exception as e:
        from .errors import NeuraError as BaseError
        return Err(BaseError(code="unexpected_error", message=str(e), cause=e))


def collect_results(results: list[Result[T, E]]) -> Result[list[T], E]:
    """Collect a list of Results into a Result of list."""
    values = []
    for r in results:
        if r.is_err():
            return r
        values.append(r.unwrap())
    return Ok(values)
