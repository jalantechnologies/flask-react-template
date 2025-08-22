from modules.application.errors import AppError
from modules.task_comment.types import TaskCommentErrorCode


class TaskCommentNotFoundError(AppError):
    """Error when a task comment is not found"""
    def __init__(self, comment_id: str) -> None:
        super().__init__(
            code=TaskCommentErrorCode.COMMENT_NOT_FOUND,
            http_status_code=404,
            message=f"Task comment with id '{comment_id}' not found"
        )


class UnauthorizedCommentEditError(AppError):
    """Error when user tries to edit someone else's comment"""
    def __init__(self) -> None:
        super().__init__(
            code=TaskCommentErrorCode.UNAUTHORIZED_EDIT,
            http_status_code=403,
            message="You are not authorized to edit this comment"
        )


class UnauthorizedCommentDeleteError(AppError):
    """Error when user tries to delete someone else's comment"""
    def __init__(self) -> None:
        super().__init__(
            code=TaskCommentErrorCode.UNAUTHORIZED_DELETE,
            http_status_code=403,
            message="You are not authorized to delete this comment"
        )


class TaskNotFoundForCommentError(AppError):
    """Error when trying to comment on non-existent task"""
    def __init__(self, task_id: str) -> None:
        super().__init__(
            code=TaskCommentErrorCode.TASK_NOT_FOUND,
            http_status_code=404,
            message=f"Cannot add comment: Task with id '{task_id}' not found"
        )


class InvalidCommentContentError(AppError):
    """Error when comment content is invalid"""
    def __init__(self, reason: str = "Invalid comment content") -> None:
        super().__init__(
            code=TaskCommentErrorCode.INVALID_CONTENT,
            http_status_code=400,
            message=reason
        )


class CommentLockedError(AppError):
    """Error when trying to modify a locked comment"""
    def __init__(self) -> None:
        super().__init__(
            code=TaskCommentErrorCode.COMMENT_LOCKED,
            http_status_code=423,
            message="This comment is locked and cannot be modified"
        )

