from modules.application.common.errors import ApplicationError


class CommentNotFoundError(ApplicationError):
    def __init__(self, message: str = "Comment not found"):
        super().__init__(message=message, error_code="COMMENT_ERR_01")


class CommentBadRequestError(ApplicationError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, error_code="COMMENT_ERR_02")


class TaskNotFoundError(ApplicationError):
    def __init__(self, message: str = "Task not found"):
        super().__init__(message=message, error_code="COMMENT_ERR_03") 