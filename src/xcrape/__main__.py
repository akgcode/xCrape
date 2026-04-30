from __future__ import annotations

import asyncio
import logging

from xcrape.application.use_cases.fetch_and_notify import FetchAndNotifyUseCase
from xcrape.infrastructure.api_clients.scrapebadger import ScrapeBadgerHttpClient
from xcrape.infrastructure.api_clients.telegram import TelegramBotMessenger
from xcrape.infrastructure.persistence.repositories import AsyncTweetRepository
from xcrape.infrastructure.persistence.session import make_session_factory
from xcrape.infrastructure.scheduler.jobs import build_scheduler
from xcrape.shared.config import AppConfig, load_config


def make_job(config: AppConfig, scraper: ScrapeBadgerHttpClient, messenger: TelegramBotMessenger):
    session_factory = make_session_factory(config.database_url)

    async def job() -> None:
        async with session_factory() as session:
            repository = AsyncTweetRepository(session)
            use_case = FetchAndNotifyUseCase(
                client=scraper,
                messenger=messenger,
                repository=repository,
                config=config,
            )
            await use_case.execute()

    return job


async def main() -> None:
    config = load_config()

    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    async with (
        ScrapeBadgerHttpClient(config.scrapebadger_api_key) as scraper,
        TelegramBotMessenger(config.telegram_bot_token) as messenger,
    ):
        job = make_job(config, scraper, messenger)
        scheduler = build_scheduler(job, config)
        scheduler.start()

        try:
            await asyncio.Event().wait()
        finally:
            scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
