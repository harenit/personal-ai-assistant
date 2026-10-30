"""Registry of available AI backends, with automatic cloud-to-local failover.

Supports Groq cloud inference (sub-second) and Ollama local inference (offline).
"""
from __future__ import annotations

import os
from app.ai import ollama_backend
from app.ai.groq_backend import GroqBackend
from app.ai.backend import AIBackend, AIBackendError

_groq = GroqBackend()


class SmartFallbackBackend:
    """Intelligently routes requests to Groq when configured, with seamless
    fallback to local Ollama if offline or if Groq fails."""

    def is_available(self) -> bool:
        provider = os.environ.get("AI_PROVIDER", "groq").lower()
        if provider == "groq" and _groq.is_available():
            return True
        if provider == "ollama" and ollama_backend.is_available():
            return True
        return _groq.is_available() or ollama_backend.is_available()

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        provider = os.environ.get("AI_PROVIDER", "groq").lower()

        # Primary attempt based on provider preference
        if provider == "groq" and _groq.is_available():
            try:
                return _groq.chat(messages, tools=tools)
            except Exception as e:
                if ollama_backend.is_available():
                    return ollama_backend.chat(messages, tools=tools)
                raise AIBackendError(f"Groq failed and local Ollama is offline: {e}") from e

        if ollama_backend.is_available():
            try:
                return ollama_backend.chat(messages, tools=tools)
            except Exception as e:
                if _groq.is_available():
                    return _groq.chat(messages, tools=tools)
                raise AIBackendError(f"Ollama failed and Groq is unavailable: {e}") from e

        if _groq.is_available():
            return _groq.chat(messages, tools=tools)

        raise AIBackendError("No AI backend is currently reachable (Groq or Ollama).")


_smart_backend = SmartFallbackBackend()

_BACKENDS: dict[str, AIBackend] = {
    "groq": _groq,
    "ollama": ollama_backend,
    "smart": _smart_backend,
}

DEFAULT_BACKEND = "smart"


def get_backend(name: str = DEFAULT_BACKEND) -> AIBackend:
    return _BACKENDS.get(name, _smart_backend)
