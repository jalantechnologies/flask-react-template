from modules.application.errors import AppError
from modules.push_notification.types import PushNotificationErrorCode


class PushNotificationNotFoundError(AppError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            code=PushNotificationErrorCode.NOT_FOUND,
            http_status_code=404,
            message=message or "Push notification not found.",
        )


class PushNotificationBadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code=PushNotificationErrorCode.BAD_REQUEST,
            http_status_code=400,
            message=message,
        )


class InvalidNotificationStatusError(AppError):
    def __init__(self, status: str) -> None:
        super().__init__(
            code=PushNotificationErrorCode.INVALID_STATUS,
            http_status_code=400,
            message=f"Invalid notification status: {status}. Must be one of: 'pending', 'processing', 'sent', 'delivered', 'failed', 'expired'.",
        )


class InvalidPriorityError(AppError):
    def __init__(self, priority: str) -> None:
        super().__init__(
            code=PushNotificationErrorCode.INVALID_PRIORITY,
            http_status_code=400,
            message=f"Invalid priority: {priority}. Must be one of: 'immediate', 'normal'.",
        )


class MaxRetriesExceededError(AppError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            code=PushNotificationErrorCode.MAX_RETRIES_EXCEEDED,
            http_status_code=400,
            message=message or "Maximum retry attempts exceeded for this notification.",
        )
