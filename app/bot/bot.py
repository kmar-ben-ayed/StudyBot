"""
StudyBot: the Discord bot entry point.

This file wires together the AI service, the RAG service, and the reminder
scheduler, and exposes them on `bot.state` so command Cogs can use them
without global variables.
"""
from __future__ import annotations

import logging

import discord
from discord.ext import commands

from app.ai.client import AIClient
from app.ai.service import AIService
from app.config import Settings, VECTOR_STORE_DIR
from app.rag.chunker import TextChunker
from app.rag.embeddings import EmbeddingService
from app.rag.loader import DocumentLoader
from app.rag.retriever import Retriever
from app.rag.service import RAGService
from app.rag.vector_store import VectorStore
from app.reminders.scheduler import ReminderScheduler

logger = logging.getLogger(__name__)


class BotState:
    """Holds the shared services every command needs, built once at startup."""

    def __init__(self, settings: Settings):
        self.settings = settings

        ai_client = AIClient(settings)
        self.ai_service = AIService(ai_client)

        embedding_service = EmbeddingService(settings.embedding_model)
        vector_store = VectorStore(VECTOR_STORE_DIR)
        retriever = Retriever(vector_store, embedding_service)
        self.rag_service = RAGService(
            loader=DocumentLoader(),
            chunker=TextChunker(settings.chunk_size, settings.chunk_overlap),
            embedding_service=embedding_service,
            vector_store=vector_store,
            retriever=retriever,
        )

        self.scheduler = ReminderScheduler()


class StudyBot(commands.Bot):
    def __init__(self, settings: Settings):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.state = BotState(settings)

    async def setup_hook(self) -> None:
        from app.bot.commands.basic import BasicCommands
        from app.bot.commands.ai_commands import AICommands
        from app.bot.commands.rag_commands import RAGCommands
        from app.bot.commands.reminder_commands import ReminderCommands

        await self.add_cog(BasicCommands(self))
        await self.add_cog(AICommands(self))
        await self.add_cog(RAGCommands(self))
        await self.add_cog(ReminderCommands(self))

        self.state.scheduler.start()

        synced = await self.tree.sync()
        logger.info("Synced %d slash commands", len(synced))

    async def close(self) -> None:
        self.state.scheduler.shutdown()
        await super().close()


def create_bot(settings: Settings) -> StudyBot:
    if not settings.has_discord_token:
        raise RuntimeError(
            "DISCORD_TOKEN is not set. Add it to your .env file before starting the bot."
        )
    return StudyBot(settings)
