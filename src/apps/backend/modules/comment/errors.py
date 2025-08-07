from modules.application.errors import AppError
from modules.comment.types import CommentErrorCode


class CommentNotFoundError(AppError):
    def __init__(self, comment_id: str):
        super().__init__(
            message=f"Comment with ID '{comment_id}' not found.",
            code=CommentErrorCode.NOT_FOUND,
            http_code=404,
        )


class CommentBadRequestError(AppError):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code=CommentErrorCode.BAD_REQUEST,
            http_code=400,
        )


class CommentTaskNotFoundError(AppError):
    def __init__(self, task_id: str):
        super().__init__(
            message=f"Task with ID '{task_id}' not found. Cannot create comment.",
            code=CommentErrorCode.TASK_NOT_FOUND,
            http_code=404,
        )
