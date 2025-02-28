import uvicorn
import socketio

from skynet_backend.logging_config import root_logger


socketio_server = socketio.AsyncServer()

if __name__ == "__main__":
    root_logger.info("Starting Socket.io server via uvicorn")
    uvicorn.run(socketio.ASGIApp(socketio_server))
