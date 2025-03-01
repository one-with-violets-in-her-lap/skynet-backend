from skynet_backend.core.services.llm_speech_service import LlmSpeechService


class LlmConversationService:
    def __init__(self, llm_speech_service: LlmSpeechService):
        self.llm_speech_service = llm_speech_service
