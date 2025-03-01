from typing import Literal

from pydantic import BaseModel


class LlmMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class LlmMessageWithSpeech(LlmMessage):
    speech_audio_url: str
