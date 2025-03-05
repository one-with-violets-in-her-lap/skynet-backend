from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel


class LazypyVoice(Enum):
    EN_UK_003 = "en_uk_003"
    EN_US_010 = "en_us_010"


class LazypyTextToSpeechResult(BaseModel):
    success: bool
    audio_url: Optional[str]
    error_msg: Optional[str]


class LazypyTextToSpeechSuccessResult(BaseModel):
    success: Literal[True]
    audio_url: str
    error_msg: None
