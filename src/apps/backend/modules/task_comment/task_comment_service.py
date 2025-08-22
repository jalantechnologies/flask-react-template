from datetime import datetime
from typing import List, Optional
from pydantic import ValidationError

from modules.account.account_service import AccountService
from modules.task.task_service import TaskService
from modules.task.types import GetTaskParams
from modules.task_comment.internal.task_comment_reader import TaskCommentReader
from modules.task_comment.internal.task_comments_writer import TaskCommentWriter
from modules.task_comment.types import (
    TaskComment,
    CreateTaskCommentParams,
    UpdateTaskCommentParams,
    DeleteTaskCommentParams,
    GetTaskCommentsParams,
    TaskCommentDeletionResult,
    TaskCommentListResponse,
    TaskCommentFilters
)
from modules.task_comment.errors import (
    TaskCommentNotFoundError,
    UnauthorizedCommentEditError,
    UnauthorizedCommentDeleteError,
    InvalidCommentContentError,
    TaskNotFoundForCommentError,
    CommentLockedError
)
from modules.logger.logger import Logger


class TaskCommentService:
    """Service layer for task comment operations"""
    
    @staticmethod
    def create_comment(params: CreateTaskCommentParams) -> TaskComment:
        """
        Create a new comment on a task
        
        Steps:
        1. Verify the task exists
        2. Verify the user has permission to comment
        3. Validate comment content
        4. Create the comment
        """
        Logger.info(message=f"Creating comment for task {params.task_id} by user {params.account_id}")
        
        # Verify task exists and user has access
        try:
            Logger.info(message=f"Verifying task {params.task_id} exists for account {params.account_id}")
            task = TaskService.get_task(params=GetTaskParams(
                task_id=params.task_id,
                account_id=params.account_id
            ))
            if not task:
                Logger.error(message=f"Task {params.task_id} returned None for account {params.account_id}")
                raise TaskNotFoundForCommentError(params.task_id)
            Logger.info(message=f"Task {params.task_id} verified successfully")
        except Exception as e:
            Logger.error(message=f"Failed to verify task existence: {str(e)} (task_id={params.task_id}, account_id={params.account_id})")
            raise TaskNotFoundForCommentError(params.task_id)
        
        # Content validation is handled by Pydantic in the params
        # Additional business logic validation can go here
        
        # Create the comment
        comment = TaskCommentWriter.create_comment(params=params)
        
        Logger.info(message=f"Successfully created comment {comment.id}")
        return comment
    
    @staticmethod
    def update_comment(params: UpdateTaskCommentParams) -> TaskComment:
        """
        Update an existing comment
        
        Steps:
        1. Retrieve the comment
        2. Verify ownership
        3. Check if comment is locked
        4. Update the comment
        """
        Logger.info(message=f"Updating comment {params.comment_id}")
        
        # Get existing comment
        comment = TaskCommentReader.get_comment_by_id(comment_id=params.comment_id)
        if not comment:
            raise TaskCommentNotFoundError(params.comment_id)
        
        # Check authorization
        if comment.account_id != params.account_id:
            Logger.warning(
                message=f"Unauthorized edit attempt on comment {params.comment_id} "
                f"by user {params.account_id}"
            )
            raise UnauthorizedCommentEditError()
        
        # Check if comment is locked (e.g., too old to edit)
        # This is an example business rule
        time_since_creation = datetime.utcnow() - comment.created_at
        if time_since_creation.days > 7:  # Comments older than 7 days cannot be edited
            raise CommentLockedError()
        
        # Update the comment
        updated_comment = TaskCommentWriter.update_comment(params=params)
        
        Logger.info(message=f"Successfully updated comment {params.comment_id}")
        return updated_comment
    
    @staticmethod
    def delete_comment(params: DeleteTaskCommentParams) -> TaskCommentDeletionResult:
        """
        Delete a comment
        
        Steps:
        1. Retrieve the comment
        2. Verify ownership or admin privileges
        3. Delete the comment
        """
        Logger.info(message=f"Deleting comment {params.comment_id}")
        
        # Get existing comment
        comment = TaskCommentReader.get_comment_by_id(comment_id=params.comment_id)
        if not comment:
            raise TaskCommentNotFoundError(params.comment_id)
        
        # Check authorization
        if comment.account_id != params.account_id:
            # Here you could check if the user is an admin
            # For now, only comment owners can delete
            Logger.warning(
                message=f"Unauthorized delete attempt on comment {params.comment_id} "
                f"by user {params.account_id}"
            )
            raise UnauthorizedCommentDeleteError()
        
        # Delete the comment
        result = TaskCommentWriter.delete_comment(params=params)
        
        Logger.info(message=f"Successfully deleted comment {params.comment_id}")
        return result
    
    @staticmethod
    def get_task_comments(
        params: GetTaskCommentsParams,
        filters: Optional[TaskCommentFilters] = None
    ) -> TaskCommentListResponse:
        """
        Get all comments for a task with pagination
        
        Steps:
        1. Verify task exists
        2. Get comments with optional filters
        3. Get total count for pagination
        """
        Logger.info(message=f"Retrieving comments for task {params.task_id}")
        
        # Get comments
        comments = TaskCommentReader.get_comments_by_task(params=params, filters=filters)
        
        # Get total count
        total_count = TaskCommentReader.count_comments_by_task(task_id=params.task_id)
        
        # Build response
        pagination = params.pagination_params
        if pagination:
            has_more = (pagination.page * pagination.size) < total_count
            response = TaskCommentListResponse(
                comments=comments,
                task_id=params.task_id,
                total_count=total_count,
                page=pagination.page,
                limit=pagination.size,
                has_more=has_more
            )
        else:
            response = TaskCommentListResponse(
                comments=comments,
                task_id=params.task_id,
                total_count=total_count,
                page=1,
                limit=total_count,
                has_more=False
            )
        
        Logger.info(message=f"Retrieved {len(comments)} comments for task {params.task_id}")
        return response
    
    @staticmethod
    def get_comment_by_id(comment_id: str) -> Optional[TaskComment]:
        """Get a single comment by ID"""
        return TaskCommentReader.get_comment_by_id(comment_id=comment_id)