from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from xcrape.application.use_cases.fetch_and_notify import FetchAndNotifyUseCase
from xcrape.domain.entities.tweet import Tweet
from xcrape.domain.exceptions import TelegramDeliveryError
from xcrape.domain.value_objects.tweet_id import TweetId
from xcrape.shared.config import AppConfig, SchedulerConfig, SearchConfig


def make_config(keywords: list[str] | None = None) -> AppConfig:
    return AppConfig(
        database_url="postgresql+asyncpg://x",
        scrapebadger_api_key="key",
        telegram_bot_token="token",
        telegram_chat_id="-100",
        log_level="INFO",
        search=SearchConfig(
            keywords=keywords or ["gold"],
            count=5,
            query_type="Top",
        ),
        scheduler=SchedulerConfig(interval_hours=4),
    )


def make_tweet(tweet_id: str = "1") -> Tweet:
    return Tweet(id=TweetId(tweet_id), keyword="gold", tweet_link=f"https://t.co/{tweet_id}")


async def test_fetch_and_notify_use_case_all_new_tweets_sends_and_marks_sent():
    client = AsyncMock()
    messenger = AsyncMock()
    repository = AsyncMock()

    tweets = [make_tweet("1"), make_tweet("2")]
    client.fetch_tweets.return_value = tweets
    repository.exists.return_value = False

    use_case = FetchAndNotifyUseCase(client, messenger, repository, make_config())
    await use_case.execute()

    assert messenger.send_message.call_count == 2
    assert repository.mark_sent.call_count == 2


async def test_fetch_and_notify_use_case_all_duplicate_tweets_does_nothing():
    client = AsyncMock()
    messenger = AsyncMock()
    repository = AsyncMock()

    client.fetch_tweets.return_value = [make_tweet("1"), make_tweet("2")]
    repository.exists.return_value = True

    use_case = FetchAndNotifyUseCase(client, messenger, repository, make_config())
    await use_case.execute()

    messenger.send_message.assert_not_called()
    repository.mark_sent.assert_not_called()


async def test_fetch_and_notify_use_case_partial_duplicates_sends_only_new():
    client = AsyncMock()
    messenger = AsyncMock()
    repository = AsyncMock()

    client.fetch_tweets.return_value = [make_tweet("1"), make_tweet("2"), make_tweet("3")]
    repository.exists.side_effect = [True, False, True]

    use_case = FetchAndNotifyUseCase(client, messenger, repository, make_config())
    await use_case.execute()

    assert messenger.send_message.call_count == 1
    assert repository.mark_sent.call_count == 1


async def test_fetch_and_notify_use_case_telegram_failure_does_not_mark_sent():
    client = AsyncMock()
    messenger = AsyncMock()
    repository = AsyncMock()

    client.fetch_tweets.return_value = [make_tweet("1")]
    repository.exists.return_value = False
    messenger.send_message.side_effect = TelegramDeliveryError("fail")

    use_case = FetchAndNotifyUseCase(client, messenger, repository, make_config())

    with pytest.raises(TelegramDeliveryError):
        await use_case.execute()

    repository.mark_sent.assert_not_called()


async def test_fetch_and_notify_use_case_processes_each_keyword():
    client = AsyncMock()
    messenger = AsyncMock()
    repository = AsyncMock()

    client.fetch_tweets.return_value = []
    config = make_config(keywords=["gold", "silver", "XAUUSD"])

    use_case = FetchAndNotifyUseCase(client, messenger, repository, config)
    await use_case.execute()

    assert client.fetch_tweets.call_count == 3
    calls = [call.kwargs["keyword"] for call in client.fetch_tweets.call_args_list]
    assert calls == ["gold", "silver", "XAUUSD"]
