import logging

from skynet_backend.core.models.llm_message import LlmMessageWithSpeech
from skynet_backend.websockets_api.dependencies import (
    get_api_dependencies_for_connection,
)
from skynet_backend.websockets_api.socketio_server import socketio_server


logger = logging.getLogger(__name__)


async def handle_start_llm_conversation(connection_id: str, _=None):
    api_dependencies = await get_api_dependencies_for_connection(connection_id)

    async def send_new_llm_message_to_client(new_llm_message: LlmMessageWithSpeech):
        await socketio_server.emit(
            "new-llm-message",
            data=(
                new_llm_message.speech_audio_data,
                new_llm_message.model_dump(exclude={"speech_audio_data"}),
            ),
            to=connection_id,
        )

    logger.info("LLM conversation start event with sid: %s", connection_id)

    await api_dependencies.llm_conversation_service.start_llm_conversation(
        send_new_llm_message_to_client,
    )
    await socketio_server.emit("llm-conversation-end", to=connection_id)
