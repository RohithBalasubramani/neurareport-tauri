"""OpenAI LLM adapter implementation."""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Optional

from backend.engine.core.errors import ExternalServiceError
from .base import BaseLLMClient, LLMMessage, LLMResponse

logger = logging.getLogger("neura.adapters.llm.openai")

_FORCE_GPT5 = os.getenv("NEURA_FORCE_GPT5", "true").lower() in {"1", "true", "yes"}


class OpenAIClient(BaseLLMClient):
    """OpenAI API client implementation."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        default_model: str = "gpt-5",
        max_retries: int = 3,
        timeout_seconds: float = 60.0,
        base_url: Optional[str] = None,
    ) -> None:
        super().__init__(
            default_model=default_model,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
        )
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._base_url = base_url
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "openai package is required. Install with: pip install openai"
                )

            # Validate API key format
            if not self._api_key:
                raise ValueError(
                    "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
                )
            if not self._api_key.startswith(("sk-", "sess-")):
                logger.warning(
                    "OpenAI API key may be invalid (expected 'sk-' or 'sess-' prefix)",
                    extra={"event": "api_key_format_warning"},
                )

            kwargs: Dict[str, Any] = {
                "api_key": self._api_key,
                "timeout": self._timeout,
                "max_retries": self._max_retries,
            }
            if self._base_url:
                kwargs["base_url"] = self._base_url

            self._client = OpenAI(**kwargs)

        return self._client

    def complete(
        self,
        messages: List[LLMMessage],
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send a completion request to OpenAI."""
        client = self._get_client()
        model_name = _force_gpt5(model or self._default_model)

        kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": self._prepare_messages(messages),
            "temperature": temperature,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        start = time.perf_counter()
        try:
            if _use_responses_model(model_name):
                payload = _prepare_responses_payload(kwargs)
                try:
                    response = client.responses.create(**payload)
                except AttributeError as exc:
                    raise ExternalServiceError(
                        message=(
                            "OpenAI Responses API is required for gpt-5. "
                            "Upgrade the openai package to >=1.0.0."
                        ),
                        service="openai",
                        cause=exc,
                    )
                content = _response_output_text(response)
                usage = _response_usage(response)
                elapsed = (time.perf_counter() - start) * 1000

                logger.info(
                    "llm_completion_success",
                    extra={
                        "event": "llm_completion_success",
                        "model": model_name,
                        "elapsed_ms": elapsed,
                        "tokens": usage.get("total_tokens", 0),
                        "endpoint": "responses",
                    },
                )

                return LLMResponse(
                    content=content,
                    model=response.model if hasattr(response, "model") else model_name,
                    usage=usage,
                    finish_reason="stop",
                    raw_response=response,
                )

            response = client.chat.completions.create(**kwargs)
            elapsed = (time.perf_counter() - start) * 1000

            logger.info(
                "llm_completion_success",
                extra={
                    "event": "llm_completion_success",
                    "model": model_name,
                    "elapsed_ms": elapsed,
                    "tokens": response.usage.total_tokens if response.usage else 0,
                },
            )

            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                finish_reason=response.choices[0].finish_reason,
                raw_response=response,
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            logger.exception(
                "llm_completion_failed",
                extra={
                    "event": "llm_completion_failed",
                    "model": model_name,
                    "elapsed_ms": elapsed,
                    "error": str(e),
                },
            )
            raise ExternalServiceError(
                message="OpenAI API call failed",
                service="openai",
                cause=e,
            )

    async def complete_async(
        self,
        messages: List[LLMMessage],
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Send an async completion request to OpenAI."""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

        kwargs: Dict[str, Any] = {
            "api_key": self._api_key,
            "timeout": self._timeout,
            "max_retries": self._max_retries,
        }
        if self._base_url:
            kwargs["base_url"] = self._base_url

        client = AsyncOpenAI(**kwargs)
        model_name = _force_gpt5(model or self._default_model)

        request_kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": self._prepare_messages(messages),
            "temperature": temperature,
        }

        if max_tokens:
            request_kwargs["max_tokens"] = max_tokens

        if json_mode:
            request_kwargs["response_format"] = {"type": "json_object"}

        start = time.perf_counter()
        try:
            if _use_responses_model(model_name):
                payload = _prepare_responses_payload(request_kwargs)
                try:
                    response = await client.responses.create(**payload)
                except AttributeError as exc:
                    raise ExternalServiceError(
                        message=(
                            "OpenAI Responses API is required for gpt-5. "
                            "Upgrade the openai package to >=1.0.0."
                        ),
                        service="openai",
                        cause=exc,
                    )
                content = _response_output_text(response)
                usage = _response_usage(response)
                elapsed = (time.perf_counter() - start) * 1000

                logger.info(
                    "llm_completion_success_async",
                    extra={
                        "event": "llm_completion_success_async",
                        "model": model_name,
                        "elapsed_ms": elapsed,
                        "tokens": usage.get("total_tokens", 0),
                        "endpoint": "responses",
                    },
                )

                return LLMResponse(
                    content=content,
                    model=response.model if hasattr(response, "model") else model_name,
                    usage=usage,
                    finish_reason="stop",
                    raw_response=response,
                )

            response = await client.chat.completions.create(**request_kwargs)
            elapsed = (time.perf_counter() - start) * 1000

            logger.info(
                "llm_completion_success_async",
                extra={
                    "event": "llm_completion_success_async",
                    "model": model_name,
                    "elapsed_ms": elapsed,
                    "tokens": response.usage.total_tokens if response.usage else 0,
                },
            )

            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                finish_reason=response.choices[0].finish_reason,
                raw_response=response,
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            logger.exception(
                "llm_completion_failed_async",
                extra={
                    "event": "llm_completion_failed_async",
                    "model": model_name,
                    "elapsed_ms": elapsed,
                    "error": str(e),
                },
            )
            raise ExternalServiceError(
                message="OpenAI API call failed",
                service="openai",
                cause=e,
            )


def _use_responses_model(model_name: Optional[str]) -> bool:
    force = os.getenv("OPENAI_USE_RESPONSES", "").lower() in {"1", "true", "yes"}
    return force or str(model_name or "").lower().startswith("gpt-5")


def _force_gpt5(model_name: Optional[str]) -> str:
    if not _FORCE_GPT5:
        return str(model_name or "gpt-5").strip() or "gpt-5"
    normalized = str(model_name or "").strip()
    if normalized.lower().startswith("gpt-5"):
        return normalized
    if normalized:
        logger.warning(
            "llm_model_overridden",
            extra={"event": "llm_model_overridden", "requested": normalized, "forced": "gpt-5"},
        )
    return "gpt-5"


def _prepare_responses_payload(request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(request_kwargs)
    messages = payload.pop("messages", [])
    payload["input"] = _messages_to_responses_input(messages)
    if "max_tokens" in payload and "max_output_tokens" not in payload:
        payload["max_output_tokens"] = payload.pop("max_tokens")
    return payload


def _messages_to_responses_input(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    converted: List[Dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role") or "user"
        content = message.get("content", "")
        if isinstance(content, list):
            parts: List[Dict[str, Any]] = []
            for part in content:
                if isinstance(part, dict):
                    part_type = part.get("type")
                    if part_type == "text":
                        parts.append({"type": "input_text", "text": part.get("text", "")})
                        continue
                    if part_type == "image_url":
                        image_url = part.get("image_url")
                        if isinstance(image_url, dict):
                            image_url = image_url.get("url") or image_url.get("image_url")
                        parts.append({"type": "input_image", "image_url": image_url})
                        continue
                    parts.append(part)
                else:
                    parts.append({"type": "input_text", "text": str(part)})
            content = parts
        converted.append({"role": role, "content": content})
    return converted


def _response_output_text(response: Any) -> str:
    if isinstance(response, dict):
        output_text = response.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text
        output = response.get("output")
    else:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text
        output = getattr(response, "output", None)

    if isinstance(output, list):
        texts: List[str] = []
        for item in output:
            if isinstance(item, dict):
                item_type = item.get("type")
                content = item.get("content") or []
            else:
                item_type = getattr(item, "type", None)
                content = getattr(item, "content", None) or []
            if item_type != "message":
                continue
            for segment in content:
                if isinstance(segment, dict):
                    seg_type = segment.get("type")
                    text = segment.get("text")
                else:
                    seg_type = getattr(segment, "type", None)
                    text = getattr(segment, "text", None)
                if seg_type in {"output_text", "text"} and isinstance(text, str):
                    texts.append(text)
        if texts:
            return "\n".join(texts)
    return ""


def _response_usage(response: Any) -> Dict[str, int]:
    usage = response.get("usage") if isinstance(response, dict) else getattr(response, "usage", None)
    if usage is None:
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    if isinstance(usage, dict):
        input_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
        output_tokens = usage.get("output_tokens") or usage.get("completion_tokens") or 0
    else:
        input_tokens = getattr(usage, "input_tokens", None)
        if input_tokens is None:
            input_tokens = getattr(usage, "prompt_tokens", 0)
        output_tokens = getattr(usage, "output_tokens", None)
        if output_tokens is None:
            output_tokens = getattr(usage, "completion_tokens", 0)
    total_tokens = int(input_tokens or 0) + int(output_tokens or 0)
    return {
        "prompt_tokens": int(input_tokens or 0),
        "completion_tokens": int(output_tokens or 0),
        "total_tokens": int(total_tokens),
    }
