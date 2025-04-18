import logging
import g4f
import timeit

from skynet_backend.api_clients.responsive_voice.client import ResponsiveVoiceClient
from skynet_backend.common_errors import ExternalApiError
from skynet_backend.core.models.llm_conversation import ConversationParticipantModelName
from skynet_backend.core.models.llm_message import LlmMessage, LlmMessageWithSpeech


logger = logging.getLogger(__name__)


class LlmSpeechService:
    def __init__(
        self,
        g4f_client: g4f.AsyncClient,
        responsive_voice_client: ResponsiveVoiceClient,
    ):
        self.g4f_client = g4f_client
        self.responsive_voice_client = responsive_voice_client

    async def get_llm_speech_reply(
        self,
        message_history: list[LlmMessage],
        talking_model_name: ConversationParticipantModelName,
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

        speech_audio_data = await self.responsive_voice_client.fetch_speech_from_text(
            message.content,
            gender="female" if talking_model_name == "model-1" else "male",
        )

        seconds_spent_on_text_to_speech = (
            timeit.default_timer() - text_to_speech_start_time_seconds
        )

        logger.info(
            "TTS API request took %s seconds", f"{seconds_spent_on_text_to_speech:.2f}"
        )

        return LlmMessageWithSpeech(
            role=message.role,
            content=message.content,
            speech_audio_data=speech_audio_data,
        )
