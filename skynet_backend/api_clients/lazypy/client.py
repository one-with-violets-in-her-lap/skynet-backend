import json
import logging
import urllib.parse
import httpx
import urllib

from skynet_backend.api_clients.lazypy.models import (
    LazypyTextToSpeechResult,
    LazypyTextToSpeechSuccessResult,
    LazypyVoice,
)
from skynet_backend.common_errors import ExternalApiError


_FAKE_USER_AGENT = "Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0"
_LAZYPY_API_BASE_URL = "https://lazypy.ro"
_DEFAULT_ERROR_MESSAGE = (
    "Something went wrong while generating speech from text using lazypy.ro API"
)


logger = logging.getLogger(__name__)


class LazypyTextToSpeechClient:
    async def __aenter__(self):
        httpx_transport_with_retries = httpx.AsyncHTTPTransport(retries=2)
        self.httpx_client = httpx.AsyncClient(
            base_url=_LAZYPY_API_BASE_URL, transport=httpx_transport_with_retries
        )

        return self

    async def __aexit__(self, *args):
        await self.httpx_client.aclose()

    async def fetch_speech_from_text(
        self, text: str, voice: LazypyVoice = LazypyVoice.EN_UK_003
    ):
        form_urlencoded_body = urllib.parse.urlencode(
            {"service": "TikTok", "voice": voice.value, "text": text}
        )

        response = await self.httpx_client.post(
            "/tts/request_tts.php",
            headers={
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.6",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": _LAZYPY_API_BASE_URL,
                "Referer": _LAZYPY_API_BASE_URL,
                "User-agent": _FAKE_USER_AGENT,
            },
            content=form_urlencoded_body,
            timeout=24,
        )

        if response.is_error:
            logger.error("Lazypy API returned an error. Trying to get error details...")

            error_detail = _DEFAULT_ERROR_MESSAGE

            try:
                error_detail += f". More info: {response.json()}"
            except json.JSONDecodeError:
                logger.error(
                    "Lazypy API error does not contain any info. It's just a "
                    + "4xx/5xx status code"
                )

            raise ExternalApiError(
                status_code=response.status_code, detail=error_detail
            )

        result = LazypyTextToSpeechResult.model_validate(response.json())

        if result.audio_url is None:
            error_detail = _DEFAULT_ERROR_MESSAGE

            if result.error_msg is not None:
                error_detail += f". More info: {result.error_msg}"

            raise ExternalApiError(
                status_code=response.status_code, detail=error_detail
            )

        return LazypyTextToSpeechSuccessResult.model_validate(result.model_dump())
