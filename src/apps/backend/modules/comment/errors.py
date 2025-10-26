from modules.application.errors import AppError
from modules.task.types import TaskErrorCode


class CommentNotFound(AppError):
    def __init__(self, task_id: str) -> None:
        super().__init__(code=1, http_status_code=404, message=f"Comment with id {task_id} not found.")


class CommandBadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=TaskErrorCode.BAD_REQUEST, http_status_code=400, message=message)
