from modules.application.errors import AppError
from modules.comment.types import CommentErrorCode


class CommentNotFoundError(AppError):
    def __init__(self, *, comment_id: str):
        super().__init__(
            code=CommentErrorCode.NOT_FOUND, http_status_code=404, message=f"Comment with id {comment_id} not found"
        )
        self.comment_id = comment_id


class CommentAccessDeniedError(AppError):
    def __init__(self, *, comment_id: str, account_id: str):
        super().__init__(
            code=CommentErrorCode.ACCESS_DENIED,
            http_status_code=403,
            message=f"Access denied to comment {comment_id} for account {account_id}",
        )
        self.comment_id = comment_id
        self.account_id = account_id


class TaskNotFoundError(AppError):
    def __init__(self, *, task_id: str):
        super().__init__(
            code=CommentErrorCode.BAD_REQUEST, http_status_code=400, message=f"Task with id {task_id} not found"
        )
        self.task_id = task_id
