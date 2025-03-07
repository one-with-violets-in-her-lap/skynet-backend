import logging
import g4f
import httpx

from skynet_backend.api_clients.lazypy.client import LazypyTextToSpeechClient
from skynet_backend.api_clients.lazypy.models import LazypyVoice
from skynet_backend.common_errors import ExternalApiError
from skynet_backend.core.models.llm_message import LlmMessage, LlmMessageWithSpeech


logger = logging.getLogger(__name__)


class LlmSpeechService:
    def __init__(
        self,
        g4f_client: g4f.AsyncClient,
        lazypy_text_to_speech_client: LazypyTextToSpeechClient,
    ):
        self.g4f_client = g4f_client
        self.lazypy_text_to_speech_client = lazypy_text_to_speech_client

    async def get_llm_speech_reply(
        self,
        message_history: list[LlmMessage],
        text_to_speech_voice=LazypyVoice.EN_UK_003,
    ):
        response = await self.g4f_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[message.model_dump() for message in message_history],
            web_search=False,
        )

        if len(response.choices) < 1:
            raise ExternalApiError(
                detail="LLM API response is empty (no choices " + "with completions)"
            )

        message = response.choices[0].message

        logger.debug('LLM response is %s chars long', len(message.content))

        text_to_speech_result = (
            await self.lazypy_text_to_speech_client.fetch_speech_from_text(
                message.content, voice=text_to_speech_voice
            )
        )

        logger.info("Text to speech operation completed, fetching audio data...")

        speech_audio_data = await self._fetch_speech_audio_data(
            text_to_speech_result.audio_url
        )

        return LlmMessageWithSpeech(
            role=message.role,
            content=message.content,
            speech_audio_data=speech_audio_data,
        )

    async def _fetch_speech_audio_data(self, audio_file_url: str):
        async with httpx.AsyncClient() as httpx_client:
            response = await httpx_client.get(audio_file_url)

            if response.is_error:
                raise ExternalApiError(
                    status_code=response.status_code,
                    detail="Failed to fetch speech audio data from lazypy API",
                )

            return response.read()
