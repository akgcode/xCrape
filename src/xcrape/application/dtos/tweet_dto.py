from __future__ import annotations

from pydantic import BaseModel


class TweetDTO(BaseModel):
    model_config = {"extra": "ignore"}

    id: str
    text: str
    username: str
    user_name: str
    user_verified: bool
    user_is_blue_verified: bool
    user_followers_count: int


class TweetBatchResponseDTO(BaseModel):
    model_config = {"extra": "ignore"}

    data: list[TweetDTO]
