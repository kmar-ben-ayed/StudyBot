from app.rag.chunker import TextChunker
from app.rag.embeddings import EmbeddingService
from app.rag.loader import DocumentLoader
from app.rag.retriever import Retriever
from app.rag.service import RAGService
from app.rag.vector_store import VectorStore


def build_service(fake_ai_client, tmp_vector_store_dir):
    embedding_service = EmbeddingService(fake_ai_client)
    vector_store = VectorStore(tmp_vector_store_dir)
    retriever = Retriever(vector_store, embedding_service)
    return RAGService(
        loader=DocumentLoader(),
        chunker=TextChunker(chunk_size=500, chunk_overlap=50),
        embedding_service=embedding_service,
        vector_store=vector_store,
        retriever=retriever,
    )


def test_ingest_sample_pdf_produces_stats(fake_ai_client, tmp_vector_store_dir, sample_pdf_path):
    service = build_service(fake_ai_client, tmp_vector_store_dir)

    stats = service.ingest(sample_pdf_path)

    assert stats["num_pages"] >= 1
    assert stats["num_chunks"] > 0
    assert stats["num_embeddings"] == stats["num_chunks"]
    assert service.has_indexed_material() is True


def test_get_context_returns_relevant_text(fake_ai_client, tmp_vector_store_dir, sample_pdf_path):
    service = build_service(fake_ai_client, tmp_vector_store_dir)
    service.ingest(sample_pdf_path)

    context = service.get_context("What is a deadlock?", top_k=3)
    assert isinstance(context, list)


def test_get_context_empty_before_ingest(fake_ai_client, tmp_vector_store_dir):
    service = build_service(fake_ai_client, tmp_vector_store_dir)
    assert service.has_indexed_material() is False
    assert service.get_context("anything") == []
