import json
from typing import Literal, Optional, TypedDict

import httpx

from skynet_backend.common.api_clients.fake_user_agent import FAKE_USER_AGENT
from skynet_backend.common.errors import ExternalApiError


class DeepaiLlmMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


class DeepaiClient:
    def __init__(self, proxy_url: Optional[str]):
        self.proxy_url = proxy_url

    async def __aenter__(self):
        self.httpx_client = httpx.AsyncClient(proxy=self.proxy_url)
        return self

    async def __aexit__(self, *_):
        await self.httpx_client.__aexit__()

    async def fetch_gpt_completion(self, messages: list[DeepaiLlmMessage]):
        response = await self.httpx_client.post(
            url="https://api.deepai.org/hacking_is_a_serious_crime",
            headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.6",
                "cache-control": "no-cache",
                "origin": "https://deepai.org",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Linux"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "sec-gpc": "1",
                "user-agent": FAKE_USER_AGENT,
            },
            data={
                "chat_style": "chat",
                "chatHistory": json.dumps(messages),
                "model": "standard",
                # Request must contain this field, do not ask me why
                "hacker_is_stinky": "very_stinky",
            },
            files={},
        )

        if response.is_error:
            raise ExternalApiError(
                response.status_code,
                f"Failed to fetch GPT completion from deepai.com: {response.text}",
            )

        return response.text
