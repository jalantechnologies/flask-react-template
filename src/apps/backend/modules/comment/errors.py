from modules.application.common.errors import ApplicationError
from modules.comment.types import CommentErrorCode


class CommentNotFoundError(ApplicationError):
    def __init__(self, *, comment_id: str):
        super().__init__(
            error_code=CommentErrorCode.NOT_FOUND,
            message=f"Comment with id {comment_id} not found",
        )


class CommentBadRequestError(ApplicationError):
    def __init__(self, *, message: str):
        super().__init__(
            error_code=CommentErrorCode.BAD_REQUEST,
            message=message,
        ) 