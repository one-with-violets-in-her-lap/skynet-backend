from typing import Literal

from pydantic import BaseModel


class LlmMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

    def __str__(self):
        return f"{self.role}: {self.content}"


class LlmMessageWithSpeech(LlmMessage):
    speech_audio_url: str
