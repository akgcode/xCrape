from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from xcrape.domain.value_objects.tweet_id import TweetId
from xcrape.infrastructure.persistence.models import Base
from xcrape.infrastructure.persistence.repositories import AsyncTweetRepository


@pytest.fixture
async def session_factory(postgresql):
    url = (
        f"postgresql+asyncpg://{postgresql.info.user}:{postgresql.info.password}"
        f"@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    )
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


async def test_tweet_repository_exists_unknown_id_returns_false(session_factory):
    async with session_factory() as session:
        repo = AsyncTweetRepository(session)
        result = await repo.exists(TweetId("nonexistent"))
    assert result is False


async def test_tweet_repository_mark_sent_then_exists_returns_true(session_factory):
    async with session_factory() as session:
        repo = AsyncTweetRepository(session)
        await repo.mark_sent(TweetId("tweet-abc"), "gold")

    async with session_factory() as session:
        repo = AsyncTweetRepository(session)
        result = await repo.exists(TweetId("tweet-abc"))
    assert result is True


async def test_tweet_repository_mark_sent_different_ids_are_independent(session_factory):
    async with session_factory() as session:
        repo = AsyncTweetRepository(session)
        await repo.mark_sent(TweetId("aaa"), "gold")

    async with session_factory() as session:
        repo = AsyncTweetRepository(session)
        assert await repo.exists(TweetId("aaa")) is True
        assert await repo.exists(TweetId("bbb")) is False
