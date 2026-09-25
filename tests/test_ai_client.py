from unittest.mock import MagicMock, patch

import pytest

from app.ai.client import AIClient
from app.config import ConfigError, Settings


def make_settings(hf_api_key=None) -> Settings:
    return Settings(
        discord_token="token",
        hf_api_key=hf_api_key,
        hf_model="meta-llama/Llama-3.1-8B-Instruct",
        embedding_model="all-MiniLM-L6-v2",
        chunk_size=800,
        chunk_overlap=120,
        top_k=4,
        log_level="INFO",
    )


def test_is_configured_reflects_hf_key():
    assert AIClient(make_settings(hf_api_key=None)).is_configured is False
    assert AIClient(make_settings(hf_api_key="hf_xxx")).is_configured is True


def test_chat_raises_config_error_without_key():
    client = AIClient(make_settings(hf_api_key=None))
    with pytest.raises(ConfigError):
        client.chat([{"role": "user", "content": "hi"}])


@patch("app.ai.client.requests.post")
def test_chat_sends_expected_request_and_parses_response(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello from HF!"}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    client = AIClient(make_settings(hf_api_key="hf_xxx"))
    result = client.chat([{"role": "user", "content": "hi"}])

    assert result == "Hello from HF!"
    called_url = mock_post.call_args.args[0]
    called_headers = mock_post.call_args.kwargs["headers"]
    assert "router.huggingface.co" in called_url
    assert called_headers["Authorization"] == "Bearer hf_xxx"


@patch("app.ai.client.requests.post")
def test_chat_wraps_network_errors(mock_post):
    import requests

    mock_post.side_effect = requests.RequestException("boom")
    client = AIClient(make_settings(hf_api_key="hf_xxx"))

    with pytest.raises(RuntimeError):
        client.chat([{"role": "user", "content": "hi"}])
