import logging
import timeit
from typing import Optional

from open_minded import fetch_llm_completion

from skynet_backend.common.api_clients.responsive_voice.client import (
    ResponsiveVoiceClient,
)
from skynet_backend.core.models.llm_conversation import ConversationParticipantModelName
from skynet_backend.core.models.llm_message import LlmMessage, LlmMessageWithSpeech


logger = logging.getLogger(__name__)


class LlmSpeechService:
    def __init__(
        self,
        responsive_voice_client: ResponsiveVoiceClient,
    ):
        self.responsive_voice_client = responsive_voice_client

    async def get_llm_speech_reply(
        self,
        message_history: list[LlmMessage],
        talking_model_name: ConversationParticipantModelName,
        proxy_url: Optional[str] = None,
    ):
        logger.info("Fetching LLM reply with proxy %s", proxy_url)

        completion = await fetch_llm_completion(
            [
                {"content": message.content, "role": message.role}
                for message in message_history
            ]
        )

        text_to_speech_start_time_seconds = timeit.default_timer()

        speech_audio_data = await self.responsive_voice_client.fetch_speech_from_text(
            completion.result,
            gender="female" if talking_model_name == "model-1" else "male",
        )

        seconds_spent_on_text_to_speech = (
            timeit.default_timer() - text_to_speech_start_time_seconds
        )

        logger.info(
            "TTS API request took %s seconds", f"{seconds_spent_on_text_to_speech:.2f}"
        )

        return LlmMessageWithSpeech(
            role="assistant",
            content=completion.result,
            speech_audio_data=speech_audio_data,
        )
