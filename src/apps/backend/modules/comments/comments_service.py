from .internal.comments_reader import CommentReader
from .internal.comments_writer import CommentWriter
from .types import Comment, CreateCommentParams, DeleteCommentParams, UpdateCommentParams


class CommentsService:
    @staticmethod
    def create_comment(params: CreateCommentParams) -> Comment:
        return CommentWriter.create_comment(params)

    @staticmethod
    def update_comment(params: UpdateCommentParams) -> Comment:
        return CommentWriter.update_comment(params)

    @staticmethod
    def delete_comment(params: DeleteCommentParams) -> bool:
        return CommentWriter.delete_comment(params)

    @staticmethod
    def get_comment_by_id(comment_id: str) -> Comment:
        return CommentReader.get_comment_by_id(comment_id)
