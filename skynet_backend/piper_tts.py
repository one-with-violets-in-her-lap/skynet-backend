"""**Sync** interface for managing Piper TTS models

If using in async event loop, make sure to wrap blocking CPU-intensive
functions calls in asyncio-friendly wrappers like `run_in_executor`
"""

import logging
from enum import Enum
from typing import Optional

from piper.download import ensure_voice_exists, get_voices
from piper.voice import PiperVoice


logger = logging.getLogger(__name__)


DOWNLOAD_DIRECTORY_PATH = "."


class PiperVoiceName(Enum):
    EN_US_JOHN_MEDIUM = "en_US-john-medium"
    EN_US_LESSAC_MEDIUM = "en_US-lessac-medium"


class PiperTTSModelsNotLoadedError(Exception):
    def __init__(self):
        super().__init__(
            "To use Piper models, you must load them via "
            + "`load_piper_tts_models` function"
        )


_loaded_piper_tts_models: Optional[dict[PiperVoiceName, PiperVoice]] = None


def ensure_piper_tts_models_downloaded():
    """Downloads Piper ONNX models and puts them in the current directory (`./`)

    **Runs synchronously**

    To use the TTS models, run `load_piper_tts_models` function
    """

    for voice in PiperVoiceName:
        logger.info(
            'Downloading "%s" model if it\'s not already downloaded...', voice.value
        )
        ensure_voice_exists(
            voice.value,
            data_dirs=[DOWNLOAD_DIRECTORY_PATH],
            download_dir=DOWNLOAD_DIRECTORY_PATH,
            voices_info=get_voices(DOWNLOAD_DIRECTORY_PATH),
        )

    logger.info("All Piper models was downloaded")


def load_piper_tts_models():
    """Loads Piper ONNX models from the current directory. **Runs synchronously**

    Excepts ONNX files to be here with names in this format: `[PIPER_VOICE_NAME].onnx`

    **To avoid errors related to missing files, usage of
    `ensure_piper_tts_models_downloaded` function is recommended**

    Returns:
        Dictionary with model names enums as keys and Piper instances as values
    """

    global _loaded_piper_tts_models

    _loaded_piper_tts_models = {
        voice: PiperVoice.load(f"{DOWNLOAD_DIRECTORY_PATH}/{voice.value}.onnx")
        for voice in PiperVoiceName
    }

    return _loaded_piper_tts_models


def get_loaded_piper_tts_models():
    """
    Gets Piper TTS models that are currently loaded via `load_piper_tts_models` function

    Raises:
        PiperTTSModelsNotLoadedError: If Piper models was not loaded yet. You must
            call `load_piper_tts_models` function before getting the models to use

    Returns:
        Dictionary with model names enums as keys and Piper instances as values
    """

    if _loaded_piper_tts_models is None:
        raise PiperTTSModelsNotLoadedError()

    return _loaded_piper_tts_models
