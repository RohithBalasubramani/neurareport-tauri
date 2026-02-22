# mypy: ignore-errors
"""
LLM Provider Implementation - Claude Code CLI.

NeuraReport uses Claude Code CLI as the exclusive LLM backend.
The CLI handles authentication via its own session - no API keys needed.
"""
from __future__ import annotations

import base64
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from .config import LLMConfig, LLMProvider
from backend.app.utils.errors import AppError

logger = logging.getLogger("neura.llm.providers")

# Patterns that may appear in exception messages containing secrets
import re as _re

_SECRET_PATTERNS = _re.compile(
    r"(sk-[A-Za-z0-9]{8,}|Bearer\s+\S{8,}|api[_-]?key[=:]\s*\S+)",
    _re.IGNORECASE,
)


def _sanitize_error(exc: Exception) -> str:
    """Return error string with possible API keys/tokens redacted."""
    msg = str(exc)
    return _SECRET_PATTERNS.sub("[REDACTED]", msg)


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client: Any = None

    @abstractmethod
    def get_client(self) -> Any:
        """Get or create the provider client."""
        pass

    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a chat completion request."""
        pass

    @abstractmethod
    def chat_completion_stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[Dict[str, Any]]:
        """Execute a streaming chat completion request."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is available."""
        pass

    def supports_vision(self, model: Optional[str] = None) -> bool:
        """Check if the model supports vision inputs."""
        return self.config.supports_vision

    def prepare_vision_message(
        self,
        text: str,
        images: List[Union[str, bytes, Path]],
        detail: str = "auto",
    ) -> Dict[str, Any]:
        """Prepare a message with vision content."""
        content: List[Dict[str, Any]] = [{"type": "text", "text": text}]

        for image in images:
            if isinstance(image, Path):
                image_data = base64.b64encode(image.read_bytes()).decode("utf-8")
                media_type = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"
                image_url = f"data:{media_type};base64,{image_data}"
            elif isinstance(image, bytes):
                image_data = base64.b64encode(image).decode("utf-8")
                image_url = f"data:image/png;base64,{image_data}"
            else:
                # Assume it's already a URL or base64 string
                if image.startswith("data:") or image.startswith("http"):
                    image_url = image
                else:
                    image_url = f"data:image/png;base64,{image}"

            content.append({
                "type": "image_url",
                "image_url": {"url": image_url, "detail": detail}
            })

        return {"role": "user", "content": content}


