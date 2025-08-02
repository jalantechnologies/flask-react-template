from datetime import datetime

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pymongo import ReturnDocument

from modules.task.errors import CommentValidationError
from modules.task.internal.comment_util import CommentUtil
from modules.task.internal.store.comment_model import CommentModel
from modules.task.internal.store.comment_repository import CommentRepository
from modules.task.types import Comment, CreateCommentParams, DeleteCommentParams, UpdateCommentParams


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        CommentUtil.validate_comment_content(params.content)
        CommentUtil.validate_task_exists(params.task_id, params.account_id)

        comment_bson = CommentModel(
            task_id=params.task_id, account_id=params.account_id, content=params.content.strip()
        ).to_bson()

        query = CommentRepository.collection().insert_one(comment_bson)
        created_comment_bson = CommentRepository.collection().find_one({"_id": query.inserted_id})

        return CommentUtil.convert_comment_bson_to_comment(created_comment_bson)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        CommentUtil.validate_comment_content(params.content)
        CommentUtil.validate_comment_exists(params.comment_id, params.task_id, params.account_id)

        try:
            object_id = ObjectId(params.comment_id)
        except InvalidId:
            raise CommentValidationError("Comment not found")

        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {"_id": object_id, "task_id": params.task_id, "account_id": params.account_id, "active": True},
            {"$set": {"content": params.content.strip(), "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_comment_bson is None:
            raise CommentValidationError("Failed to update comment")

        return CommentUtil.convert_comment_bson_to_comment(updated_comment_bson)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> bool:
        CommentUtil.validate_comment_exists(params.comment_id, params.task_id, params.account_id)

        try:
            object_id = ObjectId(params.comment_id)
        except InvalidId:
            raise CommentValidationError("Comment not found")

        result = CommentRepository.collection().update_one(
            {"_id": object_id, "task_id": params.task_id, "account_id": params.account_id, "active": True},
            {"$set": {"active": False, "updated_at": datetime.now()}},
        )

        return result.modified_count > 0
