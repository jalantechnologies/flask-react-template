from typing import List, Optional

from modules.application.errors import AppError
from modules.notification.types import DeviceType, NotificationErrorCode, ValidationFailure


class ValidationError(AppError):
    failures: List[ValidationFailure]

    def __init__(self, msg: str, failures: Optional[List[ValidationFailure]] = None) -> None:
        if failures is None:
            failures = []
        self.code = NotificationErrorCode.VALIDATION_ERROR
        super().__init__(message=msg, code=self.code)
        self.failures = failures
        self.http_code = 400


class InvalidDeviceTypeError(AppError):
    def __init__(self, device_type: str, allowed_types: List[DeviceType]) -> None:
        allowed_types_str = ", ".join([device_type.value for device_type in allowed_types])

        super().__init__(
            code=NotificationErrorCode.INVALID_DEVICE_TYPE,
            http_status_code=400,
            message=f"Invalid device type: {device_type}. Must be one of: {allowed_types_str}",
        )


class AccountNotificationPreferencesNotFoundError(AppError):
    def __init__(self, account_id: str) -> None:
        super().__init__(
            code=NotificationErrorCode.PREFERENCES_NOT_FOUND,
            http_status_code=404,
            message=f"Notification preferences not found for account: {account_id}. Please create preferences first.",
        )


class DeviceTokenValidationError(Exception):
    def __init__(self, device_type_str: str, allowed_types: List[DeviceType]):
        self.device_type_str = device_type_str
        self.allowed_types = allowed_types
        super().__init__(f"Invalid device type: {device_type_str}")


class ServiceError(AppError):
    def __init__(self, err: Exception) -> None:
        super().__init__(message=err.args[2], code=NotificationErrorCode.SERVICE_ERROR)
        self.code = NotificationErrorCode.SERVICE_ERROR
        self.stack = getattr(err, "stack", None)
        self.http_status_code = 503
