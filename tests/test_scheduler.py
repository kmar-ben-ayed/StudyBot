from datetime import datetime

import pytest

from app.reminders.scheduler import (
    InvalidReminderTimeError,
    ReminderRequest,
    ReminderScheduler,
    parse_time_string,
)


def test_parse_time_string_future_today():
    now = datetime(2026, 1, 1, 10, 0)
    result = parse_time_string("18:00", now=now)
    assert result == datetime(2026, 1, 1, 18, 0)


def test_parse_time_string_rolls_to_tomorrow_when_passed():
    now = datetime(2026, 1, 1, 20, 0)
    result = parse_time_string("08:00", now=now)
    assert result == datetime(2026, 1, 2, 8, 0)


@pytest.mark.parametrize("bad_input", ["25:00", "not-a-time", "8:60", "18:0", ""])
def test_parse_time_string_rejects_invalid_input(bad_input):
    with pytest.raises(InvalidReminderTimeError):
        parse_time_string(bad_input)


@pytest.mark.asyncio
async def test_schedule_reminder_registers_a_job():
    # AsyncIOScheduler needs a running event loop to start, so this test is async.
    scheduler = ReminderScheduler()
    scheduler.start()
    try:
        request = ReminderRequest(
            run_at=datetime.now(),
            message="Revise chapter 3",
            channel_id=123,
            user_id=456,
        )

        async def noop_callback(_req):
            return None

        job_id = scheduler.schedule_reminder(request, noop_callback)
        assert job_id is not None
        assert any(job.id == job_id for job in scheduler.jobs)
    finally:
        scheduler.shutdown()
