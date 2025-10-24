from dataclasses import dataclass
from typing import Any, Optional


class AppError(Exception):
    def __init__(self, message: str, code: str, http_status_code: Optional[int] = None) -> None:
        self.message = message
        self.code = code
        self.http_code = http_status_code
        super().__init__(self.message)

    def to_str(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        error_dict = {
            "message": self.message,
            "code": self.code,
            "http_code": self.http_code,
            "args": self.args,
            "with_traceback": self.with_traceback,
        }
        return error_dict


@dataclass(frozen=True)
class WorkerErrorCode:
    WORKER_CLIENT_CONNECTION_ERROR: str = "WORKER_ERR_01"
    WORKER_NOT_REGISTERED: str = "WORKER_ERR_02"
    WORKER_WITH_ID_NOT_FOUND: str = "WORKER_ERR_03"
    WORKER_START_ERROR: str = "WORKER_ERR_04"
    WORKER_ALREADY_COMPLETED: str = "WORKER_ERR_05"
    WORKER_ALREADY_CANCELLED: str = "WORKER_ERR_06"
    WORKER_ALREADY_TERMINATED: str = "WORKER_ERR_07"


class WorkerClientConnectionError(AppError):
    def __init__(self, server_address: str) -> None:
        super().__init__(
            code=WorkerErrorCode.WORKER_CLIENT_CONNECTION_ERROR,
            http_status_code=500,
            message=f"System is unable to find a running instance of Temporal server at {server_address}. "
            f"Please make sure it is running and restart the server.",
        )


class WorkerNotRegisteredError(AppError):
    def __init__(self, worker_name: str) -> None:
        super().__init__(
            code=WorkerErrorCode.WORKER_NOT_REGISTERED,
            http_status_code=400,
            message=f"Worker class {worker_name} is not registered. "
            f"Have you included it in the list of workers in 'temporal_config.py'?",
        )


class WorkerIdNotFoundError(AppError):
    def __init__(self, worker_id: str) -> None:
        super().__init__(
            code=WorkerErrorCode.WORKER_WITH_ID_NOT_FOUND,
            http_status_code=404,
            message=f"Worker with given id: {worker_id} not found. Verify the ID of the worker and try again.",
        )


class WorkerStartError(AppError):
    def __init__(self, worker_name: str) -> None:
        super().__init__(
            code=WorkerErrorCode.WORKER_START_ERROR,
            http_status_code=500,
            message=f"Could not start worker with name: {worker_name}. "
            f"Check temporal server logs for more information.",
        )


class WorkerAlreadyCompletedError(AppError):
    def __init__(self, worker_id: str) -> None:
        super().__init__(
            code=WorkerErrorCode.WORKER_ALREADY_COMPLETED,
            http_status_code=400,
            message=f"Worker with id: {worker_id} has already completed running. "
            f"Verify the worker ID and try again.",
        )


class WorkerAlreadyCancelledError(AppError):
    def __init__(self, worker_id: str) -> None:
        super().__init__(
            code=WorkerErrorCode.WORKER_ALREADY_CANCELLED,
            http_status_code=400,
            message=f"Worker with id: {worker_id} has already been cancelled. Verify the worker ID and try again.",
        )


class WorkerAlreadyTerminatedError(AppError):
    def __init__(self, worker_id: str) -> None:
        super().__init__(
            code=WorkerErrorCode.WORKER_ALREADY_TERMINATED,
            http_status_code=400,
            message=f"Worker with id: {worker_id} has already been terminated. Verify the worker ID and try again.",
        )
