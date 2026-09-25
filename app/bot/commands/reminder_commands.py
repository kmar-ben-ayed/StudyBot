"""
/remind — schedule a one-off study reminder.
"""
from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from app.reminders.scheduler import InvalidReminderTimeError, ReminderRequest, parse_time_string

logger = logging.getLogger(__name__)


async def _fire_reminder(bot: commands.Bot, request: ReminderRequest) -> None:
    channel = bot.get_channel(request.channel_id)
    if channel is None:
        logger.warning("Reminder fired but channel %s not found", request.channel_id)
        return
    await channel.send(f" <@{request.user_id}> Study reminder: {request.message}")


class ReminderCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="remind", description="Set a study reminder (24h HH:MM)")
    @app_commands.describe(time="Time in 24h format, e.g. 18:00", message="What to remind you about")
    async def remind(self, interaction: discord.Interaction, time: str, message: str):
        try:
            run_at = parse_time_string(time)
        except InvalidReminderTimeError as exc:
            await interaction.response.send_message(f"⚠️ {exc}")
            return

        request = ReminderRequest(
            run_at=run_at,
            message=message,
            channel_id=interaction.channel_id,
            user_id=interaction.user.id,
        )

        async def callback(req: ReminderRequest):
            await _fire_reminder(self.bot, req)

        self.bot.state.scheduler.schedule_reminder(request, callback)

        await interaction.response.send_message(
            f"Reminder set for **{run_at.strftime('%Y-%m-%d %H:%M')}**: {message}"
        )
