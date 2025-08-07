from typing import List

from modules.comment.internal.comment_reader import CommentReader
from modules.comment.internal.comment_writer import CommentWriter
from modules.comment.types import (
    Comment,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetTaskCommentsParams,
    UpdateCommentParams,
)


class CommentService:
    @staticmethod
    def create_comment(params: CreateCommentParams) -> Comment:
        writer = CommentWriter()
        return writer.create_comment(params)

    @staticmethod
    def get_comment(params: GetCommentParams) -> Comment:
        reader = CommentReader()
        return reader.get_comment_by_id(params)

    @staticmethod
    def get_task_comments(params: GetTaskCommentsParams) -> List[Comment]:
        reader = CommentReader()
        return reader.get_comments_by_task_id(params)

    @staticmethod
    def update_comment(params: UpdateCommentParams) -> Comment:
        writer = CommentWriter()
        return writer.update_comment(params)

    @staticmethod
    def delete_comment(params: DeleteCommentParams) -> None:
        writer = CommentWriter()
        writer.delete_comment(params)
