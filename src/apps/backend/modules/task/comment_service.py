from modules.application.common.types import PaginationResult
from modules.task.internal.comment_reader import CommentReader
from modules.task.internal.comment_writer import CommentWriter
from modules.task.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetCommentsForTaskParams,
    Comment,
    CommentDeletionResult,
    UpdateCommentParams,
)


class CommentService:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        return CommentWriter.create_comment(params=params)

    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        return CommentReader.get_comment(params=params)

    @staticmethod
    def get_comments_for_task(*, params: GetCommentsForTaskParams) -> PaginationResult[Comment]:
        return CommentReader.get_comments_for_task(params=params)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        return CommentWriter.update_comment(params=params)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        return CommentWriter.delete_comment(params=params)