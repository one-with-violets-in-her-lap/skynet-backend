from datetime import datetime
import logging
from typing import Any, Callable, Literal

from skynet_backend.api_clients.lazypy.models import LazypyVoice
from skynet_backend.core.models.llm_message import LlmMessage, LlmMessageWithSpeech
from skynet_backend.core.services.llm_speech_service import LlmSpeechService


ENTRYPOINT_MESSAGE = LlmMessage(
    role="user",
    content="Greet me, ask me how I am doing and let's talk about something",
)

MASTER_PROMPT = LlmMessage(
    role="user",
    content='Do not ask "Can I help you with something other?" or similar '
    + "questions. Try to maintain the conversation proactively with me. And "
    + "please respond in a short form, like 1-2 sentences",
)


ModelIdentifier = Literal[1, 2]


logger = logging.getLogger(__name__)


class LlmConversationService:
    def __init__(self, llm_speech_service: LlmSpeechService):
        self.llm_speech_service = llm_speech_service

    async def start_llm_conversation(
        self,
        handle_new_message: Callable[[LlmMessageWithSpeech], Any],
        max_conversation_messages_count=10,
    ):
        conversation_id = round(datetime.now().timestamp())

        current_model_talking: ModelIdentifier = 1
        models_voices: dict[ModelIdentifier, LazypyVoice] = {
            1: LazypyVoice.BRIAN,
            2: LazypyVoice.JOEY,
        }
        models_message_histories: dict[ModelIdentifier, list[LlmMessage]] = {
            1: [MASTER_PROMPT, ENTRYPOINT_MESSAGE],
            2: [MASTER_PROMPT],
        }

        logger.info("<%s> AI conversation started", conversation_id)

        for message_number in range(max_conversation_messages_count + 1):
            logger.info(
                "<%s> Model %s is talking", conversation_id, str(current_model_talking)
            )

            current_model_message_history = models_message_histories[
                current_model_talking
            ]

            # logger.info(
            #     "<%s> Model %s message history: %s",
            #     conversation_id,
            #     str(current_model_talking),
            #     current_model_message_history,
            # )

            new_message = await self.llm_speech_service.get_llm_speech_reply(
                current_model_message_history,
                text_to_speech_voice=models_voices[current_model_talking],
            )
            await handle_new_message(new_message)

            logger.info(
                '<%s> Model %s said (message %s): "%s"',
                conversation_id,
                current_model_talking,
                message_number,
                new_message.content.replace("\n", " "),
            )

            # Toggles between 1st and 2nd model
            next_model_that_replies = 1 if current_model_talking == 2 else 2

            models_message_histories[next_model_that_replies].append(
                LlmMessage(role="user", content=new_message.content)
            )

            current_model_talking = next_model_that_replies

        logger.info("<%s> Conversation finished", conversation_id)
