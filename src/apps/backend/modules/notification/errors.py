from typing import List, Optional
from modules.application.errors import AppError
from modules.notification.types import CommunicationErrorCode, NotificationErrorCode, ValidationFailure


class ValidationError(AppError):
    failures: List[ValidationFailure]

    def __init__(self, msg: str, failures: Optional[List[ValidationFailure]] = None) -> None:
        if failures is None:
            failures = []
        self.code = CommunicationErrorCode.VALIDATION_ERROR
        super().__init__(message=msg, code=self.code)
        self.failures = failures
        self.http_code = 400


class NotificationPreferencesNotFoundError(AppError):
    def __init__(self, account_id: str) -> None:
        super().__init__(
            code=NotificationErrorCode.PREFERENCES_NOT_FOUND,
            http_status_code=404,
            message=f"Notification preferences not found for account: {account_id}. Please create preferences first.",
        )


class ServiceError(AppError):
    def __init__(self, err: Exception) -> None:
        super().__init__(message=err.args[2], code=CommunicationErrorCode.SERVICE_ERROR)
        self.code = CommunicationErrorCode.SERVICE_ERROR
        self.stack = getattr(err, "stack", None)
        self.http_status_code = 503
