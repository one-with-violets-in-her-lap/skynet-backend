import g4f

from skynet_backend.api_clients.lazypy.client import LazypyTextToSpeechClient
from skynet_backend.api_clients.lazypy.models import LazypyVoice
from skynet_backend.common_errors import ExternalApiError
from skynet_backend.core.models.llm_message import LlmMessage, LlmMessageWithSpeech


class LlmSpeechService:
    def __init__(
        self,
        g4f_client: g4f.AsyncClient,
        lazypy_text_to_speech_client: LazypyTextToSpeechClient,
    ):
        self.g4f_client = g4f_client
        self.lazypy_text_to_speech_client = lazypy_text_to_speech_client

    async def get_llm_speech_reply(
        self, message_history: list[LlmMessage], text_to_speech_voice=LazypyVoice.BRIAN
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

        text_to_speech_result = (
            await self.lazypy_text_to_speech_client.fetch_speech_from_text(
                message.content, voice=text_to_speech_voice
            )
        )

        return LlmMessageWithSpeech(
            role=message.role,
            content=message.content,
            speech_audio_url=text_to_speech_result.audio_url,
        )
