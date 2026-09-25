"""
Small helpers for formatting bot output for Discord's constraints.
"""
from __future__ import annotations

from typing import List

DISCORD_MESSAGE_LIMIT = 2000


def split_for_discord(text: str, limit: int = DISCORD_MESSAGE_LIMIT) -> List[str]:
    """
    Split a long message into chunks under Discord's per-message character
    limit, preferring to break on paragraph/line boundaries so chunks stay
    readable.
    """
    if len(text) <= limit:
        return [text] if text else []

    chunks: List[str] = []
    remaining = text

    while len(remaining) > limit:
        split_at = remaining.rfind("\n\n", 0, limit)
        if split_at == -1:
            split_at = remaining.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at <= 0:
            split_at = limit

        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()

    if remaining:
        chunks.append(remaining)

    return chunks
