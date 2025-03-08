class WebsocketsApiError(Exception):
    """
    An error to send to WS client when something wrong happened during
    Socket.IO client event processing

    **Make sure not to put any sensitive data in `name` or  `detail` fields,
    because these errors are sent to the client**
    """

    def __init__(self, name: str, detail: str):
        super().__init__(f"{detail} ({name})")

        self.name = name
        self.detail = detail


class WebsocketsApiUnknownError(WebsocketsApiError):
    """Generic Websockets API error

    Send this when something unexpectedly failed or when client doesn't need to know
    about the reason of an error (e.g. error contains sensitive data)
    """

    def __init__(self):
        super().__init__("unknown-error", "An unknown error occurred")
