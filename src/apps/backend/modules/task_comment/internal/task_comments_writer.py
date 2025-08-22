from datetime import datetime
from typing import Optional, List, Dict, Any

from bson.objectid import ObjectId
from pymongo import ReturnDocument

from modules.task_comment.errors import (
    TaskCommentNotFoundError,
    UnauthorizedCommentEditError,
    UnauthorizedCommentDeleteError,
    InvalidCommentContentError
)
from modules.task_comment.internal.store.task_comment_model import TaskCommentModel
from modules.task_comment.internal.store.task_comments import TaskCommentRepository
from modules.task_comment.internal.task_comment_reader import TaskCommentReader
from modules.task_comment.internal.task_comment_util import TaskCommentUtil
from modules.task_comment.types import (
    TaskComment,
    CreateTaskCommentParams,
    UpdateTaskCommentParams,
    DeleteTaskCommentParams,
    TaskCommentDeletionResult
)
from modules.logger.logger import Logger


class TaskCommentWriter:
    """Handles write operations for task comments"""
    
    @staticmethod
    def create_comment(*, params: CreateTaskCommentParams) -> TaskComment:
        """
        Create a new task comment
        
        Args:
            params: Parameters for creating the comment
            
        Returns:
            TaskComment: The created comment
        """
        # Validate content
        if not params.content or len(params.content.strip()) == 0:
            raise InvalidCommentContentError("Comment content cannot be empty")
        
        if len(params.content) > 1000:
            raise InvalidCommentContentError("Comment content cannot exceed 1000 characters")
        
        # Create the comment model
        comment_model = TaskCommentModel(
            task_id=params.task_id,
            account_id=params.account_id,
            content=params.content.strip(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Convert to BSON and insert
        comment_bson = comment_model.to_bson()
        result = TaskCommentRepository.collection().insert_one(comment_bson)
        
        # Retrieve the created comment
        created_comment_bson = TaskCommentRepository.collection().find_one({"_id": result.inserted_id})
        
        Logger.info(message=f"Created comment {result.inserted_id} for task {params.task_id}")
        
        return TaskCommentUtil.convert_comment_bson_to_comment(created_comment_bson)
    
    @staticmethod
    def update_comment(*, params: UpdateTaskCommentParams) -> TaskComment:
        """
        Update an existing comment
        
        Args:
            params: Parameters for updating the comment
            
        Returns:
            TaskComment: The updated comment
            
        Raises:
            TaskCommentNotFoundError: If comment not found
            UnauthorizedCommentEditError: If user is not the author
            InvalidCommentContentError: If content is invalid
        """
        # Validate content
        if not params.content or len(params.content.strip()) == 0:
            raise InvalidCommentContentError("Comment content cannot be empty")
        
        if len(params.content) > 1000:
            raise InvalidCommentContentError("Comment content cannot exceed 1000 characters")
        
        # Check if comment exists and user has permission
        existing_comment = TaskCommentReader.get_comment_by_id(comment_id=params.comment_id)
        if not existing_comment:
            raise TaskCommentNotFoundError(params.comment_id)
        
        if existing_comment.account_id != params.account_id:
            Logger.warning(
                message=f"Unauthorized edit attempt on comment {params.comment_id} "
                f"by user {params.account_id}"
            )
            raise UnauthorizedCommentEditError()
        
        # Update the comment
        updated_comment_bson = TaskCommentRepository.collection().find_one_and_update(
            {
                "_id": ObjectId(params.comment_id),
                "task_id": params.task_id,
                "account_id": params.account_id
            },
            {
                "$set": {
                    "content": params.content.strip(),
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=ReturnDocument.AFTER
        )
        
        if updated_comment_bson is None:
            raise TaskCommentNotFoundError(params.comment_id)
        
        Logger.info(message=f"Updated comment {params.comment_id}")
        
        return TaskCommentUtil.convert_comment_bson_to_comment(updated_comment_bson)
    
    @staticmethod
    def delete_comment(*, params: DeleteTaskCommentParams) -> TaskCommentDeletionResult:
        """
        Delete a comment permanently
        
        Args:
            params: Parameters for deleting the comment
            
        Returns:
            TaskCommentDeletionResult: Result of the deletion operation
            
        Raises:
            TaskCommentNotFoundError: If comment not found
            UnauthorizedCommentDeleteError: If user is not the author
        """
        # Check if comment exists and user has permission
        existing_comment = TaskCommentReader.get_comment_by_id(comment_id=params.comment_id)
        if not existing_comment:
            raise TaskCommentNotFoundError(params.comment_id)
        
        if existing_comment.account_id != params.account_id:
            Logger.warning(
                message=f"Unauthorized delete attempt on comment {params.comment_id} "
                f"by user {params.account_id}"
            )
            raise UnauthorizedCommentDeleteError()
        
        # Delete the comment permanently
        result = TaskCommentRepository.collection().delete_one({
            "_id": ObjectId(params.comment_id)
        })
        
        success = result.deleted_count > 0
        
        if success:
            Logger.info(message=f"Deleted comment {params.comment_id}")
        else:
            Logger.error(message=f"Failed to delete comment {params.comment_id}")
        
        return TaskCommentDeletionResult(
            comment_id=params.comment_id,
            deleted_at=datetime.utcnow(),
            success=success,
            message="Comment deleted successfully" if success else "Failed to delete comment"
        )
    
    @staticmethod
    def bulk_delete_task_comments(*, task_id: str) -> int:
        """
        Delete all comments for a task
        Used when a task is deleted
        
        Args:
            task_id: ID of the task whose comments should be deleted
            
        Returns:
            int: Number of comments deleted
        """
        result = TaskCommentRepository.collection().delete_many({
            "task_id": task_id
        })
        
        Logger.info(message=f"Deleted {result.deleted_count} comments for task {task_id}")
        
        return result.deleted_count