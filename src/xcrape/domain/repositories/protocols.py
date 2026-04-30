from __future__ import annotations

from typing import Protocol

from xcrape.domain.value_objects.tweet_id import TweetId


class TweetRepository(Protocol):
    async def exists(self, tweet_id: TweetId) -> bool:
        ...

    async def mark_sent(self, tweet_id: TweetId, keyword: str) -> None:
        ...


class ScrapeBadgerClient(Protocol):
    async def fetch_tweets(self, keyword: str, count: int, query_type: str) -> list:
        ...


class TelegramMessenger(Protocol):
    async def send_message(self, chat_id: str, text: str) -> None:
        ...
