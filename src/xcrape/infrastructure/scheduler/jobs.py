from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from xcrape.shared.config import AppConfig


def build_scheduler(
    job: Callable[[], Awaitable[None]],
    config: AppConfig,
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        job,
        IntervalTrigger(hours=config.scheduler.interval_hours),
        id="fetch_and_notify",
        replace_existing=True,
        next_run_time=datetime.now(UTC),
    )
    return scheduler
