# Task comment error defintions
#
# This module defines exception classes for comment operations
# It follows the same patterns established in moduels/task/errors.py
#

from tokenize import Comment
from modules.application.errors import AppError
from modules.task.comments.types import CommentErrorCode

class CommentNotFoundError(AppError):
    """
    Raised when requested comment does not exist

    Security considerations: message should not reveal if the task exists
    - prevents information leakage about other users' tasks
    - generic message for both non existent comments and unauthorised access

    Assumptions: 404 is appropriate for both caes
    """
    def __init__(self, comment_id: str) -> None:
        super().__init__(
            code=CommentErrorCode.NOT_FOUND,
            http_status_code=404,
            message=f"Comment with id {comment_id} not found."
        )


class CommentBadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code=CommentErrorCode.BAD_REQUEST,
            http_status_code=400,
            message=message
        )

class CommentTaskNotFoundError(AppError):
    """
    Raised for invalid comment request data

    Desgin decision: Generic bad request error for all validation failures
    - Content validation: Empty comment
    - Business rule violation
    - Invalid JSON

    Flexibility: message parameters allows specific validation details
    """

    def __init__(self, message: str) -> None:
        super().__init__(
            code= CommentErrorCode.BAD_REQUEST,
            http_status=400,
            message=message,
        )


class CommentTaskNotFoundError(AppError):
    """
    Raised when trying to create/access comment for non-existent task

    Different from CommentNotFoundError for clarity
    - helps distinguish between comment not found and task not found
    - only reveals tasks exisence to authorised users
    """

    def __init__(self, task_id: str) -> None:
        super().__init__(
            code=CommentErrorCode.TASK_NOT_FOUND,
            http_status_code=400,
            message=f"Task with id {task_id} not found."
        )

class CommentUnauthorizedAccessError(AppError):
    """
    Raised when user attempts to access comments they don't own.
    """

    def __init__(self, message: str = "Unauthorised access to comment") -> None:
        super().__init__(
            code=CommentErrorCode.UNAUTHORIZED_ACCESS,
            http_status_code=401,
            message=message
        )
