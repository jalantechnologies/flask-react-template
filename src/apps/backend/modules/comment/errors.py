from modules.application.errors import AppError
from modules.comment.types import CommentErrorCode


class CommentError(AppError):
    pass


class CommentNotFoundError(CommentError):
    def __init__(self, message: str = "Comment not found"):
        super().__init__(message, 404, CommentErrorCode.NOT_FOUND)


class CommentBadRequestError(CommentError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, 400, CommentErrorCode.BAD_REQUEST)
