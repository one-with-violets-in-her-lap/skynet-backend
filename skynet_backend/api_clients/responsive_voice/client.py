from typing import Literal

import httpx

from skynet_backend.api_clients.fake_user_agent import FAKE_USER_AGENT
from skynet_backend.common_errors import ExternalApiError


_RESPONSIVE_VOICE_API_BASE_URL = "https://texttospeech.responsivevoice.org/v1"


class ResponsiveVoiceClient:
    async def __aenter__(self):
        httpx_transport_with_retries = httpx.AsyncHTTPTransport(retries=3)
        self.httpx_client = httpx.AsyncClient(
            base_url=_RESPONSIVE_VOICE_API_BASE_URL,
            headers={"User-Agent": FAKE_USER_AGENT},
            transport=httpx_transport_with_retries,
            timeout=11,
        )

        return self

    async def __aexit__(self, *args):
        await self.httpx_client.aclose()

    async def fetch_speech_from_text(
        self, text: str, gender: Literal["male", "female"]
    ):
        response = await self.httpx_client.get(
            "/text:synthesize",
            params={
                "text": text,
                "lang": "en-US",
                "engine": "g1",
                "name": "",
                "pitch": 0.5,
                "rate": 0.5,
                "volume": 1,
                "key": "kvfbSITh",  # Publicly available )
                "gender": gender,
            },
            timeout=12,
        )

        if response.is_error:
            raise ExternalApiError(
                response.status_code,
                f"ResponsiveVoice API returned an error: {response.text}",
            )

        return response.read()
