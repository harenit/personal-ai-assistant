"""Groq cloud AI backend for ultra-fast student agent reasoning.

Runs high-performance models (e.g. qwen/qwen3.8-27b) with sub-second latency
and native OpenAI-compatible function/tool calling.
"""
from __future__ import annotations

import json
import logging
import os
import httpx
from app.ai.backend import AIBackendError

logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqBackend:
    """Groq Cloud API integration satisfying the AIBackend protocol."""

    def __init__(self) -> None:
        self._api_key = os.environ.get("GROQ_API_KEY", "")

    @property
    def api_key(self) -> str:
        return os.environ.get("GROQ_API_KEY", self._api_key)

    @property
    def model(self) -> str:
        return os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL)

    def is_available(self) -> bool:
        """Whether a valid Groq API key is present."""
        key = self.api_key.strip()
        return bool(key and key.startswith("gsk_"))

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        key = self.api_key.strip()
        if not key:
            raise AIBackendError("GROQ_API_KEY is not configured")

        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 1024,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "JARVIS-Student-Agent/1.0",
        }

        try:
            with httpx.Client(timeout=18.0) as client:
                resp = client.post(GROQ_API_URL, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise AIBackendError(f"Groq API error {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
        except httpx.RequestError as exc:
            raise AIBackendError(f"Failed to reach Groq API: {exc}") from exc

        choices = data.get("choices")
        if not choices:
            raise AIBackendError("Groq returned an empty response")

        msg = choices[0].get("message", {})
        result: dict = {
            "role": msg.get("role", "assistant"),
            "content": msg.get("content") or "",
        }

        # Parse tool calls if returned
        raw_tools = msg.get("tool_calls")
        if raw_tools:
            parsed_tools = []
            for t in raw_tools:
                fn = t.get("function", {})
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}
                parsed_tools.append({
                    "id": t.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": fn.get("name", ""),
                        "arguments": args,
                    },
                })
            result["tool_calls"] = parsed_tools

        return result
