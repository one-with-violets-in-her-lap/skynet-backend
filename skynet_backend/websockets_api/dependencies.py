# TODO: use ready-to-use dependency injection library

from dataclasses import dataclass
import logging
from typing import AsyncContextManager

import g4f

from skynet_backend.api_clients.lazypy.client import LazypyTextToSpeechClient
from skynet_backend.core.services.llm_conversation_service import LlmConversationService
from skynet_backend.core.services.llm_speech_service import LlmSpeechService
from skynet_backend.websockets_api.socketio_server import socketio_server


logger = logging.getLogger(__name__)


@dataclass
class ApiDependencies:
    llm_speech_service: LlmSpeechService
    llm_conversation_service: LlmConversationService


async def get_api_dependencies_for_connection(connection_id: str):
    session = await socketio_server.get_session(connection_id)
    return session["dependencies"]


async def initialize_api_dependencies_in_socketio_session(connection_id: str, *_):
    lazypy_text_to_speech_client = LazypyTextToSpeechClient()
    g4f_client = g4f.AsyncClient()

    llm_speech_service = LlmSpeechService(
        g4f_client=g4f_client,
        lazypy_text_to_speech_client=lazypy_text_to_speech_client,
    )

    llm_conversation_service = LlmConversationService(llm_speech_service)

    logger.info("Initializing dependencies")

    dependencies_with_context_managers: list[AsyncContextManager] = [
        lazypy_text_to_speech_client,
    ]
    # TODO: rewrite with async `ExitStack``
    for dependency in dependencies_with_context_managers:
        await dependency.__aenter__()

    await socketio_server.save_session(
        connection_id,
        {
            "dependencies": ApiDependencies(
                llm_speech_service=llm_speech_service,
                llm_conversation_service=llm_conversation_service,
            ),
            "dependencies_with_context_managers": dependencies_with_context_managers,
        },
    )


async def close_resources_on_socketio_disconnect(connection_id: str, _):
    """
    Closes dependencies with context managers (teardown) after websocket client
    disconnected
    """

    logger.info("Closing resources")

    session = await socketio_server.get_session(connection_id)

    for dependency in session["dependencies_with_context_managers"]:
        await dependency.__aexit__(None, None, None)
