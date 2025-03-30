from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


ConversationParticipantModelName = Literal["model-1", "model-2"]


def get_opposite_model_name(
    current_talking_model_name: ConversationParticipantModelName,
) -> ConversationParticipantModelName:
    if current_talking_model_name == "model-1":
        return "model-2"
    else:
        return "model-1"


class LlmConversationMessage(BaseModel):
    """A message from a conversation between two AI models"""

    from_which_model: ConversationParticipantModelName
    content: str
    speech_audio_data: bytes


class LlmConversationPreferences(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    let_know_they_talk_with_ai: bool = False
    """Flag option that lets LLM bots know they are talking with AI like themselves"""
