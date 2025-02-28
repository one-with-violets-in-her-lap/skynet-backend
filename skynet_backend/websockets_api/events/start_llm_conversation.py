import logging


logger = logging.getLogger(__name__)


async def handle_start_llm_conversation(sid, environ):
    logger.info("LLM conversation start event with sid: %s", sid)
