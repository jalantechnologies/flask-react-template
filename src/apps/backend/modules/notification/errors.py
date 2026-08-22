from typing import List, Optional

from modules.core.errors import AppError
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
    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        super().__init__(code=NotificationErrorCode.SERVICE_ERROR, http_status_code=503, message=message)
        self.original_error = original_error
        self.original_error_message = str(original_error) if original_error else None
        self.stack = getattr(original_error, "stack", None)


class EmailRejectedError(AppError):
    def __init__(self, recipient: str, reason: str, status_code: Optional[int] = None) -> None:
        super().__init__(
            code=NotificationErrorCode.EMAIL_REJECTED,
            http_status_code=502,
            message=f"The email was rejected by the email provider: {reason}.",
        )
        self.recipient = recipient
        self.reason = reason
        self.status_code = status_code


class EmailServiceUnavailableError(AppError):
    def __init__(self, recipient: str, reason: str, status_code: Optional[int] = None) -> None:
        super().__init__(
            code=NotificationErrorCode.EMAIL_SERVICE_UNAVAILABLE,
            http_status_code=503,
            message=f"The email could not be delivered because the email provider is unavailable: {reason}.",
        )
        self.recipient = recipient
        self.reason = reason
        self.status_code = status_code
