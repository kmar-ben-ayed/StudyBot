import pytest

from app.rag.chunker import TextChunker


def test_empty_text_returns_no_chunks():
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    assert chunker.split("") == []
    assert chunker.split("   ") == []


def test_short_text_produces_one_chunk():
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    chunks = chunker.split("Hello world.")
    assert len(chunks) == 1
    assert chunks[0].text == "Hello world."


def test_long_text_is_split_into_multiple_overlapping_chunks():
    text = "A" * 250
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.split(text)

    assert len(chunks) > 1
    # Every chunk should respect the max size.
    assert all(len(c.text) <= 100 for c in chunks)
    # Indices should be sequential starting at 0.
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_invalid_chunk_settings_raise():
    with pytest.raises(ValueError):
        TextChunker(chunk_size=0, chunk_overlap=0)
    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, chunk_overlap=100)
