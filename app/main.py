"""
Application entry point.

Usage:
    python -m app.main
"""
from __future__ import annotations

import logging
import sys

from app.bot.bot import create_bot
from app.bot.events import register_events
from app.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> int:
    configure_logging()

    if not settings.has_discord_token:
        print(
            "ERROR: DISCORD_TOKEN is not set.\n"
            "Create a .env file (see .env.example) with your bot token, then try again."
        )
        return 1

    if not settings.has_hf_key:
        print(
            "WARNING: HF_API_KEY is not set. The bot will start, and PDF indexing "
            "will still work (embeddings run locally), but /ask, /summary, /quiz "
            "and /flashcards will reply with a friendly configuration error until "
            "you set HF_API_KEY in your .env file."
        )

    bot = create_bot(settings)
    register_events(bot)

    bot.run(settings.discord_token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
