from datetime import datetime

from bson.objectid import ObjectId

from modules.comment.errors import CommentNotFoundError
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.types import CreateCommentParams, UpdateCommentParams, DeleteCommentParams, CommentDeletionResult


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> str:
        comment_bson = CommentUtil.convert_create_comment_params_to_comment_bson(params)
        result = CommentRepository.collection().insert_one(comment_bson)
        return str(result.inserted_id)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> None:
        update_data = {"content": params.content, "updated_at": datetime.utcnow()}
        result = CommentRepository.collection().update_one(
            {"_id": ObjectId(params.comment_id), "account_id": params.account_id, "task_id": params.task_id, "active": True},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise CommentNotFoundError(comment_id=params.comment_id)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        result = CommentRepository.collection().update_one(
            {"_id": ObjectId(params.comment_id), "account_id": params.account_id, "task_id": params.task_id, "active": True},
            {"$set": {"active": False, "updated_at": datetime.utcnow()}}
        )
        return CommentDeletionResult(comment_id=params.comment_id, deleted=result.modified_count > 0)
