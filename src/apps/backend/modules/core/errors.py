from typing import Any, Optional

from modules.core.common.types import CacheErrorCode, PhoneNumberErrorCode


class AppError(Exception):
    def __init__(self, message: str, code: str, http_status_code: Optional[int] = None) -> None:
        self.message = message
        self.code = code
        self.http_code = http_status_code
        super().__init__(self.message)

    def to_str(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        error_dict = {
            "message": self.message,
            "code": self.code,
            "http_code": self.http_code,
            "args": self.args,
            "with_traceback": self.with_traceback,
        }
        return error_dict


class CacheNonPositiveTTLError(AppError):
    def __init__(self, ttl_seconds: int) -> None:
        super().__init__(
            code=CacheErrorCode.NON_POSITIVE_TTL,
            http_status_code=400,
            message=f"Cache writes require a time to live greater than zero seconds, got {ttl_seconds}.",
        )


class CacheDiscardFailedError(AppError):
    def __init__(self, key: str, reason: str) -> None:
        super().__init__(
            code=CacheErrorCode.DISCARD_FAILED,
            http_status_code=503,
            message=f"Cache entry {key} could not be discarded and may still be served: {reason}",
        )


class MalformedPhoneNumberError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=PhoneNumberErrorCode.MALFORMED, http_status_code=400, message=message)


class InvalidPhoneNumberError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code=PhoneNumberErrorCode.INVALID, http_status_code=400, message="Please provide a valid phone number."
        )
