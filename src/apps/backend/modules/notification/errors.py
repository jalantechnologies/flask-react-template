from modules.application.errors import AppError
from modules.notification.types import NotificationErrorCode


class NotificationInvalidTokenError(AppError):
    """Raised when an FCM token format is invalid or corrupted"""

    def __init__(self, token: str) -> None:
        super().__init__(
            code=NotificationErrorCode.INVALID_TOKEN,
            http_status_code=400,
            message=f"The provided FCM token '{token}' is invalid.",
        )


class NotificationServiceError(AppError):
    """Raised when the notification service encounters an unexpected error"""

    def __init__(self, message: str) -> None:
        super().__init__(
            code=NotificationErrorCode.SERVICE_ERROR,
            http_status_code=503,
            message=f"Notification service error: {message}",
        )


class NotificationValidationError(AppError):
    """Raised when notification parameters fail validation"""

    def __init__(self, message: str) -> None:
        super().__init__(
            code=NotificationErrorCode.VALIDATION_ERROR,
            http_status_code=400,
            message=f"Notification validation error: {message}",
        )


class NotificationConfigurationError(AppError):
    """
    Raised when Firebase configuration is missing or invalid

    This typically happens when environment variables or config values
    for Firebase credentials are missing or corrupted
    """

    def __init__(self) -> None:
        super().__init__(
            code=NotificationErrorCode.CONFIGURATION_ERROR,
            http_status_code=500,
            message="Firebase configuration is missing or invalid.",
        )


class NotificationTokenNotRegisteredError(AppError):
    """
    Raised when an FCM token is no longer registered with Firebase

    This usually means the user has uninstalled the app or cleared app data
    """

    def __init__(self, token: str) -> None:
        super().__init__(
            code=NotificationErrorCode.TOKEN_NOT_REGISTERED,
            http_status_code=400,
            message=f"The FCM token '{token}' is not registered or has expired.",
        )
