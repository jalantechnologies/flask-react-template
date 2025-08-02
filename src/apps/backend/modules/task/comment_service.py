from modules.task.internal.comment_reader import CommentReader
from modules.task.internal.comment_writer import CommentWriter
from modules.task.types import (
    Comment,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetTaskCommentsParams,
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
    def get_task_comments(*, params: GetTaskCommentsParams):
        return CommentReader.get_task_comments(params=params)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        return CommentWriter.update_comment(params=params)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> bool:
        return CommentWriter.delete_comment(params=params)
