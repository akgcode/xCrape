from __future__ import annotations

import re

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from xcrape.application.dtos.tweet_dto import TweetBatchResponseDTO, TweetDTO
from xcrape.domain.entities.tweet import Tweet
from xcrape.domain.exceptions import APIClientError
from xcrape.domain.value_objects.tweet_id import TweetId

_URL_RE = re.compile(r"https?://\S+")
_BASE_URL = "https://scrapebadger.com/v1/twitter/tweets/advanced_search"


class ScrapeBadgerHttpClient:
    def __init__(self, api_key: str) -> None:
        self._client = httpx.AsyncClient(
            headers={"x-api-key": api_key},
            timeout=30,
            verify=True,
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def fetch_tweets(self, keyword: str, count: int, query_type: str) -> list[Tweet]:
        try:
            response = await self._client.get(
                _BASE_URL,
                params={"query": keyword, "count": count, "query_type": query_type},
            )
            response.raise_for_status()
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            raise APIClientError(f"ScrapeBadger request failed: {exc}") from exc

        batch = TweetBatchResponseDTO.model_validate(response.json())
        return [_to_domain(dto, keyword) for dto in batch.data]

    async def __aenter__(self) -> ScrapeBadgerHttpClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._client.aclose()


def _to_domain(dto: TweetDTO, keyword: str) -> Tweet:
    urls = _URL_RE.findall(dto.text)
    tweet_link = urls[-1] if urls else f"https://x.com/{dto.username}/status/{dto.id}"
    return Tweet(
        id=TweetId(value=dto.id),
        keyword=keyword,
        tweet_link=tweet_link,
        text=dto.text,
        user_name=dto.user_name,
        username=dto.username,
        user_verified=dto.user_verified,
        user_is_blue_verified=dto.user_is_blue_verified,
        user_followers_count=dto.user_followers_count,
    )
