"""
/ask — general or RAG-augmented question answering.
"""
from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from app.config import ConfigError
from app.utils.discord_helpers import split_for_discord

logger = logging.getLogger(__name__)


class AICommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ask", description="Ask StudyBot a question")
    @app_commands.describe(question="Your question")
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer(thinking=True)
        state = self.bot.state

        try:
            context_chunks = []
            if state.rag_service.has_indexed_material():
                context_chunks = state.rag_service.get_context(
                    question, top_k=state.settings.top_k
                )

            if context_chunks:
                answer = state.ai_service.answer_with_context(question, context_chunks)
                reply = f" **According to your course material:**\n\n{answer}"
            else:
                answer = state.ai_service.answer_general(question)
                reply = f"{answer}"

        except ConfigError as exc:
            await interaction.followup.send(f"⚠️ {exc}")
            return
        except Exception:
            logger.exception("Error handling /ask")
            await interaction.followup.send(
                "Sorry, something went wrong answering that question."
            )
            return

        for i, part in enumerate(split_for_discord(reply)):
            if i == 0:
                await interaction.followup.send(part)
            else:
                await interaction.channel.send(part)
