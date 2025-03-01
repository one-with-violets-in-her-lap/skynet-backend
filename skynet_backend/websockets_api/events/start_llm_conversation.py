import logging

from skynet_backend.core.models.llm_message import LlmMessageWithSpeech
from skynet_backend.websockets_api.dependencies import (
    initialize_api_dependencies,
)
from skynet_backend.websockets_api.socketio_server import socketio_server


logger = logging.getLogger(__name__)


async def handle_start_llm_conversation(sid: str, _):
    async with initialize_api_dependencies() as api_dependencies:
        async def send_new_llm_message_to_client(new_llm_message: LlmMessageWithSpeech):
            await socketio_server.emit(
                "new-llm-message",
                data=(
                    new_llm_message.speech_audio_data,
                    new_llm_message.model_dump(exclude={"speech_audio_data"}),
                ),
            )

        logger.info("LLM conversation start event with sid: %s", sid)

        await api_dependencies.llm_conversation_service.start_llm_conversation(
            send_new_llm_message_to_client
        )

        await socketio_server.emit("llm-conversation-end")
