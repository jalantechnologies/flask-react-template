from modules.comment.internal.comment_reader import CommentReader
from modules.comment.internal.comment_writer import CommentWriter
from modules.comment.types import (
    Comment,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentsParams,
    UpdateCommentParams,
)


class CommentService:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        return CommentWriter.create_comment(params=params)

    @staticmethod
    def get_comments_by_task(*, params: GetCommentsParams) -> list[Comment]:
        return CommentReader.get_comments_by_task_id(params=params)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        return CommentWriter.update_comment(params=params)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> str:
        return CommentWriter.delete_comment(params=params)
