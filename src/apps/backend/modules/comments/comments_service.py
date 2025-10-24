from typing import List

from modules.comments.internal.comments_reader import CommentReader
from modules.comments.internal.comments_writer import CommentWriter
from modules.comments.types import (
    Comment,
    CommentDeletionResult,
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
    def get_comments(*, params: GetCommentsParams) -> List[Comment]:
        return CommentReader.get_comments(params=params)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        return CommentWriter.update_comment(params=params)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        return CommentWriter.delete_comment(params=params)
