import logging

from skynet_backend.core.models.llm_message import LlmMessageWithSpeech
from skynet_backend.websockets_api.dependencies import (
    initialize_api_dependencies,
)
from skynet_backend.websockets_api.socketio_server import socketio_server


logger = logging.getLogger(__name__)


async def handle_start_llm_conversation(sid: str, _):
    async def send_new_llm_message_to_client(new_llm_message: LlmMessageWithSpeech):
        await socketio_server.emit("new-llm-message", data=new_llm_message.model_dump())

    logger.info("LLM conversation start event with sid: %s", sid)

    app_dependencies = initialize_api_dependencies()

    await app_dependencies.llm_conversation_service.start_llm_conversation(
        send_new_llm_message_to_client
    )

    await socketio_server.emit("llm-conversation-end")
