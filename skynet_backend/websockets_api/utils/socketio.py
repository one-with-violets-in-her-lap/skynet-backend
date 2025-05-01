from functools import wraps
import logging
from typing import Any, Callable

from pyrate_limiter import BucketFullException, Limiter, Rate

from skynet_backend.websockets_api.socketio_server import socketio_server
from skynet_backend.websockets_api.utils.dependencies import (
    ApiSocketioSession,
    get_socketio_api_session,
)
from skynet_backend.websockets_api.utils.errors import (
    RateLimitedError,
    WebsocketsApiError,
    WebsocketsApiUnknownError,
)


_logger = logging.getLogger(__name__)

SocketioEventHandler = Callable[[str, ApiSocketioSession, str], Any]


def socketio_event_handler(
    event_handler_function: SocketioEventHandler,
):
    """
    Decorator for Socket.IO event handlers.

    Abstracts away error handling (you can just raise an error), session obtaining
    (you can just access `session` arg)
    """

    @wraps(event_handler_function)
    async def run_event_handler(connection_id: str, data):
        session = await get_socketio_api_session(connection_id)

        function_with_error_handling = handle_and_send_errors_to_socketio_client(
            event_handler_function
        )

        await function_with_error_handling(connection_id, session, data)

    return run_event_handler


def handle_and_send_errors_to_socketio_client(event_handler_function: Callable):
    """
    Decorator for Socket.IO event handlers that catches raised errors, sends them
    to Socket.IO client as `error` event and **closes the connection**.

    If the error raised is not an instance of `WebsocketsApiError`, it emits a
    generic error event
    """

    @wraps(event_handler_function)
    async def run_with_error_handling(connection_id: str, *args):
        try:
            await event_handler_function(connection_id, *args)
        except Exception as error:
            _logger.error(
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


def socketio_ip_rate_limit(max_rate: int, period_in_milliseconds: int):
    """
    Decorator for Socket.IO event handlers that controls how often can client trigger the
    handler. Identifies the client by an IP address
    """

    def create_rate_limit_decorator(event_handler_function: SocketioEventHandler):
        rate_limiter = Limiter(Rate(limit=max_rate, interval=period_in_milliseconds))

        @wraps(event_handler_function)
        async def run_with_rate_limiting(
            connection_id: str, session: ApiSocketioSession, data: str
        ):
            ip_address = session["client_ip_address"]
            _logger.info("Checking if %s is not rate limited", ip_address)

            try:
                rate_limiter.try_acquire(ip_address)
            except BucketFullException:
                raise RateLimitedError()

            await event_handler_function(connection_id, session, data)

        return run_with_rate_limiting

    return create_rate_limit_decorator
