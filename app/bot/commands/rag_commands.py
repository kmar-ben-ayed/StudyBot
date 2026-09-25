"""
RAG-powered study commands: /document, /summary, /quiz, /flashcards.

/document lets a user attach a PDF directly in Discord to ingest it, so the
workshop doesn't strictly require running the CLI ingestion command (though
that remains available and is what the README teaches first).
"""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from app.config import ConfigError
from app.utils.discord_helpers import split_for_discord

logger = logging.getLogger(__name__)


class RAGCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="document", description="Upload and index a PDF as course material")
    @app_commands.describe(file="A PDF file to index")
    async def document(self, interaction: discord.Interaction, file: discord.Attachment):
        state = self.bot.state

        if not file.filename.lower().endswith(".pdf"):
            await interaction.response.send_message("⚠️ Please upload a `.pdf` file.")
            return

        # Note: indexing needs no HF key at all — embeddings run locally via
        # sentence-transformers. Only /ask, /summary, /quiz, /flashcards need
        # HF_API_KEY, since those generate text.
        await interaction.response.defer(thinking=True)

        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = Path(tmp_dir) / file.filename
            await file.save(local_path)

            try:
                stats = state.rag_service.ingest(local_path)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error ingesting document")
                await interaction.followup.send(f"⚠️ Could not index that document: {exc}")
                return

        await interaction.followup.send(
            "**Document indexed!**\n"
            f"- Pages: {stats['num_pages']}\n"
            f"- Chunks: {stats['num_chunks']}\n"
            "You can now use `/ask`, `/summary`, `/quiz`, and `/flashcards`."
        )

    async def _get_context_or_warn(self, interaction: discord.Interaction) -> list[str] | None:
        state = self.bot.state
        if not state.rag_service.has_indexed_material():
            await interaction.followup.send(
                "No course material has been indexed yet. Use `/document` to upload a PDF first."
            )
            return None
        chunks = state.rag_service.get_context("overview of the material", top_k=state.settings.top_k)
        if not chunks:
            await interaction.followup.send(
                "I couldn't find relevant content in the indexed material."
            )
            return None
        return chunks

    @app_commands.command(name="summary", description="Summarize the indexed course material")
    async def summary(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        state = self.bot.state
        chunks = await self._get_context_or_warn(interaction)
        if chunks is None:
            return
        try:
            text = state.ai_service.summarize(chunks)
        except ConfigError as exc:
            await interaction.followup.send(f"⚠️ {exc}")
            return
        reply = f"**Study summary**\n\n{text}"
        await self._send_long(interaction, reply)

    @app_commands.command(name="quiz", description="Generate a 5-question quiz from the course material")
    async def quiz(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        state = self.bot.state
        chunks = await self._get_context_or_warn(interaction)
        if chunks is None:
            return
        try:
            text = state.ai_service.generate_quiz(chunks, num_questions=5)
        except ConfigError as exc:
            await interaction.followup.send(f"⚠️ {exc}")
            return
        reply = f"**Quiz time!**\n\n{text}"
        await self._send_long(interaction, reply)

    @app_commands.command(name="flashcards", description="Generate flashcards from the course material")
    async def flashcards(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        state = self.bot.state
        chunks = await self._get_context_or_warn(interaction)
        if chunks is None:
            return
        try:
            text = state.ai_service.generate_flashcards(chunks, num_cards=6)
        except ConfigError as exc:
            await interaction.followup.send(f"⚠️ {exc}")
            return
        reply = f" **Flashcards**\n\n{text}"
        await self._send_long(interaction, reply)

    @staticmethod
    async def _send_long(interaction: discord.Interaction, text: str):
        parts = split_for_discord(text)
        for i, part in enumerate(parts):
            if i == 0:
                await interaction.followup.send(part)
            else:
                await interaction.channel.send(part)
