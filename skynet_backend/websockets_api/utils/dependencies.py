# TODO: use ready-to-use dependency injection library

import logging
from types import TracebackType
from typing import AsyncContextManager, Optional, TypedDict

from skynet_backend.common.api_clients.deepai_client import DeepaiClient
from skynet_backend.common.api_clients.responsive_voice.client import (
    ResponsiveVoiceClient,
)
from skynet_backend.core.services.llm_conversation_service import LlmConversationService
from skynet_backend.core.services.llm_speech_service import LlmSpeechService
from skynet_backend.websockets_api.socketio_server import socketio_server
from skynet_backend.websockets_api.config import websockets_api_config


logger = logging.getLogger(__name__)


class ApiDependencies(AsyncContextManager):
    """Initializes objects that is needed for API to function: services, utilities, etc.

    It's connection-scoped, so it is reinitialized on every new connection

    **Acts a context manager that controls all of the resources**
    """

    def __init__(self):
        self.responsive_voice_client = ResponsiveVoiceClient()

        self.llm_speech_service = LlmSpeechService(self.responsive_voice_client)
        self.llm_conversation_service = LlmConversationService(self.llm_speech_service)

        self.context_managers: list[AsyncContextManager] = [
            self.responsive_voice_client,
        ]

    async def __aenter__(self):
        for context_manager in self.context_managers:
            await context_manager.__aenter__()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ):
        for context_manager in self.context_managers:
            await context_manager.__aexit__(exc_type, exc_value, traceback)


class ApiSocketioSession(TypedDict):
    client_ip_address: str
    dependencies: ApiDependencies


async def initialize_api_dependencies_in_socketio_session(
    connection_id: str, environment
):
    logger.info("Socketio environment: %s", environment)

    dependencies = ApiDependencies()
    await dependencies.__aenter__()

    session: ApiSocketioSession = {
        "client_ip_address": environment["asgi.scope"]["client"][0],
        "dependencies": dependencies,
    }

    await socketio_server.save_session(
        connection_id,
        session,
    )


async def close_resources_on_socketio_disconnect(connection_id: str, _):
    """
    Closes dependencies with context managers (teardown) after websocket client
    disconnected
    """

    logger.info("Closing resources")

    session: ApiSocketioSession = await socketio_server.get_session(connection_id)

    await session["dependencies"].__aexit__()


async def get_socketio_api_session(connection_id: str) -> ApiSocketioSession:
    return await socketio_server.get_session(connection_id)
