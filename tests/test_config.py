import os

from app.config import load_settings


def test_defaults_when_env_missing(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("AI_API_KEY", raising=False)
    settings = load_settings()

    assert settings.has_discord_token is False
    assert settings.has_ai_key is False
    assert settings.ai_model  # has a sensible default
    assert settings.chunk_size > 0


def test_settings_read_env_vars(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "abc123")
    monkeypatch.setenv("AI_API_KEY", "sk-test")
    monkeypatch.setenv("AI_MODEL", "custom-model")

    settings = load_settings()

    assert settings.has_discord_token is True
    assert settings.has_ai_key is True
    assert settings.ai_model == "custom-model"
