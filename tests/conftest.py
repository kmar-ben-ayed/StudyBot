"""
Shared pytest fixtures.

Two fakes stand in for the two real AI building blocks, so no test ever
makes a network call or downloads a real model:

  - FakeAIClient: mimics AIClient's public interface (is_configured, chat)
    without calling Hugging Face.
  - FakeEncoder: mimics sentence-transformers' `.encode()` method with a
    deterministic hash-based vector, injected into EmbeddingService.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List

import pytest


class FakeAIClient:
    """Deterministic stand-in for AIClient — no network calls."""

    def __init__(self, configured: bool = True):
        self._configured = configured
        self.last_messages = None

    @property
    def is_configured(self) -> bool:
        return self._configured

    def chat(self, messages: List[dict], temperature: float = 0.4) -> str:
        self.last_messages = messages
        # Echo something derived from the input so tests can assert on it.
        user_content = messages[-1]["content"]
        return f"FAKE_ANSWER::{user_content[:50]}"


class FakeEncoder:
    """Deterministic stand-in for a sentence-transformers model."""

    def encode(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vectors.append([b / 255.0 for b in digest[:8]])
        return vectors


@pytest.fixture
def fake_ai_client():
    return FakeAIClient(configured=True)


@pytest.fixture
def unconfigured_ai_client():
    return FakeAIClient(configured=False)


@pytest.fixture
def fake_encoder():
    return FakeEncoder()


@pytest.fixture
def sample_pdf_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "sample_course.pdf"


@pytest.fixture
def tmp_vector_store_dir(tmp_path):
    return tmp_path / "vector_store"
