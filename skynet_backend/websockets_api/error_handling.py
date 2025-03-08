import logging
from typing import Callable

from skynet_backend.websockets_api.socketio_server import socketio_server
from skynet_backend.websockets_api.utils.errors import (
    WebsocketsApiError,
    WebsocketsApiUnknownError,
)


logger = logging.getLogger(__name__)


def handle_and_send_errors_to_socketio_client(event_handler_function: Callable):
    """
    Decorator for Socket.IO event handlers that catches raised errors, sends them
    to Socket.IO client as `error` event and **closes the connection**.

    If the error raised is not an instance of `WebsocketsApiError`, it emits a
    generic error event
    """

    async def run_with_error_handling(connection_id: str, *args):
        try:
            await event_handler_function(connection_id, *args)
        except Exception as error:
            logger.error(
                "Error occurred during Socket.IO event handler execution: %s",
                error,
                exc_info=True,
            )

            if isinstance(error, WebsocketsApiError):
                await socketio_server.emit("error", data=vars(error), to=connection_id)
            else:
                await socketio_server.emit(
                    "error", data=vars(WebsocketsApiUnknownError()), to=connection_id
                )

            await socketio_server.disconnect(sid=connection_id)

    return run_with_error_handling
