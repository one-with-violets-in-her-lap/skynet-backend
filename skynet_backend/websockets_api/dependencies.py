# TODO: use ready-to-use dependency injection library

from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
from typing import AsyncContextManager

import g4f

from skynet_backend.api_clients.lazypy.client import LazypyTextToSpeechClient
from skynet_backend.core.services.llm_conversation_service import LlmConversationService
from skynet_backend.core.services.llm_speech_service import LlmSpeechService


logger = logging.getLogger(__name__)


@dataclass
class ApiDependencies:
    llm_speech_service: LlmSpeechService
    llm_conversation_service: LlmConversationService


@asynccontextmanager
async def initialize_api_dependencies():
    lazypy_text_to_speech_client = LazypyTextToSpeechClient()
    g4f_client = g4f.AsyncClient()

    llm_speech_service = LlmSpeechService(
        g4f_client=g4f_client,
        lazypy_text_to_speech_client=lazypy_text_to_speech_client,
    )

    llm_conversation_service = LlmConversationService(llm_speech_service)

    dependencies_with_context_managers: list[AsyncContextManager] = [
        lazypy_text_to_speech_client,
    ]

    logger.info("Initializing dependencies")

    for dependency in dependencies_with_context_managers:
        await dependency.__aenter__()

    yield ApiDependencies(
        llm_speech_service=llm_speech_service,
        llm_conversation_service=llm_conversation_service,
    )

    # Closes dependencies with context managers (teardown)
    logger.info("Closing resources")
    for dependency in dependencies_with_context_managers:
        await dependency.__aexit__(None, None, None)
