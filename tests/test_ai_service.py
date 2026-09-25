import pytest

from app.ai.service import AIService
from app.config import ConfigError


def test_answer_general_uses_client(fake_ai_client):
    service = AIService(fake_ai_client)
    result = service.answer_general("What is a process?")
    assert result.startswith("FAKE_ANSWER::")


def test_answer_general_raises_when_not_configured(unconfigured_ai_client):
    service = AIService(unconfigured_ai_client)
    with pytest.raises(ConfigError):
        service.answer_general("What is a process?")


def test_answer_with_context_uses_client(fake_ai_client):
    service = AIService(fake_ai_client)
    result = service.answer_with_context("Explain deadlocks", ["deadlock context"])
    assert result.startswith("FAKE_ANSWER::")


def test_summarize_requires_context(fake_ai_client):
    service = AIService(fake_ai_client)
    with pytest.raises(ValueError):
        service.summarize([])


def test_generate_quiz_requires_context(fake_ai_client):
    service = AIService(fake_ai_client)
    with pytest.raises(ValueError):
        service.generate_quiz([])


def test_generate_flashcards_requires_context(fake_ai_client):
    service = AIService(fake_ai_client)
    with pytest.raises(ValueError):
        service.generate_flashcards([])
