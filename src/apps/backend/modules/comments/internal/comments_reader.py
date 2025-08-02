from modules.comments.errors import CommentNotFoundError
from modules.comments.types import Comment

from .comments_util import convert_comment_bson_to_comment
from .store.comments_repository import CommentRepository


class CommentReader:
    @staticmethod
    def get_comment_by_id(comment_id: str) -> Comment:
        repo = CommentRepository()
        bson = repo.collection().find_one({"_id": comment_id})
        if not bson:
            raise CommentNotFoundError("Comment not found")
        return convert_comment_bson_to_comment(bson)
