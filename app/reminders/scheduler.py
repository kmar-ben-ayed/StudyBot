"""
ReminderScheduler: a small wrapper around APScheduler for one-off study
reminders.

Kept intentionally simple:
  - Time format is an explicit "HH:MM" (24h, today or tomorrow if already
    passed) — no natural-language parsing, to keep the workshop focused on
    the *concept* of background/scheduled tasks rather than parsing edge
    cases.
  - Each reminder fires once and then removes itself.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


class InvalidReminderTimeError(Exception):
    pass


@dataclass
class ReminderRequest:
    run_at: datetime
    message: str
    channel_id: int
    user_id: int


def parse_time_string(time_str: str, now: datetime | None = None) -> datetime:
    """
    Parse a "HH:MM" string into the next datetime it refers to.

    If that time has already passed today, schedule it for tomorrow instead
    — this matches how students naturally expect "set a reminder at 08:00"
    to behave when it's already 14:00.
    """
    now = now or datetime.now()
    match = TIME_RE.match(time_str.strip())
    if not match:
        raise InvalidReminderTimeError(
            f"'{time_str}' is not a valid time. Use 24h HH:MM format, e.g. 18:00."
        )

    hour, minute = int(match.group(1)), int(match.group(2))
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


class ReminderScheduler:
    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._started = False

    def start(self) -> None:
        if not self._started:
            self._scheduler.start()
            self._started = True

    def shutdown(self) -> None:
        if self._started:
            self._scheduler.shutdown(wait=False)
            self._started = False

    def schedule_reminder(self, request: ReminderRequest, callback: Callable) -> str:
        """Schedule `callback(request)` to run once at request.run_at."""
        job = self._scheduler.add_job(
            callback,
            "date",
            run_date=request.run_at,
            args=[request],
        )
        return job.id

    @property
    def jobs(self):
        return self._scheduler.get_jobs()
