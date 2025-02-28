import uvicorn
import socketio

from skynet_backend.logging_config import root_logger
from skynet_backend.websockets_api.events import register_socketio_events
from skynet_backend.websockets_api.socketio_server import socketio_server


register_socketio_events(socketio_server)

if __name__ == "__main__":
    root_logger.info("Starting Socket.io server via uvicorn")
    uvicorn.run(socketio.ASGIApp(socketio_server))
