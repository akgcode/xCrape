from __future__ import annotations

import os
from dataclasses import dataclass

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class SearchConfig:
    keywords: list[str]
    count: int
    query_type: str


@dataclass(frozen=True)
class SchedulerConfig:
    interval_hours: int


@dataclass(frozen=True)
class AppConfig:
    database_url: str
    scrapebadger_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    log_level: str
    search: SearchConfig
    scheduler: SchedulerConfig


def load_config(env_path: str = ".env", yaml_path: str | None = None) -> AppConfig:
    load_dotenv(env_path, override=False)

    if yaml_path is None:
        yaml_path = os.getenv("CONFIG_PATH", "config.yaml")

    with open(yaml_path) as f:
        raw = yaml.safe_load(f)

    search_raw = raw["search"]
    scheduler_raw = raw["scheduler"]

    def _require(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    return AppConfig(
        database_url=_require("DATABASE_URL"),
        scrapebadger_api_key=_require("SCRAPEBADGER_API_KEY"),
        telegram_bot_token=_require("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=_require("TELEGRAM_CHAT_ID"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        search=SearchConfig(
            keywords=search_raw["keywords"],
            count=int(search_raw["count"]),
            query_type=search_raw["query_type"],
        ),
        scheduler=SchedulerConfig(
            interval_hours=int(scheduler_raw["interval_hours"]),
        ),
    )
