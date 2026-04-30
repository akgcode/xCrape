from __future__ import annotations

import asyncio
import logging

from xcrape.domain.repositories.protocols import ScrapeBadgerClient, TelegramMessenger, TweetRepository
from xcrape.shared.config import AppConfig

logger = logging.getLogger(__name__)

_KEYWORD_DELAY_SECONDS = 5


class FetchAndNotifyUseCase:
    def __init__(
        self,
        client: ScrapeBadgerClient,
        messenger: TelegramMessenger,
        repository: TweetRepository,
        config: AppConfig,
    ) -> None:
        self._client = client
        self._messenger = messenger
        self._repository = repository
        self._config = config

    async def execute(self) -> None:
        for i, keyword in enumerate(self._config.search.keywords):
            if i > 0:
                await asyncio.sleep(_KEYWORD_DELAY_SECONDS)
            await self._process_keyword(keyword)

    async def _process_keyword(self, keyword: str) -> None:
        tweets = await self._client.fetch_tweets(
            keyword=keyword,
            count=self._config.search.count,
            query_type=self._config.search.query_type,
        )

        new_tweets = [t for t in tweets if not await self._repository.exists(t.id)]

        if not new_tweets:
            logger.info("No new tweets for keyword=%r", keyword)
            return

        logger.info("Found %d new tweet(s) for keyword=%r", len(new_tweets), keyword)

        for tweet in new_tweets:
            await self._messenger.send_message(self._config.telegram_chat_id, tweet.telegram_text())
            await self._repository.mark_sent(tweet.id, keyword)
            logger.info("Sent tweet id=%s for keyword=%r", tweet.id.value, keyword)
