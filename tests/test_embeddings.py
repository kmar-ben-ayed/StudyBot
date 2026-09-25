from app.rag.embeddings import EmbeddingService


def test_embed_texts_empty_list_returns_empty(fake_encoder):
    service = EmbeddingService(encoder=fake_encoder)
    assert service.embed_texts([]) == []


def test_embed_texts_returns_one_vector_per_text(fake_encoder):
    service = EmbeddingService(encoder=fake_encoder)
    vectors = service.embed_texts(["hello", "world"])
    assert len(vectors) == 2
    assert all(isinstance(v, list) for v in vectors)


def test_embed_texts_is_deterministic(fake_encoder):
    service = EmbeddingService(encoder=fake_encoder)
    v1 = service.embed_texts(["same text"])
    v2 = service.embed_texts(["same text"])
    assert v1 == v2


def test_is_ready_is_always_true_no_key_needed(fake_encoder):
    service = EmbeddingService(encoder=fake_encoder)
    assert service.is_ready is True
