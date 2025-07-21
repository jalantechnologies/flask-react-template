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


class InvalidDeviceTypeError(ValidationError):
    def __init__(self, device_type: str, allowed_types: List[str]) -> None:
        allowed_types_str = ", ".join(allowed_types)
        super().__init__(
            f"Invalid device type: {device_type}. Must be one of: {allowed_types_str}",
            [ValidationFailure(field="device_type", message=f"Must be one of: {allowed_types_str}")],
        )
        self.code = NotificationErrorCode.INVALID_DEVICE_TYPE


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
