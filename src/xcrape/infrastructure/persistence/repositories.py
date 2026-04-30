from __future__ import annotations

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from xcrape.domain.value_objects.tweet_id import TweetId
from xcrape.infrastructure.persistence.models import SentTweetModel


class AsyncTweetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, tweet_id: TweetId) -> bool:
        stmt = select(exists().where(SentTweetModel.id == tweet_id.value))
        result = await self._session.scalar(stmt)
        return bool(result)

    async def mark_sent(self, tweet_id: TweetId, keyword: str) -> None:
        row = SentTweetModel(id=tweet_id.value, keyword=keyword)
        self._session.add(row)
        await self._session.commit()
