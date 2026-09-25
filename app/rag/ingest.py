"""
Command-line entry point for ingesting a PDF into the vector store.

Usage:
    python -m app.rag.ingest data/sample_course.pdf

Ingestion only needs sentence-transformers (local, free, no key). No
Hugging Face key is required to index a document — only /ask, /summary,
/quiz and /flashcards need HF_API_KEY, since those generate text.
"""
from __future__ import annotations

import sys

from app.config import settings, VECTOR_STORE_DIR
from app.rag.chunker import TextChunker
from app.rag.embeddings import EmbeddingService
from app.rag.loader import DocumentLoader
from app.rag.retriever import Retriever
from app.rag.service import RAGService
from app.rag.vector_store import VectorStore


def build_rag_service() -> RAGService:
    embedding_service = EmbeddingService(settings.embedding_model)
    vector_store = VectorStore(VECTOR_STORE_DIR)
    retriever = Retriever(vector_store, embedding_service)
    return RAGService(
        loader=DocumentLoader(),
        chunker=TextChunker(settings.chunk_size, settings.chunk_overlap),
        embedding_service=embedding_service,
        vector_store=vector_store,
        retriever=retriever,
    )


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: python -m app.rag.ingest <path-to-pdf>")
        return 1

    pdf_path = argv[0]
    rag_service = build_rag_service()

    print(f"Loading and indexing: {pdf_path}")
    print("(This runs a local embedding model — the first run may take a")
    print(" little longer while it downloads, then it's cached.)")
    try:
        stats = rag_service.ingest(pdf_path)
    except Exception as exc:  # noqa: BLE001 - CLI top-level, show a clean message
        print(f"Ingestion failed: {exc}")
        return 1

    print("Ingestion complete:")
    print(f"  Pages extracted:   {stats['num_pages']}")
    print(f"  Characters:        {stats['num_characters']}")
    print(f"  Chunks created:    {stats['num_chunks']}")
    print(f"  Embeddings made:   {stats['num_embeddings']}")
    print(f"  Vector store dir:  {VECTOR_STORE_DIR}")
    print("Successfully indexed! You can now use /ask, /summary, /quiz, /flashcards in Discord")
    print("(those still need HF_API_KEY set in .env, since they generate text).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
