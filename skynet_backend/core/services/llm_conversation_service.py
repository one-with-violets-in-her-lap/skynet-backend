from datetime import datetime
import logging
from typing import Any, Callable

from skynet_backend.core.models.llm_conversation import (
    ConversationParticipantModelName,
    LlmConversationMessage,
    LlmConversationPreferences,
    get_opposite_model_name,
)
from skynet_backend.core.models.llm_message import LlmMessage
from skynet_backend.core.services.llm_speech_service import LlmSpeechService
from skynet_backend.core.utils.llm_conversation_message_builder import (
    get_master_prompt,
    inject_additional_instructions_in_message,
)


ENTRYPOINT_MESSAGE = LlmMessage(
    role="user",
    content="Greet me, ask me how I am doing and let's talk about something.",
)


logger = logging.getLogger(__name__)


class LlmConversationService:
    def __init__(self, llm_speech_service: LlmSpeechService):
        self.llm_speech_service = llm_speech_service

    async def start_llm_conversation(
        self,
        handle_new_message: Callable[[LlmConversationMessage], Any],
        preferences: LlmConversationPreferences = LlmConversationPreferences(),
        max_conversation_messages_count=10,
    ):
        conversation_id = round(datetime.now().timestamp())

        current_model_talking: ConversationParticipantModelName = "model-1"

        master_prompt = get_master_prompt(preferences)
        processed_entrypoint_message = inject_additional_instructions_in_message(
            ENTRYPOINT_MESSAGE
        )

        models_message_histories: dict[
            ConversationParticipantModelName, list[LlmMessage]
        ] = {
            "model-1": [master_prompt, processed_entrypoint_message],
            "model-2": [master_prompt],
        }

        logger.info("<%s> AI conversation started", conversation_id)

        for message_number in range(1, max_conversation_messages_count + 1):
            logger.info(
                "<%s> Model %s is talking", conversation_id, str(current_model_talking)
            )

            current_model_message_history = models_message_histories[
                current_model_talking
            ]

            new_message = await self.llm_speech_service.get_llm_speech_reply(
                current_model_message_history,
                talking_model_name=current_model_talking,
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
                inject_additional_instructions_in_message(
                    LlmMessage(
                        role="user",
                        content=new_message.content,
                    )
                )
            )

            current_model_talking = next_model_that_replies

        logger.info("<%s> Conversation finished", conversation_id)
