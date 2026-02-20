"""Base interfaces for LLM adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol


class LLMRole(str, Enum):
    """Role in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class LLMMessage:
    """A message in an LLM conversation."""

    role: LLMRole
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role.value, "content": self.content}


@dataclass
class LLMResponse:
    """Response from an LLM call."""

    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    raw_response: Optional[Any] = None

    @property
    def prompt_tokens(self) -> int:
        return self.usage.get("prompt_tokens", 0)

    @property
    def completion_tokens(self) -> int:
        return self.usage.get("completion_tokens", 0)

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)


class LLMClient(Protocol):
    """Interface for LLM clients.

    Abstracts away the specific LLM provider (OpenAI, Anthropic, etc.)
    """

    def complete(
        self,
        messages: List[LLMMessage],
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send a completion request."""
        ...

    async def complete_async(
        self,
        messages: List[LLMMessage],
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send an async completion request."""
        ...


class BaseLLMClient(ABC):
    """Abstract base for LLM clients with common functionality."""

    def __init__(
        self,
        *,
        default_model: str,
        max_retries: int = 3,
        timeout_seconds: float = 60.0,
    ) -> None:
        self._default_model = default_model
        self._max_retries = max_retries
        self._timeout = timeout_seconds

    @abstractmethod
    def complete(
        self,
        messages: List[LLMMessage],
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send a completion request."""
        pass

    @abstractmethod
    async def complete_async(
        self,
        messages: List[LLMMessage],
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send an async completion request."""
        pass

    def _prepare_messages(self, messages: List[LLMMessage]) -> List[Dict[str, str]]:
        """Convert messages to dict format."""
        return [m.to_dict() for m in messages]


@dataclass
class PromptTemplate:
    """A reusable prompt template with variable substitution."""

    template: str
    system_prompt: Optional[str] = None
    variables: List[str] = field(default_factory=list)

    def render(self, **kwargs: Any) -> List[LLMMessage]:
        """Render the template with provided variables."""
        messages = []

        if self.system_prompt:
            messages.append(LLMMessage(role=LLMRole.SYSTEM, content=self.system_prompt))

        content = self.template
        for var in self.variables:
            if var in kwargs:
                content = content.replace(f"{{{{{var}}}}}", str(kwargs[var]))

        messages.append(LLMMessage(role=LLMRole.USER, content=content))
        return messages
