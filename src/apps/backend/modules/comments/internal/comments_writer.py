from modules.comments.errors import CommentNotFoundError
from modules.comments.types import Comment, CreateCommentParams, DeleteCommentParams, UpdateCommentParams

from .comments_util import convert_comment_bson_to_comment
from .store.comments_repository import CommentRepository


class CommentWriter:
    @staticmethod
    def create_comment(params: CreateCommentParams) -> Comment:
        repo = CommentRepository()
        doc = {
            "task_id": params.task_id,
            "account_id": params.account_id,
            "content": params.content,
            "created_at": params.created_at if hasattr(params, "created_at") else None,
            "updated_at": params.updated_at if hasattr(params, "updated_at") else None,
        }
        result = repo.collection().insert_one(doc)
        return CommentReader.get_comment_by_id(str(result.inserted_id))

    @staticmethod
    def update_comment(params: UpdateCommentParams) -> Comment:
        repo = CommentRepository()
        result = repo.collection().find_one_and_update(
            {"_id": params.comment_id},
            {"$set": {"content": params.content, "updated_at": datetime.now()}},
            return_document=True,
        )
        if not result:
            raise CommentNotFoundError("Comment not found")
        return convert_comment_bson_to_comment(result)

    @staticmethod
    def delete_comment(params: DeleteCommentParams) -> bool:
        repo = CommentRepository()
        result = repo.collection().delete_one({"_id": params.comment_id})
        if result.deleted_count == 0:
            raise CommentNotFoundError("Comment not found")
        return True
