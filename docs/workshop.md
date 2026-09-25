# Workshop guide — "From Bot to Brain"

A 3-hour session for 2nd-year engineering students, building StudyBot
progressively through 5 checkpoints.

## Before the workshop

- Have your own `.env` filled in and tested end-to-end (bot online,
  `/ask`, `/document` + `/summary`/`/quiz`/`/flashcards`, `/remind` all
  working) at least the day before.
- Prepare a second, empty checkpoint-1-only copy of the repo for live
  coding, or use Git tags/branches per checkpoint if you want students to
  `git checkout` between stages.
- Have `data/sample_course.pdf` pre-indexed as a fallback in case live
  ingestion has API issues during the session.
- Test your venue's Wi-Fi against your AI provider's API — this is the #1
  cause of live-demo failures.

## Presentation flow

| # | Section | Concept to explain | Code file to show | Live demo | Approx. duration | Common student questions |
|---|---|---|---|---|---|---|
| 0 | Introduction | Workshop goals, final product demo | — | Show finished bot answering a RAG question | 10 min | "Is this a real AI or scripted?" |
| 1 | What is a bot? | A program that reacts to events on a platform | `app/main.py`, `app/bot/bot.py` | Start the bot, see `on_ready` fire | 10 min | "Does the bot run 24/7?" |
| 2 | Event-driven programming | Handlers vs. polling | `app/bot/events.py` | Trigger `on_command_error` intentionally | 15 min | "What other events exist?" |
| 3 | APIs | Request/response, auth via API keys | `app/config.py` | Show `.env.example`, explain each var | 10 min | "Why not hardcode the key?" |
| 4 | Connecting an LLM | Chat completion request/response shape | `app/ai/client.py` | Call `/ask` with no material indexed | 15 min | "What's a token? Why does it cost money?" |
| 5 | Prompt engineering | System vs. user messages, instructions | `app/ai/prompts.py` | Edit `SYSTEM_GENERAL`, restart, re-ask | 15 min | "Why does wording change the answer?" |
| 6 | Why RAG? | LLMs don't know *your* course material | — (conceptual) | Ask a question about the sample PDF *before* indexing | 10 min | "Why not just paste the PDF into the prompt?" |
| 7 | RAG pipeline | End-to-end flow, overlap chunks | `app/rag/service.py`, `docs/rag.md` diagram | Walk through the diagram | 15 min | "What happens to old content when I re-index?" |
| 8 | Embeddings | Text → vectors, similarity | `app/rag/embeddings.py` | Print two embedding vectors, compare | 15 min | "Are embeddings the same as the LLM?" |
| 9 | Vector search | Nearest-neighbor retrieval, distance threshold | `app/rag/vector_store.py`, `app/rag/retriever.py` | Run `python -m app.rag.ingest`, then `/ask` the same question | 15 min | "What if no chunk is relevant?" |
| 10 | Background tasks | Scheduling without blocking the bot | `app/reminders/scheduler.py` | Set a `/remind` 1 minute in the future, wait for it to fire | 15 min | "Do reminders survive a restart?" (no — flag as an extension) |
| 11 | Final architecture | Recap all layers together | `docs/architecture.md` diagram | — | 10 min | — |
| 12 | Mini challenge | Hands-on extension | — | Students implement one feature | remaining time | — |

Total: ~3 hours including a short break after section 6.

## Final workshop challenge

Ask students to implement one or more of:

- **`/explain`** — like `/ask` but instructs the LLM (via a new prompt in
  `app/ai/prompts.py`) to explain the answer as if to a beginner, with an
  analogy.
- **`/studyplan`** — given the indexed material, ask the LLM to propose a
  day-by-day study plan; reuse `RAGService.get_context()` plus a new prompt
  builder and a new Cog command, following the same pattern as `/summary`.
- **`/summarize`** (per-message) — a context menu command that summarizes
  a specific past Discord message rather than the whole indexed document.
- **`/quiz` improvements** — let students pick the number of questions via
  a command option (`num_questions: app_commands.Range[int, 1, 10]`).
- **`/flashcards` export** — write the generated flashcards to a `.txt`
  file and send it as a Discord attachment instead of a message, using
  `discord.File`.

Each of these follows the exact same recipe already used by `/summary`:
1. Add a prompt builder in `app/ai/prompts.py`.
2. Add a method in `app/ai/service.py` (or reuse an existing one).
3. Add a slash command in the appropriate Cog under `app/bot/commands/`.
4. Add a unit test for the new prompt builder in `tests/test_prompts.py`.

## Potential problems while presenting, and how to recover

| Problem | Recovery |
|---|---|
| Venue Wi-Fi can't reach the AI provider | Switch to a pre-recorded terminal recording of the AI calls, or use a local model server if one is already running on your laptop |
| Slash commands don't appear immediately | Command sync can take a few minutes on first run; have a bot already invited and synced beforehand as a backup |
| A student's bot token was pasted into a public repo before class | Rotate it live via the Developer Portal as a teaching moment about `.gitignore` and secrets |
| Live ingestion is slow or fails mid-session | Fall back to your pre-indexed `data/vector_store/` from before the workshop |
| Rate limit hit on the shared/demo API key | Have a second backup key ready, or reduce `RAG_TOP_K`/chunk count temporarily |
| A student's Python version is too old | Have them install 3.11+ via the official installer during the break, or pair them with another student for the hands-on part |
