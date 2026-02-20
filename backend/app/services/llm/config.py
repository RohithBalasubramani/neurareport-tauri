# mypy: ignore-errors
"""
LLM Configuration Module.

NeuraReport uses Claude Code CLI as the LLM backend.
The CLI handles authentication via its own session - no API keys required.

Environment variables:
- CLAUDE_CODE_MODEL: Model to use (sonnet, opus, haiku - default: sonnet)
"""
from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("neura.llm.config")


class LLMProvider(str, Enum):
    """Supported LLM providers - Claude Code CLI only."""
    CLAUDE_CODE = "claude_code"  # Claude Code CLI (subprocess-based)


# Default model for Claude Code CLI
DEFAULT_MODELS: Dict[LLMProvider, str] = {
    LLMProvider.CLAUDE_CODE: "sonnet",  # sonnet, opus, haiku
}

# Vision-capable models
VISION_MODELS: Dict[LLMProvider, List[str]] = {
    LLMProvider.CLAUDE_CODE: ["sonnet", "opus"],  # Claude Code CLI supports vision
}

# Recommended models for document analysis tasks
DOCUMENT_ANALYSIS_MODELS: Dict[LLMProvider, str] = {
    LLMProvider.CLAUDE_CODE: "sonnet",  # Claude Code CLI - excellent for documents
}

# Recommended models for code/SQL generation
CODE_GENERATION_MODELS: Dict[LLMProvider, str] = {
    LLMProvider.CLAUDE_CODE: "sonnet",  # Claude Code CLI - excellent for code
}


@dataclass
class LLMConfig:
    """Configuration for Claude Code CLI LLM provider."""

    provider: LLMProvider = LLMProvider.CLAUDE_CODE
    model: str = "sonnet"

    # Request settings
    timeout_seconds: float = 120.0
    max_retries: int = 3
    retry_delay: float = 1.5
    retry_multiplier: float = 2.0

    # Model-specific settings
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

    # Feature flags
    supports_vision: bool = True
    supports_function_calling: bool = True
    supports_streaming: bool = True

    # Additional options
    extra_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and finalize configuration."""
        # Claude Code CLI always supports vision with sonnet and opus
        vision_models = VISION_MODELS.get(self.provider, [])
        self.supports_vision = self.model in vision_models

        logger.info(
            "llm_config_initialized",
            extra={
                "event": "llm_config_initialized",
                "provider": self.provider.value,
                "model": self.model,
                "supports_vision": self.supports_vision,
            }
        )

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create configuration from environment variables."""
        # Claude Code CLI uses model names: sonnet, opus, haiku
        model = (
            os.getenv("LLM_MODEL") or
            os.getenv("CLAUDE_CODE_MODEL") or
            "sonnet"
        )

        # Request settings
        timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
        max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
        retry_delay = float(os.getenv("LLM_RETRY_DELAY", "1.5"))
        retry_multiplier = float(os.getenv("LLM_RETRY_MULTIPLIER", "2.0"))

        # Optional settings
        temperature = os.getenv("LLM_TEMPERATURE")
        max_tokens = os.getenv("LLM_MAX_TOKENS")

        return cls(
            provider=LLMProvider.CLAUDE_CODE,
            model=model,
            timeout_seconds=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            retry_multiplier=retry_multiplier,
            temperature=float(temperature) if temperature else None,
            max_tokens=int(max_tokens) if max_tokens else None,
        )

    def get_vision_model(self) -> str:
        """Get the recommended vision model - sonnet supports vision."""
        vision_models = VISION_MODELS.get(self.provider, [])
        if self.model in vision_models:
            return self.model
        return "sonnet"  # Default to sonnet for vision

    def get_document_analysis_model(self) -> str:
        """Get the recommended model for document analysis."""
        return self.model  # All Claude models are excellent for documents

    def get_code_generation_model(self) -> str:
        """Get the recommended model for code/SQL generation."""
        return self.model  # All Claude models are excellent for code


def _check_claude_code_available() -> bool:
    """Check if Claude Code CLI is available."""
    try:
        import subprocess
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


# Global cached config
_config: Optional[LLMConfig] = None


def get_llm_config(force_reload: bool = False) -> LLMConfig:
    """Get the global LLM configuration."""
    global _config
    if _config is None or force_reload:
        _config = LLMConfig.from_env()
    return _config
