from app.rag.chunker import TextChunker
from app.rag.embeddings import EmbeddingService
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore


def test_retriever_returns_empty_when_store_is_empty(fake_ai_client, tmp_vector_store_dir):
    embedding_service = EmbeddingService(fake_ai_client)
    vector_store = VectorStore(tmp_vector_store_dir)
    retriever = Retriever(vector_store, embedding_service)

    results = retriever.retrieve("What is a deadlock?")
    assert results == []


def test_retriever_finds_indexed_chunk(fake_ai_client, tmp_vector_store_dir):
    embedding_service = EmbeddingService(fake_ai_client)
    vector_store = VectorStore(tmp_vector_store_dir)
    retriever = Retriever(vector_store, embedding_service, )

    text = "A deadlock happens when processes wait on each other forever."
    chunker = TextChunker(chunk_size=200, chunk_overlap=0)
    chunks = chunker.split(text)
    embeddings = embedding_service.embed_texts([c.text for c in chunks])

    vector_store.add(
        ids=[f"c{c.index}" for c in chunks],
        texts=[c.text for c in chunks],
        embeddings=embeddings,
        source="test.pdf",
    )

    results = retriever.retrieve(text, top_k=2, max_distance=2.0)
    assert len(results) >= 1
    assert "deadlock" in results[0].text.lower()
