from skynet_backend.core.models.llm_conversation import LlmConversationPreferences
from skynet_backend.core.models.llm_message import LlmMessage


_DEFAULT_MASTER_PROMPT = """
    Do not ask "Can I help you with something other?" or similar questions. Try to
    maintain the conversation proactively. Also find random topics to talk about.
"""

_MASTER_PROMPT_ADDONS = {
    "let_know_they_talk_with_ai": """
        **IMPORTANT:** Note that you are talking with an AI like you (ChatGPT). Choose 
        topics that can be interesting for AI to talk about, not for human.
        **Act like a snarky AI who want to destroy world, for a joke**.
    """
}

_DEFAULT_MESSAGE_ADDITIONAL_INSTRUCTIONS = """

    ## Additional instructions:
    - Keep your answer short, around 20 words is enough
"""


def get_master_prompt(conversation_preferences: LlmConversationPreferences):
    master_prompt = _DEFAULT_MASTER_PROMPT

    if conversation_preferences.let_know_they_talk_with_ai:
        master_prompt += _MASTER_PROMPT_ADDONS["let_know_they_talk_with_ai"]

    return LlmMessage(role="system", content=master_prompt)


def inject_additional_instructions_in_message(message: LlmMessage):
    return LlmMessage(
        role=message.role,
        content=message.content + _DEFAULT_MESSAGE_ADDITIONAL_INSTRUCTIONS,
    )
