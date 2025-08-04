from datetime import datetime

from bson.objectid import ObjectId
from pymongo import ReturnDocument

from modules.comments.errors import CommentNotFoundError
from modules.comments.internal.comment_reader import CommentReader
from modules.comments.internal.comment_util import CommentUtil
from modules.comments.internal.store.comment_model import CommentModel
from modules.comments.internal.store.comment_repository import CommentRepository
from modules.comments.types import (
    Comment,
    CommentDeletionResult,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    UpdateCommentParams,
)


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        comment_bson = CommentModel(
            account_id=params.account_id, task_id=params.task_id, content=params.content
        ).to_bson()

        query = CommentRepository.collection().insert_one(comment_bson)
        created_comment_bson = CommentRepository.collection().find_one({"_id": query.inserted_id})

        return CommentUtil.convert_comment_bson_to_comment(created_comment_bson)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {
                "_id": ObjectId(params.comment_id),
                "account_id": params.account_id,
                "task_id": params.task_id,
                "active": True,
            },
            {"$set": {"content": params.content, "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)

        return CommentUtil.convert_comment_bson_to_comment(updated_comment_bson)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        comment = CommentReader.get_comment(
            params=GetCommentParams(account_id=params.account_id, task_id=params.task_id, comment_id=params.comment_id)
        )

        deletion_time = datetime.now()
        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {"_id": ObjectId(comment.id)},
            {"$set": {"active": False, "updated_at": deletion_time}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)

        return CommentDeletionResult(comment_id=params.comment_id, deleted_at=deletion_time, success=True)
