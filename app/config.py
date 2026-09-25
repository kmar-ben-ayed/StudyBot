"""
Central configuration for StudyBot.

All configuration is loaded from environment variables (via a .env file in
development). Keeping configuration in one place makes it  easy for students to see exactly what the bot needs
to run.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load variables from a .env file if present. This is a no-op in production
# environments where the variables are already set (e.g. Docker, CI).
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass
class Settings:
    # --- Discord ---
    discord_token: Optional[str]

    # --- Hugging Face (chat / text generation) ---
    hf_api_key: Optional[str]
    hf_model: str

    # --- sentence-transformers (local embeddings, no key needed) ---
    embedding_model: str

    # --- RAG ---
    chunk_size: int
    chunk_overlap: int
    top_k: int

    # --- Misc ---
    log_level: str

    @property
    def has_discord_token(self) -> bool:
        return bool(self.discord_token)

    @property
    def has_hf_key(self) -> bool:
        return bool(self.hf_api_key)


def load_settings() -> Settings:
    """
    Build a Settings object from environment variables.

    This function never raises for *missing* keys — the bot should still be
    importable and testable without any secrets configured. Instead, callers
    check `has_discord_token` / `has_hf_key` and fail gracefully at the point
    where the missing value is actually needed. Embeddings never need a key
    at all, since sentence-transformers runs locally.
    """
    return Settings(
        discord_token=os.getenv("DISCORD_TOKEN") or None,
        hf_api_key=os.getenv("HF_API_KEY") or None,
        hf_model=os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        top_k=int(os.getenv("RAG_TOP_K", "4")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


settings = load_settings()
