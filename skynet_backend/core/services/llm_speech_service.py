import logging
import os
import timeit
import uuid
import wave

import g4f
import httpx
from piper import PiperVoice

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

        logger.debug("LLM response is %s chars long", len(message.content))

        text_to_speech_start_time_seconds = timeit.default_timer()

        piper = PiperVoice.load("./en_US-lessac-medium.onnx")

        temporary_wav_file_path = f"./{uuid.uuid4()}.wav"

        with wave.open(temporary_wav_file_path, mode="w") as wav_file_stream:
            piper.synthesize(message.content, wav_file_stream)

        with open(temporary_wav_file_path, mode="rb") as wav_file_read_stream:
            speech_audio_data = wav_file_read_stream.read()

        text_to_speech_seconds_elapsed = (
            timeit.default_timer() - text_to_speech_start_time_seconds
        )

        os.remove(temporary_wav_file_path)

        logger.info(
            "Text to speech operation completed. %s seconds spent",
            str(text_to_speech_seconds_elapsed),
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
