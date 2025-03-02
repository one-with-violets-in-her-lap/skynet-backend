import socketio

from skynet_backend.websockets_api.config import websockets_api_config


socketio_server = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=websockets_api_config.cors_allowed_origins
)
