# Discord bot layer

## Event-driven programming

Discord bots are event-driven: your code registers handlers, and the
Discord gateway calls them when something happens (a message arrives, a
slash command is invoked, the bot connects). `app/bot/events.py` shows the
simplest examples: `on_ready` and `on_command_error`.

## Slash commands as Cogs

Each feature area is a `commands.Cog` in `app/bot/commands/`:

- `basic.py` — `/start`, `/help`, `/status`, `/clear`
- `ai_commands.py` — `/ask`
- `rag_commands.py` — `/document`, `/summary`, `/quiz`, `/flashcards`
- `reminder_commands.py` — `/remind`

Cogs are registered in `StudyBot.setup_hook()` (`app/bot/bot.py`), which
also calls `self.tree.sync()` to publish the slash commands to Discord.

## Long-running work: `defer()` + `followup`

Discord requires an interaction to be acknowledged within 3 seconds.
Anything that calls the LLM (which can take longer) uses:

```python
await interaction.response.defer(thinking=True)
...
await interaction.followup.send(reply)
```

This shows a "StudyBot is thinking..." indicator instead of the interaction
timing out.

## Respecting Discord's message length limit

Discord messages are capped at 2000 characters. `app/utils/discord_helpers.
split_for_discord()` breaks long AI output into multiple messages, splitting
on paragraph/line boundaries where possible so answers stay readable.

## Attachments for `/document`

`/document` accepts a `discord.Attachment`, saves it to a temporary file,
and passes that path straight into `RAGService.ingest()` — the same
function used by the CLI ingestion command — so there is only one ingestion
code path to explain and test.
