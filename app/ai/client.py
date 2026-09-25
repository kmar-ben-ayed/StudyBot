from __future__ import annotations

import logging
from typing import List

import requests

from app.config import ConfigError, Settings

logger = logging.getLogger(__name__)

HF_CHAT_ENDPOINT = "https://router.huggingface.co/v1/chat/completions"
REQUEST_TIMEOUT_SECONDS = 30


class AIClient:
    """Talks to the Hugging Face chat completions endpoint."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def is_configured(self) -> bool:
        return self._settings.has_hf_key

    def _require_key(self) -> str:
        if not self._settings.hf_api_key:
            raise ConfigError(
                "No HF_API_KEY configured. Set HF_API_KEY in your .env file "
                "to enable AI-powered features."
            )
        return self._settings.hf_api_key

    def chat(self, messages: List[dict], temperature: float = 0.4) -> str:
        """Send a chat completion request and return the text response."""
        api_key = self._require_key()

        try:
            response = requests.post(
                HF_CHAT_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._settings.hf_model,
                    "messages": messages,
                    "temperature": temperature,
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.RequestException as exc:  # network/auth/rate-limit errors
            logger.exception("Hugging Face chat request failed")
            raise RuntimeError(f"AI provider error: {exc}") from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError) as exc:
            logger.exception("Unexpected Hugging Face response shape: %s", data)
            raise RuntimeError("Unexpected response from the AI provider.") from exc