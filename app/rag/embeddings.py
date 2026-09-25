"""
EmbeddingService: turns text chunks into embedding vectors using
sentence-transformers, running entirely locally.

No API key, no network call, no Hugging Face involvement at all — this is
the free, offline half of the RAG pipeline. The model downloads once (a few
dozen MB) the first time it's used, then runs from a local cache.
"""
from __future__ import annotations

from typing import List, Optional, Protocol


class _Encoder(Protocol):
    """Minimal shape both the real model and test fakes need to satisfy."""

    def encode(self, texts: List[str]):
        ...


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", encoder: Optional[_Encoder] = None):
        self._model_name = model_name
        # Allow tests to inject a fake encoder so unit tests never download
        # a real model or touch the network.
        self._encoder = encoder

    def _ensure_encoder(self) -> _Encoder:
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer(self._model_name)
        return self._encoder

    @property
    def is_ready(self) -> bool:
        # Local embeddings never need an API key — always available.
        return True

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        encoder = self._ensure_encoder()
        vectors = encoder.encode(texts)
        # Real sentence-transformers returns a numpy array; fakes in tests
        # may just return plain lists.
        return vectors.tolist() if hasattr(vectors, "tolist") else list(vectors)
