from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument

from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import (
    Comment,
    CreateCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    CommentDeletionResult,
)


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        comment_bson = CommentModel(
            task_id=params.task_id,
            account_id=params.account_id,
            content=params.content,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ).to_bson()

        # Insert
        query = CommentRepository.collection().insert_one(comment_bson)
        created_comment_bson = CommentRepository.collection().find_one({"_id": query.inserted_id})

        return CommentWriter._convert_bson_to_comment(created_comment_bson)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {"_id": ObjectId(params.comment_id), "task_id": params.task_id},
            {"$set": {"content": params.content, "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER,
        )

        if updated_comment_bson is None:
            raise Exception("Comment not found")

        return CommentWriter._convert_bson_to_comment(updated_comment_bson)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        result = CommentRepository.collection().delete_one({"_id": ObjectId(params.comment_id)})

        return CommentDeletionResult(
            comment_id=params.comment_id,
            deleted_at=datetime.now(),
            success=result.deleted_count > 0,
        )

    @staticmethod
    def _convert_bson_to_comment(data: dict) -> Comment:
        comment = CommentModel.from_bson(data)
        return Comment(
            id=str(comment.id),
            task_id=comment.task_id,
            account_id=comment.account_id,
            content=comment.content,
        )
