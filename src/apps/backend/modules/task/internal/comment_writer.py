from datetime import datetime
from bson import ObjectId
from pymongo.errors import OperationFailure

from modules.logger.logger import Logger
from modules.task.errors import TaskNotFoundError, CommentNotFoundError
from modules.task.internal.store.comment_model import CommentModel
from modules.task.internal.store.comment_repository import CommentRepository
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.types import Comment, CreateCommentParams, UpdateCommentParams, DeleteCommentParams, CommentDeletionResult


class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        # First verify the task exists and belongs to the account
        task_collection = TaskRepository.collection()
        task = task_collection.find_one(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True}
        )
        if not task:
            raise TaskNotFoundError(params.task_id)

        # Create the comment
        comment_model = CommentModel(
            task_id=params.task_id,
            account_id=params.account_id,
            content=params.content,
            active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        comment_collection = CommentRepository.collection()
        try:
            result = comment_collection.insert_one(comment_model.to_bson())
            comment_model.id = result.inserted_id

            return Comment(
                id=str(comment_model.id),
                task_id=comment_model.task_id,
                account_id=comment_model.account_id,
                content=comment_model.content,
                created_at=comment_model.created_at,
                updated_at=comment_model.updated_at,
            )
        except OperationFailure as e:
            Logger.error(message=f"Failed to create comment: {e.details}")
            raise CommentNotFoundError("Failed to create comment")

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        # First verify the task exists and belongs to the account
        task_collection = TaskRepository.collection()
        task = task_collection.find_one(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True}
        )
        if not task:
            raise TaskNotFoundError(params.task_id)

        # Update the comment
        comment_collection = CommentRepository.collection()
        update_data = {
            "content": params.content,
            "updated_at": datetime.now()
        }

        try:
            result = comment_collection.update_one(
                {
                    "_id": ObjectId(params.comment_id),
                    "task_id": params.task_id,
                    "active": True
                },
                {"$set": update_data}
            )

            if result.matched_count == 0:
                raise CommentNotFoundError(params.comment_id)

            # Get the updated comment
            updated_comment = comment_collection.find_one(
                {"_id": ObjectId(params.comment_id), "task_id": params.task_id, "active": True}
            )

            comment_model = CommentModel.from_bson(updated_comment)
            return Comment(
                id=str(comment_model.id),
                task_id=comment_model.task_id,
                account_id=comment_model.account_id,
                content=comment_model.content,
                created_at=comment_model.created_at,
                updated_at=comment_model.updated_at,
            )
        except OperationFailure as e:
            Logger.error(message=f"Failed to update comment: {e.details}")
            raise CommentNotFoundError("Failed to update comment")

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        # First verify the task exists and belongs to the account
        task_collection = TaskRepository.collection()
        task = task_collection.find_one(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True}
        )
        if not task:
            raise TaskNotFoundError(params.task_id)

        # Delete the comment (soft delete)
        comment_collection = CommentRepository.collection()
        try:
            result = comment_collection.update_one(
                {
                    "_id": ObjectId(params.comment_id),
                    "task_id": params.task_id,
                    "active": True
                },
                {"$set": {"active": False, "updated_at": datetime.now()}}
            )

            if result.matched_count == 0:
                raise CommentNotFoundError(params.comment_id)

            return CommentDeletionResult(
                comment_id=params.comment_id,
                deleted_at=datetime.now(),
                success=True
            )
        except OperationFailure as e:
            Logger.error(message=f"Failed to delete comment: {e.details}")
            raise CommentNotFoundError("Failed to delete comment") 