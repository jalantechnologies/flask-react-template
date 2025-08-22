from datetime import datetime
from typing import List, Optional, Dict, Any

from modules.task_comment.internal.store.task_comments import TaskCommentRepository as MongoTaskCommentRepository
from modules.task_comment.internal.store.task_comment_model import TaskCommentModel
from modules.task_comment.types import (
    TaskComment,
    CreateTaskCommentParams,
    UpdateTaskCommentParams,
    DeleteTaskCommentParams,
    GetTaskCommentsParams,
    TaskCommentFilters
)
from modules.task_comment.errors import TaskCommentNotFoundError


class TaskCommentRepository:
    """Repository interface for task comment data operations"""
    
    @staticmethod
    def create_comment(params: CreateTaskCommentParams) -> TaskComment:
        """Create a new task comment in the database"""
        
        # Create comment using MongoDB repository
        comment_model = MongoTaskCommentRepository.create_comment({
            "task_id": params.task_id,
            "account_id": params.account_id,
            "content": params.content
        })
        
        # Convert to domain model
        return TaskComment(**comment_model.to_domain_model())
    
    @staticmethod
    def get_comment_by_id(comment_id: str) -> Optional[TaskComment]:
        """Retrieve a single comment by its ID"""
        
        comment_model = MongoTaskCommentRepository.get_comment_by_id(comment_id)
        
        if not comment_model:
            return None
            
        return TaskComment(**comment_model.to_domain_model())
    
    @staticmethod
    def get_comments_by_task(
        params: GetTaskCommentsParams,
        filters: Optional[TaskCommentFilters] = None
    ) -> List[TaskComment]:
        """Get all comments for a specific task with optional filtering"""
        
        # Calculate pagination
        skip = 0
        limit = 20
        if params.pagination_params:
            skip = (params.pagination_params.page - 1) * params.pagination_params.size
            limit = params.pagination_params.size
        
        # Get comments based on whether we need author info
        if params.include_author_info:
            # Use aggregation to get author info
            comments_data = MongoTaskCommentRepository.get_comments_with_author_info(
                task_id=params.task_id,
                skip=skip,
                limit=limit
            )
            
            # Convert to domain models
            comments = []
            for data in comments_data:
                # Ensure datetime fields are properly formatted
                if isinstance(data.get('created_at'), datetime):
                    data['created_at'] = data['created_at']
                if isinstance(data.get('updated_at'), datetime):
                    data['updated_at'] = data['updated_at']
                    
                comments.append(TaskComment(**data))
            
            return comments
        else:
            # Get comments without author info
            comment_models = MongoTaskCommentRepository.get_comments_by_task(
                task_id=params.task_id,
                skip=skip,
                limit=limit
            )
            
            return [TaskComment(**model.to_domain_model()) for model in comment_models]
    
    @staticmethod
    def count_comments_by_task(task_id: str) -> int:
        """Count total comments for a task"""
        return MongoTaskCommentRepository.count_comments_by_task(task_id)
    
    @staticmethod
    def update_comment(params: UpdateTaskCommentParams) -> TaskComment:
        """Update an existing comment"""
        
        # Update in MongoDB
        success = MongoTaskCommentRepository.update_comment(
            comment_id=params.comment_id,
            content=params.content
        )
        
        if not success:
            raise TaskCommentNotFoundError(params.comment_id)
        
        # Return updated comment
        updated_model = MongoTaskCommentRepository.get_comment_by_id(params.comment_id)
        if not updated_model:
            raise TaskCommentNotFoundError(params.comment_id)
            
        return TaskComment(**updated_model.to_domain_model())
    
    @staticmethod
    def delete_comment(comment_id: str) -> bool:
        """Delete a comment permanently"""
        return MongoTaskCommentRepository.delete_comment(comment_id)
    
    @staticmethod
    def search_comments(
        search_text: str,
        task_id: Optional[str] = None,
        account_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[TaskComment]:
        """Search comments using text search"""
        
        comment_models = MongoTaskCommentRepository.search_comments(
            search_text=search_text,
            task_id=task_id,
            account_id=account_id,
            skip=skip,
            limit=limit
        )
        
        return [TaskComment(**model.to_domain_model()) for model in comment_models]
    
    @staticmethod
    def get_user_comments(
        account_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[TaskComment]:
        """Get all comments by a specific user"""
        
        comment_models = MongoTaskCommentRepository.get_user_comments(
            account_id=account_id,
            skip=skip,
            limit=limit
        )
        
        return [TaskComment(**model.to_domain_model()) for model in comment_models]
    
    @staticmethod
    def bulk_delete_task_comments(task_id: str) -> int:
        """Delete all comments for a task (when task is deleted)"""
        return MongoTaskCommentRepository.bulk_delete_task_comments(task_id)