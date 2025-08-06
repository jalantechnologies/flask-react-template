from modules.comment.internal.comment_writer import CommentWriter
from modules.comment.internal.comment_reader import CommentReader
from modules.comment.types import (
    CreateCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    Comment,
    CommentDeletionResult,
)


class CommentService:
    @staticmethod
    def create_comment(params: CreateCommentParams) -> Comment:
        return CommentWriter.create_comment(params=params)

    @staticmethod
    def update_comment(params: UpdateCommentParams) -> Comment:
        return CommentWriter.update_comment(params=params)

    @staticmethod
    def delete_comment(params: DeleteCommentParams) -> CommentDeletionResult:
        return CommentWriter.delete_comment(params=params)

    @staticmethod
    def get_comments_by_task_id(task_id: str) -> list[Comment]:
        return CommentReader.get_comments_by_task_id(task_id)
