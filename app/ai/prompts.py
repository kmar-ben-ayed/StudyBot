"""
Prompt templates used across the bot.

Keeping prompts in one file makes it easy for workshop attendees to see
"prompt engineering" as a distinct, editable concern rather than something
buried inside business logic.
"""
from __future__ import annotations

from typing import List

SYSTEM_GENERAL = (
    "You are StudyBot, a friendly and concise AI study assistant for "
    "university students. Answer clearly and keep responses focused. "
    "If you are unsure, say so instead of making things up."
)

SYSTEM_RAG = (
    "You are StudyBot, an AI study assistant. Answer the student's question "
    "using ONLY the provided course material context. If the context does "
    "not contain enough information to answer, clearly say that the course "
    "material does not cover it, instead of guessing."
)


def build_general_prompt(question: str) -> List[dict]:
    return [
        {"role": "system", "content": SYSTEM_GENERAL},
        {"role": "user", "content": question},
    ]


def build_rag_prompt(question: str, context_chunks: List[str]) -> List[dict]:
    context_block = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no context found)"
    user_content = (
        f"Course material excerpts:\n\n{context_block}\n\n"
        f"Student question: {question}\n\n"
        "Answer using only the excerpts above."
    )
    return [
        {"role": "system", "content": SYSTEM_RAG},
        {"role": "user", "content": user_content},
    ]


def build_summary_prompt(context_chunks: List[str]) -> List[dict]:
    context_block = "\n\n---\n\n".join(context_chunks)
    user_content = (
        "Summarize the following course material excerpts into a clear, "
        "well-organized study summary using short paragraphs or bullet "
        f"points:\n\n{context_block}"
    )
    return [
        {"role": "system", "content": SYSTEM_RAG},
        {"role": "user", "content": user_content},
    ]


def build_quiz_prompt(context_chunks: List[str], num_questions: int = 5) -> List[dict]:
    context_block = "\n\n---\n\n".join(context_chunks)
    user_content = (
        f"Based only on the course material excerpts below, write {num_questions} "
        "multiple-choice quiz questions (4 options each, mark the correct one "
        "with a leading '(correct)'). Number the questions. Keep it beginner-"
        f"friendly.\n\nExcerpts:\n\n{context_block}"
    )
    return [
        {"role": "system", "content": SYSTEM_RAG},
        {"role": "user", "content": user_content},
    ]


def build_flashcards_prompt(context_chunks: List[str], num_cards: int = 6) -> List[dict]:
    context_block = "\n\n---\n\n".join(context_chunks)
    user_content = (
        f"Based only on the course material excerpts below, create {num_cards} "
        "flashcards. Format each one exactly as:\n"
        "Q: <question>\nA: <answer>\n\n"
        f"Excerpts:\n\n{context_block}"
    )
    return [
        {"role": "system", "content": SYSTEM_RAG},
        {"role": "user", "content": user_content},
    ]
