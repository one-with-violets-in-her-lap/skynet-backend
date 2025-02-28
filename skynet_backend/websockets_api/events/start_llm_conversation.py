import logging

from skynet_backend.core.models.llm_message import LlmMessage
from skynet_backend.websockets_api.dependencies import (
    initialize_api_dependencies,
)
from skynet_backend.websockets_api.socketio_server import socketio_server


logger = logging.getLogger(__name__)


async def handle_start_llm_conversation(sid: str, data):
    logger.info("LLM conversation start event with sid: %s", sid)

    app_dependencies = initialize_api_dependencies()

    llm_message = await app_dependencies.llm_speech_service.get_llm_speech_reply(
        [LlmMessage(role="user", content="What is a horizon?")]
    )

    await socketio_server.emit("new-llm-message", data=llm_message.model_dump())