class ClaudeCodeCLIProvider(BaseProvider):
    """
    Claude Code CLI provider.

    Uses the `claude` CLI tool as a subprocess to get LLM completions.
    This is the exclusive LLM backend for NeuraReport.

    Model names: sonnet (default), opus, haiku
    """

    def __init__(self, config: "LLMConfig"):
        super().__init__(config)
        self._available: Optional[bool] = None
        self._claude_bin: str = "claude"

    def get_client(self) -> Any:
        """Check CLI availability on first use."""
        if self._available is None:
            self._available = self._check_cli_available()
        if not self._available:
            raise AppError(
                code="llm_unavailable",
                message="AI features require Claude Code CLI which is not installed on this machine.",
                status_code=503,
                detail="Install Claude Code CLI from https://docs.anthropic.com/claude-code to enable AI-powered features.",
            )
        return True

    def _check_cli_available(self) -> bool:
        """Check if claude CLI is available, searching common locations."""
        import shutil
        import subprocess

        # Check PATH first, then common install locations
        claude_bin = shutil.which("claude")
        if not claude_bin:
            from pathlib import Path
            common_paths = [
                Path.home() / ".local" / "bin" / "claude",
                Path("/usr/local/bin/claude"),
                Path.home() / ".npm-global" / "bin" / "claude",
                Path.home() / ".nvm" / "current" / "bin" / "claude",
            ]
            for p in common_paths:
                if p.is_file():
                    claude_bin = str(p)
                    break
        if not claude_bin:
            return False
        self._claude_bin = claude_bin
        try:
            result = subprocess.run(
                [claude_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _extract_images_from_messages(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract base64 images from messages and save to temp files."""
        import tempfile
        image_files = []

        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        # Handle image_url format
                        if part.get("type") == "image_url":
                            image_url = part.get("image_url", {})
                            url = image_url.get("url", "") if isinstance(image_url, dict) else ""
                            if url.startswith("data:image/"):
                                # Extract base64 data
                                try:
                                    # Format: data:image/png;base64,<data>
                                    header, b64_data = url.split(",", 1)
                                    ext = ".png" if "png" in header else ".jpg"
                                    img_bytes = base64.b64decode(b64_data)

                                    # Save to temp file
                                    with tempfile.NamedTemporaryFile(
                                        mode='wb', suffix=ext, delete=False
                                    ) as f:
                                        f.write(img_bytes)
                                        image_files.append(f.name)
                                except Exception as e:
                                    logger.warning(f"Failed to extract image: {e}")
                        # Handle image format (type: image)
                        elif part.get("type") == "image":
                            source = part.get("source", {})
                            if source.get("type") == "base64":
                                try:
                                    b64_data = source.get("data", "")
                                    media_type = source.get("media_type", "image/png")
                                    ext = ".png" if "png" in media_type else ".jpg"
                                    img_bytes = base64.b64decode(b64_data)

                                    with tempfile.NamedTemporaryFile(
                                        mode='wb', suffix=ext, delete=False
                                    ) as f:
                                        f.write(img_bytes)
                                        image_files.append(f.name)
                                except Exception as e:
                                    logger.warning(f"Failed to extract image: {e}")

        return image_files

    def _build_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """Convert message format to a single prompt string."""
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Handle multimodal content - extract text parts
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                content = "\n".join(text_parts)

            if role == "system":
                parts.append(f"<system>\n{content}\n</system>")
            elif role == "assistant":
                parts.append(f"<assistant>\n{content}\n</assistant>")
            else:  # user
                parts.append(content)

        return "\n\n".join(parts)

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a chat completion via Claude Code CLI."""
        import subprocess
        import tempfile

        self.get_client()  # Verify CLI is available
        model = model or self.config.model or "sonnet"

        # Extract images from messages and save to temp files
        image_files = self._extract_images_from_messages(messages)

        # Build the prompt
        prompt = self._build_prompt(messages)

        # Build CLI command
        cmd = [self._claude_bin, "-p"]  # -p = print mode (no interactive UI)

        # Add model flag
        if model in ("opus", "sonnet", "haiku"):
            cmd.extend(["--model", model])

        # Allow Read tool for image access with auto-accept permissions
        if image_files:
            cmd.extend(["--allowedTools", "Read", "--permission-mode", "acceptEdits"])

        # Add image file paths to the prompt as instructions to read them
        if image_files:
            image_instructions = "\n\nIMPORTANT: The following image files have been provided. Please read them using the Read tool:\n"
            for i, img_path in enumerate(image_files, 1):
                # Convert to forward slashes for consistency
                normalized_path = img_path.replace("\\", "/")
                image_instructions += f"- Image {i}: {normalized_path}\n"
            image_instructions += "\nPlease analyze the image(s) above to complete the requested task.\n"
            prompt = image_instructions + prompt

        logger.info(
            "claude_code_cli_call",
            extra={
                "event": "claude_code_cli_call",
                "model": model,
                "prompt_length": len(prompt),
                "image_count": len(image_files),
            }
        )

        start_time = time.time()
        try:
            # Use a temp file for the prompt to handle large inputs
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                prompt_file = f.name

            # Run claude CLI with prompt from stdin
            # Explicitly unset CLAUDECODE to avoid conflicts when running nested CLI calls
            import os as _env_os
            env = _env_os.environ.copy()
            env.pop('CLAUDECODE', None)

            with open(prompt_file, 'r', encoding='utf-8') as pf:
                result = subprocess.run(
                    cmd,
                    stdin=pf,
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds,
                    env=env,
                )

            # Clean up temp files
            import os as _os
            _os.unlink(prompt_file)
            for img_path in image_files:
                try:
                    _os.unlink(img_path)
                except Exception:
                    pass

            if result.returncode != 0:
                stderr_msg = (result.stderr or "").strip()
                stdout_msg = (result.stdout or "").strip()
                # Claude CLI often writes errors to stdout, not stderr
                error_msg = stderr_msg or stdout_msg or f"Claude CLI exited with code {result.returncode}"
                # Truncate to avoid enormous log entries
                if len(error_msg) > 500:
                    error_msg = error_msg[:500] + "..."
                logger.error(
                    "claude_code_cli_error",
                    extra={"event": "claude_code_cli_error", "error": error_msg, "returncode": result.returncode}
                )
                raise AppError(
                    code="llm_call_failed",
                    message="AI request failed. Claude Code CLI returned an error.",
                    status_code=502,
                    detail=error_msg,
                )

            content = result.stdout.strip()
            elapsed = time.time() - start_time

            logger.info(
                "claude_code_cli_success",
                extra={
                    "event": "claude_code_cli_success",
                    "model": model,
                    "elapsed_seconds": round(elapsed, 2),
                    "output_length": len(content),
                }
            )

            # Estimate tokens (rough approximation)
            input_tokens = len(prompt) // 4
            output_tokens = len(content) // 4

            return {
                "id": f"claude-cli-{int(time.time())}",
                "model": f"claude-{model}",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                    "finish_reason": "stop",
                }],
                "usage": {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                }
            }

        except subprocess.TimeoutExpired:
            raise AppError(
                code="llm_timeout",
                message=f"AI request timed out after {self.config.timeout_seconds}s. Try a simpler query.",
                status_code=504,
            )
        except AppError:
            raise  # Already structured — don't wrap again
        except Exception as e:
            logger.error(
                "claude_code_cli_failed",
                extra={"event": "claude_code_cli_failed", "error": _sanitize_error(e)}
            )
            raise AppError(
                code="llm_error",
                message="AI request failed unexpectedly.",
                status_code=502,
                detail=_sanitize_error(e),
            )

    def chat_completion_stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[Dict[str, Any]]:
        """Streaming is not natively supported - yield full response as single chunk."""
        response = self.chat_completion(messages, model, **kwargs)
        content = response["choices"][0]["message"]["content"]

        # Yield the full response as a single chunk
        yield {
            "id": response["id"],
            "model": response["model"],
            "choices": [{
                "index": 0,
                "delta": {"content": content},
                "finish_reason": "stop",
            }]
        }

    def list_models(self) -> List[str]:
        """List available models for Claude Code CLI."""
        return ["sonnet", "opus", "haiku"]

    def health_check(self) -> bool:
        """Check if Claude Code CLI is available."""
        return self._check_cli_available()


# For backwards compatibility, also export as LiteLLMProvider
# (tests may reference this class name)
LiteLLMProvider = ClaudeCodeCLIProvider


def get_provider(config: LLMConfig) -> BaseProvider:
    """Get the Claude Code CLI provider."""
    return ClaudeCodeCLIProvider(config)
