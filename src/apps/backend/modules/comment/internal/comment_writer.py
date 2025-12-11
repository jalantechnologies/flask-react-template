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
    GetCommentParams,
    Comment,
    CommentDeletionResult,
    UpdateCommentParams,
)
from modules.task.task_service import TaskService
from modules.task.types import GetTaskParams


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        # First verify that the task exists and belongs to the account
        task_params = GetTaskParams(account_id=params.account_id, task_id=params.task_id)
        TaskService.get_task(params=task_params)  # This will raise TaskNotFoundError if task doesn't exist
        
        comment_bson = CommentModel(
            account_id=params.account_id,
            task_id=params.task_id,
            content=params.content
        ).to_bson()
        
        query = CommentRepository.collection().insert_one(comment_bson)
        created_comment_bson = CommentRepository.collection().find_one({"_id": query.inserted_id})
        return CommentUtil.convert_comment_bson_to_comment(created_comment_bson)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {
                "_id": ObjectId(params.comment_id),
                "task_id": params.task_id,
                "account_id": params.account_id,
                "active": True
            },
            {"$set": {"content": params.content, "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER,
        )
        if updated_comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)
        return CommentUtil.convert_comment_bson_to_comment(updated_comment_bson)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        # First verify the comment exists
        comment = CommentReader.get_comment(params=GetCommentParams(
            account_id=params.account_id,
            task_id=params.task_id,
            comment_id=params.comment_id
        ))
        
        deletion_time = datetime.now()
        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {"_id": ObjectId(comment.id)},
            {"$set": {"active": False, "updated_at": deletion_time}},
            return_document=ReturnDocument.AFTER,
        )
        
        if updated_comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)
        
        return CommentDeletionResult(
            comment_id=params.comment_id,
            deleted_at=deletion_time,
            success=True
        )