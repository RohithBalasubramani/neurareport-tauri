"""
Tests for image-URL parsing safety in LLM providers — lines 1250-1261 of FORENSIC_AUDIT_REPORT.md.

Covers:
- Malformed data: URLs (no comma) must not raise ValueError
- Well-formed data: URLs are split correctly
- Guard condition: ``"," in img_url`` present in source

Run with: pytest backend/tests/services/llm/test_image_url_safety.py -v
"""
from __future__ import annotations

import inspect
import json
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# Ollama Provider — inline parsing in _native_chat_completion
# =============================================================================


class TestOllamaImageUrlParsing:
    """Verify Ollama provider handles malformed data: URLs safely."""

    def _run_native_chat(self, messages):
        """Call _native_chat_completion with a mocked HTTP response."""
        from backend.app.services.llm.providers import OllamaProvider

        provider = OllamaProvider.__new__(OllamaProvider)
        provider._client = {"base_url": "http://localhost:11434"}
        # Provide the config attributes accessed after message conversion
        provider.config = MagicMock()
        provider.config.temperature = None
        provider.config.timeout_seconds = 30

        fake_response_body = json.dumps({
            "message": {"role": "assistant", "content": "ok"},
            "model": "llava",
            "done": True,
        }).encode()

        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_response_body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
            provider._native_chat_completion(messages, "llava")
            # Return the payload that was sent
            call_args = mock_open.call_args
            req = call_args[0][0]
            return json.loads(req.data)

    def test_wellformed_data_url_extracts_b64(self):
        """A proper data: URL with comma should produce images list."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "describe"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,iVBOR"},
                    },
                ],
            }
        ]
        payload = self._run_native_chat(messages)
        assert payload["messages"][0].get("images") == ["iVBOR"]

    def test_malformed_data_url_no_comma_skipped(self):
        """A data: URL without a comma must be silently skipped."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "describe"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64"},
                    },
                ],
            }
        ]
        payload = self._run_native_chat(messages)
        msg = payload["messages"][0]
        assert "images" not in msg or msg["images"] == []

    def test_http_url_ignored(self):
        """HTTP URLs should not be treated as base64 images."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "describe"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/img.png"},
                    },
                ],
            }
        ]
        payload = self._run_native_chat(messages)
        msg = payload["messages"][0]
        assert "images" not in msg or msg["images"] == []

    def test_source_has_comma_guard(self):
        """The source code must include the comma-presence guard."""
        from backend.app.services.llm.providers import OllamaProvider

        source = inspect.getsource(OllamaProvider._native_chat_completion)
        assert '"," in img_url' in source or "',' in img_url" in source, (
            "Ollama image parsing must guard against missing comma"
        )


# =============================================================================
# Anthropic Provider — _convert_messages
# =============================================================================


class TestAnthropicImageUrlParsing:
    """Verify Anthropic provider handles malformed data: URLs safely."""

    def test_wellformed_data_url_extracts_b64_and_media_type(self):
        """A proper data: URL should produce an image content block."""
        from backend.app.services.llm.providers import AnthropicProvider

        provider = AnthropicProvider.__new__(AnthropicProvider)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "describe"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,/9j/4A"},
                    },
                ],
            }
        ]
        converted = provider._convert_messages(messages)
        user_msg = converted[0]
        image_blocks = [
            b for b in user_msg["content"] if b.get("type") == "image"
        ]
        assert len(image_blocks) == 1
        assert image_blocks[0]["source"]["data"] == "/9j/4A"
        assert image_blocks[0]["source"]["media_type"] == "image/jpeg"

    def test_malformed_data_url_no_comma_skipped(self):
        """A data: URL without a comma must NOT raise ValueError."""
        from backend.app.services.llm.providers import AnthropicProvider

        provider = AnthropicProvider.__new__(AnthropicProvider)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "describe"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64"},
                    },
                ],
            }
        ]
        converted = provider._convert_messages(messages)
        user_msg = converted[0]
        image_blocks = [
            b for b in user_msg["content"] if b.get("type") == "image"
        ]
        assert len(image_blocks) == 0

    def test_source_has_comma_guard(self):
        """The source code must include the comma-presence guard."""
        from backend.app.services.llm.providers import AnthropicProvider

        source = inspect.getsource(AnthropicProvider._convert_messages)
        assert '"," in img_url' in source or "',' in img_url" in source, (
            "Anthropic image parsing must guard against missing comma"
        )
