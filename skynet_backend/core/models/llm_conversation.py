from typing import Literal

from pydantic import BaseModel


ConversationParticipantModelName = Literal["model-1", "model-2"]


def get_opposite_model_name(current_talking_model_name: ConversationParticipantModelName) -> ConversationParticipantModelName:
    if current_talking_model_name == "model-1":
        return "model-2"
    else:
        return "model-1"


class LlmConversationMessage(BaseModel):
    """A message from a conversation between two AI models"""

    from_which_model: ConversationParticipantModelName
    content: str
    speech_audio_data: bytes
