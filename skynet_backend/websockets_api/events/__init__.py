import socketio

from skynet_backend.websockets_api.events.start_llm_conversation import (
    handle_start_llm_conversation,
)


def register_socketio_events(socketio_server: socketio.AsyncServer):
    socketio_server.on("start-llm-conversation", handle_start_llm_conversation)
