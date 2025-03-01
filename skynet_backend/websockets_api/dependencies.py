# TODO: use ready-to-use dependency injection library

from dataclasses import dataclass

import g4f

from skynet_backend.api_clients.lazypy.client import LazypyTextToSpeechClient
from skynet_backend.core.services.llm_conversation_service import LlmConversationService
from skynet_backend.core.services.llm_speech_service import LlmSpeechService


@dataclass
class AppDependencies:
    llm_speech_service: LlmSpeechService
    llm_conversation_service: LlmConversationService


def initialize_api_dependencies():
    llm_speech_service = LlmSpeechService(
        g4f_client=g4f.AsyncClient(),
        lazypy_text_to_speech_client=LazypyTextToSpeechClient(),
    )

    llm_conversation_service = LlmConversationService(llm_speech_service)

    return AppDependencies(
        llm_speech_service=llm_speech_service,
        llm_conversation_service=llm_conversation_service,
    )
