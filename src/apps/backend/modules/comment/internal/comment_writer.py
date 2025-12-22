from datetime import datetime

from bson.objectid import ObjectId
from pymongo import ReturnDocument

from modules.comment.errors import CommentNotFoundError
from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.internal.comment_reader import CommentReader
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentsParams,
    Comment,
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
            {"_id": ObjectId(params.comment_id), "account_id": params.account_id, "active": True},
            {"$set": {"content": params.content, "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_comment_bson is None:
            raise CommentNotFoundError(message=f"Comment with id {params.comment_id} not found")

        return CommentUtil.convert_comment_bson_to_comment(updated_comment_bson)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> str:
        # Check if comment exists first? Or just try to delete.
        # TaskWriter checks first.
        
        # We don't have GetCommentParams for single comment by ID readily available in types 
        # but we can query directly or just use find_one_and_update which returns None if not found.
        
        deletion_time = datetime.now()
        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {"_id": ObjectId(params.comment_id), "account_id": params.account_id},
            {"$set": {"active": False, "updated_at": deletion_time}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_comment_bson is None:
            raise CommentNotFoundError(message=f"Comment with id {params.comment_id} not found")

        return params.comment_id
