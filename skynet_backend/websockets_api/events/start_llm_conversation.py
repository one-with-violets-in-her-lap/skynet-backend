import logging

from skynet_backend.core.models.llm_conversation import (
    LlmConversationMessage,
    LlmConversationPreferences,
)
from skynet_backend.websockets_api.config import websockets_api_config
from skynet_backend.websockets_api.error_handling import (
    handle_and_send_errors_to_socketio_client,
)
from skynet_backend.websockets_api.socketio_server import socketio_server
from skynet_backend.websockets_api.utils.dependencies import get_socketio_api_session
from skynet_backend.websockets_api.utils.event_data_validation import (
    validate_and_get_event_data,
)


logger = logging.getLogger(__name__)


@handle_and_send_errors_to_socketio_client
async def handle_start_llm_conversation(connection_id: str, data):
    preferences = validate_and_get_event_data(data, LlmConversationPreferences)

    socketio_session = await get_socketio_api_session(connection_id)

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

    await socketio_session[
        "dependencies"
    ].llm_conversation_service.start_llm_conversation(
        handle_new_message=send_new_llm_message_to_client,
        preferences=preferences,
        proxy_url=websockets_api_config.proxy_url,
    )

    await socketio_server.emit("llm-conversation-end", to=connection_id)

    await socketio_server.disconnect(connection_id)
