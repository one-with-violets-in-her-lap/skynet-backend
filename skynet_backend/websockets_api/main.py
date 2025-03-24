import uvicorn
import socketio

from skynet_backend.piper_tts import (
    ensure_piper_tts_models_downloaded,
    load_piper_tts_models,
)
from skynet_backend.logging_config import root_logger
from skynet_backend.websockets_api.events import register_socketio_events
from skynet_backend.websockets_api.socketio_server import socketio_server
from skynet_backend.websockets_api.config import websockets_api_config


def main():
    register_socketio_events(socketio_server)

    ensure_piper_tts_models_downloaded()
    load_piper_tts_models()

    root_logger.info("Starting Socket.io server via uvicorn")
    uvicorn.run(
        socketio.ASGIApp(
            socketio_server,
            static_files={"/public": "./public"},
        ),
        host=websockets_api_config.host,
        port=websockets_api_config.port,
    )
