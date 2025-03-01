# TODO: use ready-to-use dependency injection library

from dataclasses import dataclass
import g4f

from skynet_backend.api_clients.lazypy.client import LazypyTextToSpeechClient
from skynet_backend.core.services.llm_speech_service import LlmSpeechService


@dataclass
class AppDependencies:
    llm_speech_service: LlmSpeechService


def initialize_api_dependencies():
    return AppDependencies(
        llm_speech_service=LlmSpeechService(
            g4f_client=g4f.AsyncClient(),
            lazypy_text_to_speech_client=LazypyTextToSpeechClient(),
        )
    )
