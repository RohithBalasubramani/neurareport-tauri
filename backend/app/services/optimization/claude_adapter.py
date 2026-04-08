from __future__ import annotations

import logging
from collections import deque
from typing import Any, Dict, List, Optional

logger = logging.getLogger("neura.optimization.claude_adapter")

# ---------------------------------------------------------------------------
# Optional dependency: DSPy
# ---------------------------------------------------------------------------
_dspy_available = False
try:
    import dspy

    _dspy_available = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Import the existing LLM client
# ---------------------------------------------------------------------------
from backend.app.services.llm.client import LLMClient, get_llm_client


# =========================================================================== #
#  ClaudeCodeLM — DSPy LM adapter backed by the existing LLMClient           #
# =========================================================================== #

# Determine base class: use dspy.LM if available, otherwise plain object.
_BaseLM: type = object
if _dspy_available:
    try:
        _BaseLM = dspy.LM  # type: ignore[misc]
    except AttributeError:
        # Older dspy versions may not expose dspy.LM directly.
        _BaseLM = object


class ClaudeCodeLM(_BaseLM):  # type: ignore[misc]
    """DSPy language model adapter that routes through :class:`LLMClient`.

    This allows DSPy modules (e.g. ``dspy.ChainOfThought``) to use the same
    LLM infrastructure already configured in NeuraReport, including circuit
    breakers, caching, retries, and provider fallback.

    Args:
        model: Model name hint (e.g. ``"sonnet"``, ``"opus"``).  Passed
            through to :meth:`LLMClient.complete` as the ``model`` kwarg.
        client: Optional pre-existing :class:`LLMClient` instance.  If
            ``None``, ``get_llm_client()`` is called to obtain the shared
            singleton.
        **kwargs: Extra keyword arguments forwarded to the base class (if
            it is ``dspy.LM``).
    """

    def __init__(
        self,
        model: str = "sonnet",
        client: Optional[LLMClient] = None,
        **kwargs: Any,
    ) -> None:
        if _BaseLM is not object:
            # dspy.LM base — pass model identifier up
            try:
                super().__init__(model=f"claude/{model}", **kwargs)
            except TypeError:
                # Fallback if dspy.LM constructor signature differs
                super().__init__()
        else:
            super().__init__()

        self._model = model
        self._client = client or get_llm_client()
        self._history: deque[Dict[str, Any]] = deque(maxlen=100)

        logger.info(
            "claude_lm_init",
            extra={"event": "claude_lm_init", "model": model},
        )

    # ------------------------------------------------------------------ #
    #  Core call interface                                                #
    # ------------------------------------------------------------------ #

    def __call__(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> list[str]:
        """Execute a completion and return a list containing the response text.

        DSPy expects LM.__call__ to return ``list[str]``.
        """
        if prompt is not None and messages is None:
            msgs: List[Dict[str, Any]] = [{"role": "user", "content": str(prompt)}]
        elif messages is not None:
            msgs = list(messages)
        else:
            msgs = [{"role": "user", "content": ""}]

        response = self._client.complete(
            messages=msgs,
            model=self._model,
            description="dspy_adapter",
            **kwargs,
        )

        # Extract response text from OpenAI-compatible dict
        response_text = self._extract_text(response)

        # Record in history
        self._history.append({
            "messages": msgs,
            "response": response_text[:500],
            "model": self._model,
        })

        return [response_text]

    # ------------------------------------------------------------------ #
    #  History inspection                                                 #
    # ------------------------------------------------------------------ #

    def inspect_history(self, n: int = 1) -> str:
        """Return a human-readable summary of the last *n* calls."""
        entries = list(self._history)[-n:]
        if not entries:
            return "(no history)"

        parts: list[str] = []
        for i, entry in enumerate(entries, 1):
            msg_preview = entry["messages"][-1]["content"][:200] if entry["messages"] else ""
            parts.append(
                f"--- Call {i} (model={entry['model']}) ---\n"
                f"Input:  {msg_preview}...\n"
                f"Output: {entry['response'][:200]}..."
            )
        return "\n\n".join(parts)

    # ------------------------------------------------------------------ #
    #  Internals                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_text(response: Dict[str, Any]) -> str:
        """Pull the assistant text out of an OpenAI-compatible response."""
        try:
            choices = response.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
        except (AttributeError, IndexError, TypeError):
            pass
        # Fallback: some providers return a plain string
        if isinstance(response, str):
            return response
        return str(response)


# =========================================================================== #
#  Global configuration helper                                                #
# =========================================================================== #

_configured = False


def configure_dspy_with_claude(
    model: str = "sonnet",
    client: Optional[LLMClient] = None,
) -> bool:
    """Configure DSPy to use :class:`ClaudeCodeLM` as its default LM.

    This is a no-op if DSPy is not installed or if configuration has already
    been applied.

    Args:
        model: Model name hint forwarded to :class:`ClaudeCodeLM`.
        client: Optional pre-existing :class:`LLMClient`.

    Returns:
        ``True`` if DSPy was successfully configured, ``False`` otherwise.
    """
    global _configured

    if not _dspy_available:
        logger.info(
            "dspy_configure_skip",
            extra={"event": "dspy_configure_skip", "reason": "dspy_unavailable"},
        )
        return False

    if _configured:
        logger.debug(
            "dspy_already_configured",
            extra={"event": "dspy_already_configured"},
        )
        return True

    try:
        lm = ClaudeCodeLM(model=model, client=client)

        # Try the modern API first, fall back to legacy
        try:
            dspy.configure(lm=lm)
        except (AttributeError, TypeError):
            try:
                dspy.settings.configure(lm=lm)
            except (AttributeError, TypeError):
                logger.warning(
                    "dspy_configure_fallback",
                    extra={
                        "event": "dspy_configure_fallback",
                        "note": "Could not call dspy.configure or dspy.settings.configure",
                    },
                )
                return False

        _configured = True
        logger.info(
            "dspy_configured",
            extra={"event": "dspy_configured", "model": model},
        )
        return True

    except Exception:
        logger.warning(
            "dspy_configure_error",
            exc_info=True,
            extra={"event": "dspy_configure_error"},
        )
        return False


def is_configured() -> bool:
    """Check whether DSPy has been configured with the Claude adapter."""
    return _configured


def reset_configuration() -> None:
    """Reset the configuration flag (mainly for testing)."""
    global _configured
    _configured = False
