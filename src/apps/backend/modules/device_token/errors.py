from modules.application.errors import AppError
from modules.device_token.types import DeviceTokenErrorCode


class DeviceTokenNotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code=DeviceTokenErrorCode.NOT_FOUND,
            http_status_code=404,
            message=message,
        )


class InvalidPlatformError(AppError):
    def __init__(self, platform: str) -> None:
        super().__init__(
            code=DeviceTokenErrorCode.INVALID_PLATFORM,
            http_status_code=400,
            message=f"Invalid platform: {platform}. Must be one of: 'android', 'ios'.",
        )

class DeviceTokenBadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code=DeviceTokenErrorCode.BAD_REQUEST,
            http_status_code=400,
            message=message,
        )

class DeviceTokenConflictError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code=DeviceTokenErrorCode.CONFLICT,
            http_status_code=409,
            message=message,
        )
