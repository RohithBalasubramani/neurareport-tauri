# mypy: ignore-errors
"""
LLM Provider Implementation - Claude Code CLI.

NeuraReport uses Claude Code CLI as the exclusive LLM backend.
The CLI handles authentication via its own session - no API keys needed.
"""
from __future__ import annotations

import base64
import logging
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from .config import LLMConfig, LLMProvider
from backend.app.utils.errors import AppError

logger = logging.getLogger("neura.llm.providers")


def _no_window_kwargs() -> dict:
    """Return subprocess kwargs to suppress console windows on Windows."""
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # SW_HIDE
        return {"startupinfo": si, "creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


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
                **_no_window_kwargs(),
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

    def _has_images(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if any message contains image content."""
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") in ("image_url", "image"):
                        return True
        return False

    def _call_litellm_direct(
        self,
        messages: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Direct HTTP call to LiteLLM's Anthropic /v1/messages endpoint.

        Used for vision calls where Claude CLI can't pass images.
        Qwen 3.5 27B handles images natively through vLLM.
        """
        import requests as _requests

        api_base = getattr(self.config, 'api_base', 'http://localhost:4000').rstrip('/')
        url = f"{api_base}/v1/messages"

        # Convert OpenAI-style image_url blocks to Anthropic-style image blocks
        anthropic_messages = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                parts = []
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            parts.append({"type": "text", "text": part.get("text", "")})
                        elif part.get("type") == "image_url":
                            image_url = part.get("image_url", {})
                            url_str = image_url.get("url", "") if isinstance(image_url, dict) else ""
                            if url_str.startswith("data:"):
                                # data:image/png;base64,<data>
                                header, b64_data = url_str.split(",", 1)
                                media_type = header.split(";")[0].split(":")[1] if ":" in header else "image/png"
                                parts.append({
                                    "type": "image",
                                    "source": {"type": "base64", "media_type": media_type, "data": b64_data}
                                })
                        elif part.get("type") == "image":
                            parts.append(part)  # Already Anthropic format
                    elif isinstance(part, str):
                        parts.append({"type": "text", "text": part})
                anthropic_messages.append({"role": msg.get("role", "user"), "content": parts})
            else:
                anthropic_messages.append({"role": msg.get("role", "user"), "content": str(content)})

        payload = {
            "model": "claude-sonnet-4-6",
            "max_tokens": kwargs.get("max_tokens", 8192),
            "messages": anthropic_messages,
        }

        start_time = time.time()
        logger.info("litellm_vision_call", extra={
            "event": "litellm_vision_call",
            "message_count": len(messages),
        })

        try:
            resp = _requests.post(url, json=payload, headers={
                "x-api-key": getattr(self.config, 'api_key', 'dummy') or "dummy",
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }, timeout=self.config.timeout_seconds)

            data = resp.json()
            if "error" in data:
                raise AppError(
                    code="llm_call_failed",
                    message=f"LiteLLM vision call failed: {data['error']}",
                    status_code=502,
                )

            content = data.get("content", [{}])[0].get("text", "")
            elapsed = time.time() - start_time
            usage = data.get("usage", {})

            logger.info("litellm_vision_success", extra={
                "event": "litellm_vision_success",
                "model": data.get("model", "?"),
                "elapsed_seconds": round(elapsed, 2),
                "output_length": len(content),
            })

            return {
                "id": data.get("id", f"litellm-{int(time.time())}"),
                "model": data.get("model", "qwen"),
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }],
                "usage": {
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
            }

        except AppError:
            raise
        except Exception as e:
            logger.error("litellm_vision_failed", extra={"error": _sanitize_error(e)})
            raise AppError(
                code="llm_call_failed",
                message="Vision LLM call failed.",
                status_code=502,
                detail=_sanitize_error(e),
            )

    def _call_claude_cli(self, prompt: str) -> Dict[str, Any]:
        """
        Text-only call via Claude Code CLI subprocess.

        Claude CLI → ANTHROPIC_BASE_URL (LiteLLM) → vLLM → Qwen 3.5 27B.
        Used for text-only calls (mapping, contract, chat).
        """
        import tempfile

        cmd = [self._claude_bin, "-p", "--bare", "--model", "sonnet"]

        logger.info("claude_code_cli_call", extra={
            "event": "claude_code_cli_call",
            "prompt_length": len(prompt),
        })

        start_time = time.time()
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                prompt_file = f.name

            import os as _env_os
            env = _env_os.environ.copy()
            env.pop('CLAUDECODE', None)
            env['ANTHROPIC_BASE_URL'] = getattr(self.config, 'api_base', 'http://localhost:4000').rstrip('/v1').rstrip('/')
            env['ANTHROPIC_API_KEY'] = getattr(self.config, 'api_key', 'dummy') or 'dummy'

            with open(prompt_file, 'r', encoding='utf-8') as pf:
                result = subprocess.run(
                    cmd, stdin=pf, capture_output=True, text=True,
                    timeout=self.config.timeout_seconds, env=env,
                    **_no_window_kwargs(),
                )

            import os as _os
            _os.unlink(prompt_file)

            if result.returncode != 0:
                error_msg = (result.stderr or result.stdout or "").strip()[:500]
                logger.error("claude_code_cli_error", extra={"error": error_msg, "returncode": result.returncode})
                raise AppError(code="llm_call_failed", message="Claude CLI returned an error.", status_code=502, detail=error_msg)

            content = result.stdout.strip()
            elapsed = time.time() - start_time

            logger.info("claude_code_cli_success", extra={
                "event": "claude_code_cli_success",
                "elapsed_seconds": round(elapsed, 2),
                "output_length": len(content),
            })

            input_tokens = len(prompt) // 4
            output_tokens = len(content) // 4

            return {
                "id": f"claude-cli-{int(time.time())}",
                "model": "qwen",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": input_tokens, "completion_tokens": output_tokens, "total_tokens": input_tokens + output_tokens},
            }

        except subprocess.TimeoutExpired:
            raise AppError(code="llm_timeout", message=f"Timed out after {self.config.timeout_seconds}s.", status_code=504)
        except AppError:
            raise
        except Exception as e:
            logger.error("claude_code_cli_failed", extra={"error": _sanitize_error(e)})
            raise AppError(code="llm_error", message="AI request failed.", status_code=502, detail=_sanitize_error(e))

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Hybrid provider: Claude CLI for text, direct LiteLLM for vision.

        - Messages with images → direct HTTP to LiteLLM /v1/messages
          (Anthropic format, LiteLLM routes to Qwen 3.5 27B on vLLM)
        - Text-only messages → Claude CLI subprocess with --bare
          (ANTHROPIC_BASE_URL redirects to LiteLLM → Qwen 3.5 27B)

        Both paths end at Qwen 3.5 27B. Claude Code CLI stays in the loop
        for text calls. No Anthropic API is ever hit.
        """
        self.get_client()

        if self._has_images(messages):
            return self._call_litellm_direct(messages, **kwargs)
        else:
            prompt = self._build_prompt(messages)
            return self._call_claude_cli(prompt)

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
