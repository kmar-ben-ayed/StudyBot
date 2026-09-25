"""
Basic, non-AI slash commands: /start, /help, /status, /clear.
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

HELP_TEXT = (
    "**StudyBot Commands**\n"
    "`/start` — Welcome message and quick overview\n"
    "`/help` — Show this help message\n"
    "`/ask <question>` — Ask StudyBot anything\n"
    "`/document status:True` — Check what course material is indexed\n"
    "`/summary` — Summarize the indexed course material\n"
    "`/quiz` — Generate a 5-question quiz from the course material\n"
    "`/flashcards` — Generate flashcards from the course material\n"
    "`/remind time:HH:MM message:...` — Set a study reminder\n"
    "`/status` — Check bot/AI/RAG configuration status\n"
    "`/clear` — Clear the indexed course material\n"
)


class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="start", description="Get started with StudyBot")
    async def start(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Hi, I'm **StudyBot**! I can answer questions, summarize your "
            "course material, and generate quizzes/flashcards. Type `/help` "
            "to see everything I can do.",
        )

    @app_commands.command(name="help", description="Show available commands")
    async def help_command(self, interaction: discord.Interaction):
        await interaction.response.send_message(HELP_TEXT)

    @app_commands.command(name="status", description="Check StudyBot's configuration status")
    async def status(self, interaction: discord.Interaction):
        state = self.bot.state
        ai_ok = "AI service is ready" if state.ai_service.is_ready else "Error in AI service is detected! HF_API_KEY missing."
        indexed = state.rag_service.has_indexed_material()
        material = (
            f"({state.rag_service.vector_store.count()} chunks, "
            f"source: {state.rag_service.last_ingested_source or 'unknown'})"
            if indexed
            else "No course material is indexed yet. Run the ingest command"
        )
        await interaction.response.send_message(
            f"**StudyBot status**\nAI provider: {ai_ok}\nCourse material indexed: {material}"
        )

    @app_commands.command(name="clear", description="Clear the currently indexed course material")
    async def clear(self, interaction: discord.Interaction):
        self.bot.state.rag_service.vector_store.reset()
        self.bot.state.rag_service.last_ingested_source = None
        await interaction.response.send_message("Cleared the indexed course material.")
