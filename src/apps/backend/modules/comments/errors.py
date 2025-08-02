from modules.application.errors import AppError


class CommentNotFoundError(AppError):
    code = "COMMENT_ERR_01"
    http_code = 404


class CommentBadRequestError(AppError):
    code = "COMMENT_ERR_02"
    http_code = 400
