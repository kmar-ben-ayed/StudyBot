from app.utils.discord_helpers import split_for_discord


def test_short_text_is_single_chunk():
    parts = split_for_discord("hello world")
    assert parts == ["hello world"]


def test_empty_text_returns_no_chunks():
    assert split_for_discord("") == []


def test_long_text_is_split_under_limit():
    text = ("word " * 1000).strip()  # ~5000 chars
    parts = split_for_discord(text, limit=2000)

    assert len(parts) > 1
    assert all(len(p) <= 2000 for p in parts)
    # No content should be lost (ignoring whitespace differences from splitting).
    rejoined = " ".join(parts)
    assert rejoined.split() == text.split()
