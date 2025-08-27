import re
from typing import Literal

import httpx

from skynet_backend.common.api_clients.fake_user_agent import FAKE_USER_AGENT
from skynet_backend.common.errors import ExternalApiError, NotFoundError

_RESPONSIVE_VOICE_API_BASE_URL = "https://texttospeech.responsivevoice.org/v1"
_RESPONSIVE_VOICE_WEBSITE_URL = "https://responsivevoice.org"


class ResponsiveVoiceClient:
    async def __aenter__(self):
        httpx_transport_with_retries = httpx.AsyncHTTPTransport(retries=3)
        self.httpx_client = httpx.AsyncClient(
            headers={
                "user-agent": FAKE_USER_AGENT,
                "referer": "https://responsivevoice.org/",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.7",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "i",
                "range": "bytes=0-",
                "sec-ch-ua": '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Linux"',
                "sec-fetch-dest": "audio",
                "sec-fetch-mode": "no-cors",
                "sec-fetch-site": "same-site",
                "sec-gpc": "1",
            },
            transport=httpx_transport_with_retries,
        )

        return self

    async def __aexit__(self, *args):
        await self.httpx_client.aclose()

    async def fetch_speech_from_text(
        self, text: str, gender: Literal["male", "female"]
    ):
        response = await self.httpx_client.get(
            _RESPONSIVE_VOICE_API_BASE_URL + "/text:synthesize",
            params={
                "text": text,
                "lang": "en-US",
                "engine": "g1",
                "name": "",
                "pitch": 0.5,
                "rate": 0.5,
                "volume": 1,
                "key": await self._fetch_key(),  # Publicly available )
                "gender": gender,
            },
            timeout=None,
        )

        print(response.request.url)

        if response.is_error:
            raise ExternalApiError(
                response.status_code,
                f"ResponsiveVoice API returned an error: {response.text}",
            )

        return response.read()

    async def _fetch_key(self):
        response = await self.httpx_client.get(
            _RESPONSIVE_VOICE_WEBSITE_URL,
            timeout=12,
        )

        keys = re.findall("[?&]key=([A-Za-z0-9]+)", response.text)

        if len(keys) == 0:
            raise NotFoundError(
                "Key cannot be found in responsive voice  website's html code: "
                + response.text
            )

        return keys[0].replace("'", "").replace('"', "")
