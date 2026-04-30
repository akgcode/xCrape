from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from xcrape.domain.exceptions import TelegramDeliveryError


class TelegramBotMessenger:
    def __init__(self, bot_token: str) -> None:
        self._token = bot_token
        self._client = httpx.AsyncClient(timeout=15, verify=True)

    @retry(wait=wait_exponential(multiplier=1, min=2, max=30), stop=stop_after_attempt(3))
    async def send_message(self, chat_id: str, text: str) -> None:
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        try:
            response = await self._client.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
            response.raise_for_status()
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            raise TelegramDeliveryError(f"Telegram delivery failed: {exc}") from exc

    async def __aenter__(self) -> TelegramBotMessenger:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._client.aclose()
