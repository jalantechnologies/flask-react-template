from modules.application.errors import AppError


class TaskNotFoundError(AppError):
    def __init__(self, message: str = "Task not found"):
        super().__init__(message=message, code="TASK_ERR_01", http_status_code=404)


class TaskBadRequestError(AppError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, code="TASK_ERR_02", http_status_code=400)


class CommentNotFoundError(AppError):
    def __init__(self, message: str = "Comment not found"):
        super().__init__(message=message, code="COMMENT_ERR_01", http_status_code=404)


class CommentBadRequestError(AppError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, code="COMMENT_ERR_02", http_status_code=400)


class CommentValidationError(AppError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message=message, code="COMMENT_ERR_03", http_status_code=400)
