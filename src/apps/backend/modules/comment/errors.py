from modules.application.errors import AppError
from modules.comment.types import CommentErrorCode


class CommentNotFoundError(AppError):
    def __init__(self, comment_id: str) -> None:
        super().__init__(
            message=f"Comment with id '{comment_id}' not found", code=CommentErrorCode.NOT_FOUND, http_code=404
        )


class CommentBadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code=CommentErrorCode.BAD_REQUEST, http_code=400)