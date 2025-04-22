from typing import Optional


class ExternalApiError(Exception):
    def __init__(self, status_code: Optional[int] = None, detail: Optional[str] = None):
        error_message = "Something went wrong while calling an external API"

        if detail is not None:
            error_message = f"External API error: {detail}"

        if status_code is not None:
            error_message += f". Status code: {status_code}"

        super().__init__(error_message)

        self.status_code = status_code
        self.detail = detail
