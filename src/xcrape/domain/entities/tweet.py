from __future__ import annotations

from dataclasses import dataclass

from xcrape.domain.value_objects.tweet_id import TweetId


@dataclass
class Tweet:
    id: TweetId
    keyword: str
    tweet_link: str
    text: str
    user_name: str
    username: str
    user_verified: bool
    user_is_blue_verified: bool
    user_followers_count: int

    def telegram_text(self) -> str:
        verified = "✅ " if (self.user_verified or self.user_is_blue_verified) else ""
        followers = f"{self.user_followers_count:,}"
        return (
            f"🔔 *{self.keyword}*\n"
            f"👤 *{self.user_name}* (@{self.username}) · {verified}{followers} followers\n\n"
            f"{self.text}\n\n"
            f"🔗 {self.tweet_link}"
        )
