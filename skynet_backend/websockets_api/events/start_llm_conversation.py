import logging

from pyrate_limiter import Duration, Rate

from skynet_backend.core.models.llm_conversation import (
    LlmConversationMessage,
    LlmConversationPreferences,
)
from skynet_backend.websockets_api.config import websockets_api_config
from skynet_backend.websockets_api.socketio_server import socketio_server
from skynet_backend.websockets_api.utils.dependencies import ApiSocketioSession
from skynet_backend.websockets_api.utils.socketio import (
    socketio_event_handler,
    socketio_ip_rate_limit,
)
from skynet_backend.websockets_api.utils.event_data_validation import (
    validate_and_get_event_data,
)


logger = logging.getLogger(__name__)


@socketio_event_handler
@socketio_ip_rate_limit(Rate(limit=1, interval=Duration.DAY))
async def handle_start_llm_conversation(
    connection_id: str, session: ApiSocketioSession, data
):
    preferences = validate_and_get_event_data(data, LlmConversationPreferences)

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

    await session["dependencies"].llm_conversation_service.start_llm_conversation(
        handle_new_message=send_new_llm_message_to_client,
        preferences=preferences,
        proxy_url=websockets_api_config.proxy_url,
    )

    await socketio_server.emit("llm-conversation-end", to=connection_id)

    await socketio_server.disconnect(connection_id)
