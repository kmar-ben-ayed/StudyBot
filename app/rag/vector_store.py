"""
VectorStore: a thin wrapper around a local ChromaDB persistent collection.

ChromaDB stores everything on disk under `data/vector_store/`, so students
can index a document once and reuse it across bot restarts without any
external database server.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import chromadb


@dataclass
class SearchResult:
    text: str
    distance: float
    metadata: dict


class VectorStore:
    COLLECTION_NAME = "studybot_material"

    def __init__(self, persist_dir: str | Path):
        self._persist_dir = Path(persist_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._persist_dir))
        self._collection = self._client.get_or_create_collection(self.COLLECTION_NAME)

    def reset(self) -> None:
        """Delete all indexed content (used before re-ingesting a document)."""
        self._client.delete_collection(self.COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(self.COLLECTION_NAME)

    def add(
        self,
        ids: Sequence[str],
        texts: Sequence[str],
        embeddings: Sequence[List[float]],
        source: str,
    ) -> None:
        if not ids:
            return
        metadatas = [{"source": source} for _ in ids]
        self._collection.add(
            ids=list(ids),
            documents=list(texts),
            embeddings=list(embeddings),
            metadatas=metadatas,
        )

    def count(self) -> int:
        return self._collection.count()

    def query(self, query_embedding: List[float], top_k: int = 4) -> List[SearchResult]:
        if self.count() == 0:
            return []
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.count()),
        )
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        return [
            SearchResult(text=doc, distance=dist, metadata=meta or {})
            for doc, dist, meta in zip(documents, distances, metadatas)
        ]
