from typing import List, Optional

from modules.application.errors import AppError
from modules.notification.types import NotificationErrorCode, ValidationFailure


class ValidationError(AppError):
    failures: List[ValidationFailure]

    def __init__(self, msg: str, failures: Optional[List[ValidationFailure]] = None) -> None:
        if failures is None:
            failures = []
        self.code = NotificationErrorCode.VALIDATION_ERROR
        super().__init__(message=msg, code=self.code)
        self.failures = failures
        self.http_code = 400


class AccountNotificationPreferencesNotFoundError(AppError):
    def __init__(self, account_id: str) -> None:
        super().__init__(
            code=NotificationErrorCode.PREFERENCES_NOT_FOUND,
            http_status_code=404,
            message=f"Notification preferences not found for account: {account_id}. Please create preferences first.",
        )


class ServiceError(AppError):
    def __init__(self, err: Exception) -> None:
        super().__init__(message=err.args[2], code=NotificationErrorCode.SERVICE_ERROR)
        self.code = NotificationErrorCode.SERVICE_ERROR
        self.stack = getattr(err, "stack", None)
        self.http_status_code = 503
