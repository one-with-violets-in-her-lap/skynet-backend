import socketio

from skynet_backend.websockets_api.dependencies import (
    close_resources_on_socketio_disconnect,
    initialize_api_dependencies_in_socketio_session,
)
from skynet_backend.websockets_api.events.start_llm_conversation import (
    handle_start_llm_conversation,
)


def register_socketio_events(socketio_server: socketio.AsyncServer):
    socketio_server.on("connect", initialize_api_dependencies_in_socketio_session)
    socketio_server.on("disconnect", close_resources_on_socketio_disconnect)

    socketio_server.on("start-llm-conversation", handle_start_llm_conversation)
