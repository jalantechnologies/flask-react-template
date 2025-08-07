from modules.application.errors import AppError


class CommentError(AppError):
    pass


class CommentNotFoundError(CommentError):
    def __init__(self):
        super().__init__(error_code="COMMENT_NOT_FOUND", message="Comment not found", status_code=404)


class CommentBadRequestError(CommentError):
    def __init__(self, message: str):
        super().__init__(error_code="COMMENT_BAD_REQUEST", message=message, status_code=400)


class CommentForbiddenError(CommentError):
    def __init__(self):
        super().__init__(
            error_code="COMMENT_FORBIDDEN", message="You don't have permission to perform this action", status_code=403
        )
