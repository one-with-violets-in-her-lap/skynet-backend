import logging

import uvicorn
import socketio

from skynet_backend.websockets_api.events import register_socketio_events
from skynet_backend.websockets_api.socketio_server import socketio_server
from skynet_backend.websockets_api.config import websockets_api_config


root_logger = logging.getLogger()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: [%(levelname)s] %(name)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    register_socketio_events(socketio_server)

    root_logger.info("Starting Socket.io server via uvicorn")

    uvicorn.run(
        socketio.ASGIApp(
            socketio_server,
            static_files={"/public": "./public"},
        ),
        host=websockets_api_config.host,
        port=websockets_api_config.port,
    )
