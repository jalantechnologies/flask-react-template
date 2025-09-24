from modules.application.errors import AppError


class CommentBadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code=CommentErrorCode.BAD_REQUEST, http_status_code=400)


class CommentNotFoundError(AppError):
    def __init__(self, comment_id: str) -> None:
        super().__init__(
            message=f"Comment with id {comment_id} not found", code=CommentErrorCode.NOT_FOUND, http_status_code=404
        )


class CommentErrorCode:
    BAD_REQUEST = "COMMENT_BAD_REQUEST"
    NOT_FOUND = "COMMENT_NOT_FOUND"
