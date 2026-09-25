# RAG pipeline

RAG (Retrieval-Augmented Generation) lets the bot answer questions using
*your* course material instead of only what the LLM already knows. StudyBot
implements the full pipeline in `app/rag/`.

```
PDF file
   │  DocumentLoader (app/rag/loader.py)
   ▼
Cleaned plain text
   │  TextChunker (app/rag/chunker.py)
   ▼
Overlapping text chunks (~800 chars each)
   │  EmbeddingService (app/rag/embeddings.py)
   ▼
One embedding vector per chunk
   │  VectorStore.add() (app/rag/vector_store.py, backed by ChromaDB)
   ▼
Persisted local vector index (data/vector_store/)

──────────────────────────────────────────────

Student question
   │  EmbeddingService (embed the question the same way)
   ▼
Question embedding
   │  VectorStore.query() → Retriever (app/rag/retriever.py)
   ▼
Top-k most similar chunks (filtered by distance threshold)
   │  prompts.build_rag_prompt() (app/ai/prompts.py)
   ▼
"Answer using ONLY these excerpts..." prompt
   │  AIService.answer_with_context() → AIClient.chat()
   ▼
Final answer, shown in Discord as
"📘 According to your course material: ..."
```

## Key design decisions (good workshop talking points)

- **Chunking with overlap**: chunks are ~800 characters with a 120-character
  overlap, so a sentence that would otherwise get cut in half at a chunk
  boundary still appears in full in at least one chunk.
- **Local vector store**: ChromaDB persists to `data/vector_store/` on disk,
  so nobody needs to run a database server, and re-indexing is as simple as
  deleting that folder (or calling `/clear`).
- **Distance threshold**: `Retriever` discards chunks whose distance to the
  question is above a threshold, so the bot doesn't claim material "covers"
  something it doesn't. If nothing relevant is found, StudyBot honestly
  falls back to a general answer (`/ask`) or tells the student no material
  is indexed yet (`/summary`, `/quiz`, `/flashcards`).
- **Never fake the source**: the "According to your course material..."
  framing is only used when retrieval actually returned chunks — see
  `app/bot/commands/ai_commands.py`.
- **Swap the vector store or embedding model** by changing
  `EMBEDDING_MODEL` in `.env`, or by replacing `VectorStore` with a FAISS-
  backed implementation that exposes the same `add`/`query`/`count`
  interface — nothing else in the app needs to change.

## Inspecting the index

```powershell
python -m app.rag.ingest data/sample_course.pdf
```

prints page/character/chunk/embedding counts so students can see each stage
of the pipeline actually happening, not just "it worked."
