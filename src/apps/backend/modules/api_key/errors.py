from modules.api_key.types import ApiKeyErrorCode
from modules.application.errors import AppError


class ApiKeyNotFoundError(AppError):
    def __init__(self) -> None:
        super().__init__(code=ApiKeyErrorCode.NOT_FOUND, http_status_code=404, message="API key not found.")


class ApiKeyBadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=ApiKeyErrorCode.BAD_REQUEST, http_status_code=400, message=message)


class ApiKeyAlreadyRevokedError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code=ApiKeyErrorCode.ALREADY_REVOKED, http_status_code=409, message="API key is already revoked."
        )


class ApiKeyExpiredError(AppError):
    def __init__(self) -> None:
        super().__init__(code=ApiKeyErrorCode.EXPIRED, http_status_code=401, message="API key has expired.")


class ApiKeyInvalidError(AppError):
    def __init__(self) -> None:
        super().__init__(code=ApiKeyErrorCode.INVALID, http_status_code=401, message="Invalid API key.")
