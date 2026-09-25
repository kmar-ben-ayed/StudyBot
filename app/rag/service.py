"""
RAGService: the orchestration layer that ties ingestion and retrieval
together, and is what bot commands actually call.

Pipeline (document → answer):
  DocumentLoader → TextChunker → EmbeddingService → VectorStore
                                                        │
                        question ──► Retriever ─────────┘
                                        │
                                context chunks ──► AIService ──► answer
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from app.rag.chunker import TextChunker
from app.rag.embeddings import EmbeddingService
from app.rag.loader import DocumentLoader
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(
        self,
        loader: DocumentLoader,
        chunker: TextChunker,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        retriever: Retriever,
    ):
        self.loader = loader
        self.chunker = chunker
        self.embeddings = embedding_service
        self.vector_store = vector_store
        self.retriever = retriever
        self.last_ingested_source: str | None = None

    def ingest(self, path: str | Path) -> dict:
        """
        Run the full ingestion pipeline for a document and return stats that
        are useful to print/log during a workshop demo.
        """
        document = self.loader.load(path)
        chunks = self.chunker.split(document.text)

        if not chunks:
            raise ValueError("No text chunks were produced from this document.")

        texts = [c.text for c in chunks]
        embeddings = self.embeddings.embed_texts(texts)

        source_name = Path(path).name
        self.vector_store.reset()
        ids = [f"{source_name}-{c.index}" for c in chunks]
        self.vector_store.add(ids=ids, texts=texts, embeddings=embeddings, source=source_name)
        self.last_ingested_source = source_name

        stats = {
            "source": source_name,
            "num_pages": document.num_pages,
            "num_characters": document.num_characters,
            "num_chunks": len(chunks),
            "num_embeddings": len(embeddings),
        }
        logger.info("Ingested document: %s", stats)
        return stats

    def has_indexed_material(self) -> bool:
        return self.vector_store.count() > 0

    def get_context(self, question: str, top_k: int = 4) -> List[str]:
        results = self.retriever.retrieve(question, top_k=top_k)
        return [r.text for r in results]
