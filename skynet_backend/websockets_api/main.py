import logging

from ratelimit import Rule, RateLimitMiddleware
from ratelimit.auths.ip import client_ip
from ratelimit.backends.simple import MemoryBackend
import uvicorn
import socketio

from skynet_backend.websockets_api.events import register_socketio_events
from skynet_backend.websockets_api.config import websockets_api_config
from skynet_backend.websockets_api.socketio_server import socketio_server
from skynet_backend.websockets_api.config import websockets_api_config


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: [%(levelname)s] %(name)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    root_logger = logging.getLogger()

    register_socketio_events(socketio_server)

    socketio_asgi_app = socketio.ASGIApp(
        socketio_server,
        static_files={"/public": "./public"},
    )

    if websockets_api_config.enable_rate_limiting:
        socketio_asgi_app = RateLimitMiddleware(
            socketio_asgi_app,
            client_ip,
            MemoryBackend(),
            {
                r"^/*": [Rule(day=1, group="default")],
            },
        )

    root_logger.info("Starting Socket.io server via uvicorn")
    
    uvicorn.run(
        socketio_asgi_app,
        host=websockets_api_config.host,
        port=websockets_api_config.port,
    )
