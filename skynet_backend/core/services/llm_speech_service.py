import g4f

from skynet_backend.core.errors.external_api_error import ExternalApiError
from skynet_backend.core.models.llm_message import LlmMessage


class LlmSpeechService:
    def __init__(self, g4f_client: g4f.AsyncClient):
        self.g4f_client = g4f_client

    async def get_llm_speech_reply(self, message_history: list[LlmMessage]):
        response = await self.g4f_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[message.model_dump() for message in message_history],
            web_search=False,
        )

        if len(response.choices) < 1:
            raise ExternalApiError(
                detail="LLM API response is empty (no choices " + "with completions)"
            )

        return response.choices[0].message
