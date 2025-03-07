from datetime import datetime
import logging
from typing import Any, Callable, Literal

from skynet_backend.api_clients.lazypy.models import LazypyVoice
from skynet_backend.core.models.llm_conversation import (
    ConversationParticipantModelName,
    LlmConversationMessage,
    get_opposite_model_name,
)
from skynet_backend.core.models.llm_message import LlmMessage, LlmMessageWithSpeech
from skynet_backend.core.services.llm_speech_service import LlmSpeechService


ENTRYPOINT_MESSAGE = LlmMessage(
    role="user",
    content="Greet me, ask me how I am doing and let's talk about something",
)

MASTER_PROMPT = LlmMessage(
    role="system",
    content='Do not ask "Can I help you with something other?" or similar '
    + "questions. Try to maintain the conversation proactively with me. And "
    + "respond in short form, no more than 1 sentence or 2 small ones",
)


logger = logging.getLogger(__name__)


class LlmConversationService:
    def __init__(self, llm_speech_service: LlmSpeechService):
        self.llm_speech_service = llm_speech_service

    async def start_llm_conversation(
        self,
        handle_new_message: Callable[[LlmConversationMessage], Any],
        max_conversation_messages_count=10,
    ):
        conversation_id = round(datetime.now().timestamp())

        current_model_talking: ConversationParticipantModelName = "model-1"

        models_voices: dict[ConversationParticipantModelName, LazypyVoice] = {
            "model-1": LazypyVoice.EN_UK_003,
            "model-2": LazypyVoice.EN_US_010,
        }

        models_message_histories: dict[
            ConversationParticipantModelName, list[LlmMessage]
        ] = {
            "model-1": [MASTER_PROMPT, ENTRYPOINT_MESSAGE],
            "model-2": [MASTER_PROMPT],
        }

        logger.info("<%s> AI conversation started", conversation_id)

        for message_number in range(max_conversation_messages_count + 1):
            logger.info(
                "<%s> Model %s is talking", conversation_id, str(current_model_talking)
            )

            current_model_message_history = models_message_histories[
                current_model_talking
            ]

            new_message = await self.llm_speech_service.get_llm_speech_reply(
                current_model_message_history,
                text_to_speech_voice=models_voices[current_model_talking],
            )

            new_llm_conversation_message = LlmConversationMessage(
                content=new_message.content,
                speech_audio_data=new_message.speech_audio_data,
                from_which_model=current_model_talking,
            )
            await handle_new_message(new_llm_conversation_message)

            logger.info(
                '<%s> Model %s said (message %s): "%s"',
                conversation_id,
                current_model_talking,
                message_number,
                new_message.content.replace("\n", " "),
            )

            # Toggles between 1st and 2nd model
            next_model_that_replies = get_opposite_model_name(current_model_talking)

            models_message_histories[next_model_that_replies].append(
                # Puts AI model response in other model's message history as a
                # user message
                LlmMessage(role="user", content=new_message.content)
            )

            current_model_talking = next_model_that_replies

        logger.info("<%s> Conversation finished", conversation_id)
