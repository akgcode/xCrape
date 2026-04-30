from __future__ import annotations

import pytest

from xcrape.domain.entities.tweet import Tweet
from xcrape.domain.value_objects.tweet_id import TweetId


def make_tweet(tweet_link: str = "https://t.co/abc", keyword: str = "gold") -> Tweet:
    return Tweet(id=TweetId("123"), keyword=keyword, tweet_link=tweet_link)


def test_tweet_telegram_text_returns_extracted_url():
    tweet = make_tweet(tweet_link="https://t.co/abc")
    assert tweet.telegram_text() == "https://t.co/abc"


def test_tweet_telegram_text_returns_constructed_permalink():
    tweet = make_tweet(tweet_link="https://x.com/user/status/123")
    assert tweet.telegram_text() == "https://x.com/user/status/123"


def test_tweet_id_is_used_as_identity():
    t1 = Tweet(id=TweetId("aaa"), keyword="gold", tweet_link="https://t.co/x")
    t2 = Tweet(id=TweetId("bbb"), keyword="gold", tweet_link="https://t.co/x")
    assert t1.id != t2.id
