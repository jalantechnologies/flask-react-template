from dataclasses import dataclass
from typing import Optional

from modules.core.errors import AppError


@dataclass(frozen=True)
class HttpErrorCode:
    TRANSPORT_FAILURE = "HTTP_ERR_01"
    CONFLICTING_BODY = "HTTP_ERR_02"
    UNSUPPORTED_SCHEME = "HTTP_ERR_03"
    BLOCKED_TARGET = "HTTP_ERR_04"
    INVALID_JSON_BODY = "HTTP_ERR_05"


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


class HttpUnsupportedSchemeError(AppError):
    def __init__(self, scheme: str) -> None:
        super().__init__(
            code=HttpErrorCode.UNSUPPORTED_SCHEME,
            http_status_code=400,
            message=f"An outbound request must use http or https, not {scheme}.",
        )
        self.scheme = scheme


class HttpBlockedTargetError(AppError):
    def __init__(self, host: str, reason: str) -> None:
        super().__init__(
            code=HttpErrorCode.BLOCKED_TARGET,
            http_status_code=400,
            message=f"The request to {host} was blocked: {reason}.",
        )
        self.host = host
        self.reason = reason


class HttpInvalidJsonBodyError(AppError):
    def __init__(self, status_code: int) -> None:
        super().__init__(
            code=HttpErrorCode.INVALID_JSON_BODY,
            http_status_code=502,
            message=f"The response with status {status_code} did not carry a JSON body.",
        )
        self.status_code = status_code
