import json
import logging
import re
from typing import Any, Optional
import requests
from backend.config.settings import settings
from backend.llm.prompts import JARVIS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.openai_base_url = settings.OPENAI_BASE_URL
        self.openai_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
        temperature: float = 0.2
    ) -> dict[str, Any]:
        """
        Sends conversation messages and tools to LLM.
        Returns:
        {
            "content": "Text response or None",
            "tool_calls": [
                {"id": "...", "name": "tool_name", "arguments": {...}}
            ]
        }
        """
        if self.provider == "openai" and self.openai_key:
            return self._chat_openai(messages, tools, temperature)
        return self._chat_ollama(messages, tools, temperature)

    def _chat_ollama(
        self,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
        temperature: float = 0.2
    ) -> dict[str, Any]:
        url = f"{self.ollama_base_url}/api/chat"

        # Ensure system prompt is present
        formatted_messages = []
        has_system = any(m.get("role") == "system" for m in messages)
        if not has_system:
            formatted_messages.append({"role": "system", "content": JARVIS_SYSTEM_PROMPT})
        formatted_messages.extend(messages)

        payload: dict[str, Any] = {
            "model": self.ollama_model,
            "messages": formatted_messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code != 200:
                logger.error(f"Ollama returned status {response.status_code}: {response.text}")
                return {
                    "content": f"Ollama error (HTTP {response.status_code}). Please verify model '{self.ollama_model}' is available.",
                    "tool_calls": []
                }

            data = response.json()
            msg = data.get("message", {})
            content = msg.get("content", "")
            raw_tool_calls = msg.get("tool_calls", [])

            tool_calls = []
            if raw_tool_calls:
                for idx, tc in enumerate(raw_tool_calls):
                    fn = tc.get("function", {})
                    name = fn.get("name")
                    args = fn.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}
                    if name:
                        tool_calls.append({
                            "id": tc.get("id", f"call_{idx}"),
                            "name": name,
                            "arguments": args
                        })

            # Check if LLM output JSON tool call in text content fallback
            if not tool_calls and content and ("\"function\"" in content or "\"name\"" in content):
                parsed = self._extract_tool_call_from_text(content)
                if parsed:
                    tool_calls = parsed
                    content = ""

            return {
                "content": content,
                "tool_calls": tool_calls
            }

        except Exception as e:
            logger.exception(f"Error querying Ollama: {str(e)}")
            return {
                "content": f"Failed to connect to local Ollama at {self.ollama_base_url}: {str(e)}",
                "tool_calls": []
            }

    def _chat_openai(
        self,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
        temperature: float = 0.2
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        url = f"{self.openai_base_url}/chat/completions"

        formatted_messages = []
        has_system = any(m.get("role") == "system" for m in messages)
        if not has_system:
            formatted_messages.append({"role": "system", "content": JARVIS_SYSTEM_PROMPT})
        formatted_messages.extend(messages)

        payload: dict[str, Any] = {
            "model": self.openai_model,
            "messages": formatted_messages,
            "temperature": temperature
        }
        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            if response.status_code != 200:
                return {"content": f"OpenAI error: {response.text}", "tool_calls": []}

            data = response.json()
            choice = data["choices"][0]["message"]
            content = choice.get("content", "")
            raw_calls = choice.get("tool_calls", [])

            tool_calls = []
            for tc in raw_calls:
                fn = tc.get("function", {})
                name = fn.get("name")
                args_str = fn.get("arguments", "{}")
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except Exception:
                    args = {}
                tool_calls.append({
                    "id": tc.get("id"),
                    "name": name,
                    "arguments": args
                })

            return {"content": content, "tool_calls": tool_calls}

        except Exception as e:
            return {"content": f"OpenAI connection error: {str(e)}", "tool_calls": []}

    def _extract_tool_call_from_text(self, text: str) -> list[dict[str, Any]]:
        """Fallback to detect JSON tool call written directly in text."""
        try:
            match = re.search(r'\{.*"name"\s*:\s*"([a-zA-Z0-9_]+)".*\}', text, re.DOTALL)
            if match:
                blob = json.loads(match.group(0))
                name = blob.get("name") or blob.get("function", {}).get("name")
                args = blob.get("arguments") or blob.get("parameters") or blob.get("function", {}).get("arguments", {})
                if name:
                    return [{"id": "extracted_call", "name": name, "arguments": args}]
        except Exception:
            pass
        return []

llm_client = LLMClient()
