"""
Global Discord event handlers (not slash commands).
"""
from __future__ import annotations

import logging

from discord.ext import commands

logger = logging.getLogger(__name__)


def register_events(bot: commands.Bot) -> None:
    @bot.event
    async def on_ready():
        logger.info("Logged in as %s (id=%s)", bot.user, bot.user.id if bot.user else "?")
        print(f"StudyBot is online as {bot.user}")

    @bot.event
    async def on_command_error(ctx, error):
        logger.exception("Unhandled command error", exc_info=error)
        await ctx.send("Something went wrong running that command.")
