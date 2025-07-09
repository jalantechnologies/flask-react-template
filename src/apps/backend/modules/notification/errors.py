from typing import List, Optional

from modules.application.errors import AppError
from modules.notification.types import CommunicationErrorCode, ValidationFailure


class ValidationError(AppError):
    failures: List[ValidationFailure]

    def __init__(self, msg: str, failures: Optional[List[ValidationFailure]] = None) -> None:
        if failures is None:
            failures = []
        self.code = CommunicationErrorCode.VALIDATION_ERROR
        super().__init__(message=msg, code=self.code)
        self.failures = failures
        self.http_code = 400


class ServiceError(AppError):

    def __init__(self, err: Exception) -> None:
        super().__init__(message=err.args[2], code=CommunicationErrorCode.SERVICE_ERROR)
        self.code = CommunicationErrorCode.SERVICE_ERROR
        self.stack = getattr(err, "stack", None)
        self.http_status_code = 503


class InvalidFCMTokenError(AppError):

    def __init__(self, message: str) -> None:
        super().__init__(code=CommunicationErrorCode.INVALID_FCM_TOKEN, http_status_code=400, message=message)


class FCMServiceError(AppError):

    def __init__(self, message: str) -> None:
        super().__init__(code=CommunicationErrorCode.FCM_SERVICE_ERROR, http_status_code=503, message=message)
