"""
Universal multi-provider LLM interface supporting Gemini, Claude, GPT, DeepSeek, and Ollama.
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any, List
import requests

logger = logging.getLogger(__name__)


class UnifiedLLM:
    """Dispatches prompts to Gemini, Anthropic, OpenAI, DeepSeek, or local Ollama."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        self.provider, self.model = self._resolve_provider_and_model(provider, model)
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._resolve_api_key()

    def _resolve_provider_and_model(self, provider: Optional[str], model: Optional[str]):
        if provider:
            p = provider.lower()
            m = model or self._default_model_for_provider(p)
            return p, m

        m = (model or "").lower()
        if "claude" in m:
            return "anthropic", model
        if any(x in m for x in ["gpt", "o1", "o3", "chatgpt"]):
            return "openai", model
        if "gemini" in m:
            return "gemini", model
        if "deepseek" in m:
            return "deepseek", model

        # Check environment variables
        if os.getenv("GEMINI_API_KEY"):
            return "gemini", model or "gemini-3-flash-preview"
        if os.getenv("OPENAI_API_KEY"):
            return "openai", model or "gpt-4o"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic", model or "claude-3-5-sonnet-20241022"
        if os.getenv("DEEPSEEK_API_KEY"):
            return "deepseek", model or "deepseek-chat"

        return "gemini", model or "gemini-3-flash-preview"

    def _default_model_for_provider(self, provider: str) -> str:
        defaults = {
            "gemini": "gemini-3-flash-preview",
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "deepseek": "deepseek-chat",
            "ollama": "llama3.2",
        }
        return defaults.get(provider, "gemini-3-flash-preview")

    def _resolve_api_key(self):
        if self.api_key:
            return
        key_map = {
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env_var = key_map.get(self.provider)
        if env_var:
            self.api_key = os.getenv(env_var)

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate response via configured provider."""
        if self.provider == "gemini":
            return self._call_gemini(prompt, system_instruction)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt, system_instruction)
        elif self.provider in ("openai", "deepseek", "ollama") or self.base_url:
            return self._call_openai_compatible(prompt, system_instruction)
        else:
            return self._call_gemini(prompt, system_instruction)

    def _call_gemini(self, prompt: str, system_instruction: Optional[str]) -> str:
        models_to_try = [
            self.model,
            "gemini-3.1-flash-lite-preview",
            "gemini-3-flash-preview",
            "gemini-flash-latest",
        ]
        unique_models = [m for m in dict.fromkeys(models_to_try) if m]

        last_error = None
        for m in unique_models:
            for retry in range(2):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                    contents = []
                    if system_instruction:
                        contents.append({"role": "user", "parts": [{"text": f"SYSTEM: {system_instruction}"}]})
                    contents.append({"role": "user", "parts": [{"text": prompt}]})
                    resp = requests.post(url, json={"contents": contents}, timeout=self.timeout)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"]
                    elif resp.status_code in (503, 429):
                        time.sleep(2)
                        continue
                    last_error = f"{m} HTTP {resp.status_code}: {resp.text[:100]}"
                    break
                except Exception as e:
                    last_error = e

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    def _call_anthropic(self, prompt: str, system_instruction: Optional[str]) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_instruction:
            payload["system"] = system_instruction

        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]

    def _call_openai_compatible(self, prompt: str, system_instruction: Optional[str]) -> str:
        base = self.base_url
        if not base:
            if self.provider == "deepseek":
                base = "https://api.deepseek.com/v1"
            elif self.provider == "ollama":
                base = "http://localhost:11434/v1"
            else:
                base = "https://api.openai.com/v1"

        url = f"{base.rstrip('/')}/chat/completions"
        headers = {"content-type": "application/json"}
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
