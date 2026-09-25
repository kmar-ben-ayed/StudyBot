"""
Retriever: turns a natural-language question into relevant text chunks.

Separated from RAGService so it can be unit tested with a fake vector store
and a fake embedding service, with no network calls at all.
"""
from __future__ import annotations

from typing import List

from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import SearchResult, VectorStore

# Chunks with a distance above this threshold are considered "not relevant
# enough" and are filtered out. Cosine distance ranges roughly 0 (identical)
# to 2 (opposite). This is intentionally generous for a teaching demo.
DEFAULT_MAX_DISTANCE = 1.2


class Retriever:
    def __init__(self, vector_store: VectorStore, embedding_service: EmbeddingService):
        self._vector_store = vector_store
        self._embeddings = embedding_service

    def retrieve(
        self, question: str, top_k: int = 4, max_distance: float = DEFAULT_MAX_DISTANCE
    ) -> List[SearchResult]:
        if self._vector_store.count() == 0:
            return []

        [query_vector] = self._embeddings.embed_texts([question])
        results = self._vector_store.query(query_vector, top_k=top_k)
        
        print(f"\nQUESTION: {question}")
        print(f"RESULTS FOUND: {len(results)}")

        for i, r in enumerate(results):
            print(f"\n--- RESULT {i + 1} ---")
            print(f"Distance: {r.distance}")
            print(f"Text: {r.text[:500]}")

        return results