import logging

from skynet_backend.core.models.llm_conversation import LlmConversationMessage
from skynet_backend.websockets_api.dependencies import (
    get_api_dependencies_for_connection,
)
from skynet_backend.websockets_api.error_handling import (
    handle_and_send_errors_to_socketio_client,
)
from skynet_backend.websockets_api.socketio_server import socketio_server


logger = logging.getLogger(__name__)


@handle_and_send_errors_to_socketio_client
async def handle_start_llm_conversation(connection_id: str, _=None):
    api_dependencies = await get_api_dependencies_for_connection(connection_id)

    async def send_new_llm_message_to_client(new_llm_message: LlmConversationMessage):
        await socketio_server.emit(
            "new-llm-message",
            data=(
                new_llm_message.model_dump(exclude={"speech_audio_data"}),
                new_llm_message.speech_audio_data,
            ),
            to=connection_id,
        )

    logger.info("LLM conversation start event with sid: %s", connection_id)

    await api_dependencies.llm_conversation_service.start_llm_conversation(
        send_new_llm_message_to_client,
    )

    await socketio_server.emit("llm-conversation-end", to=connection_id)

    await socketio_server.disconnect(connection_id)
