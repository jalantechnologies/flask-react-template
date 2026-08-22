from typing import Optional

from modules.core.errors import AppError
from modules.core.http.types import HttpErrorCode


class HttpTransportError(AppError):
    def __init__(self, host: str, reason: str, original_error: Optional[Exception] = None) -> None:
        super().__init__(
            code=HttpErrorCode.TRANSPORT_FAILURE,
            http_status_code=503,
            message=f"The request to {host} could not be completed: {reason}.",
        )
        self.host = host
        self.reason = reason
        self.original_error = original_error


class HttpConflictingBodyError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code=HttpErrorCode.CONFLICTING_BODY,
            http_status_code=400,
            message="A request carries either a JSON body or a form body, never both.",
        )
