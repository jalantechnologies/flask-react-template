from typing import List, Optional, Dict, Any

from bson.objectid import ObjectId
from pymongo import DESCENDING

from modules.task_comment.internal.store.task_comment_model import TaskCommentModel
from modules.task_comment.internal.store.task_comments import TaskCommentRepository
from modules.task_comment.internal.task_comment_util import TaskCommentUtil
from modules.task_comment.types import TaskComment, GetTaskCommentsParams, TaskCommentFilters
from modules.logger.logger import Logger


class TaskCommentReader:
    """Handles read operations for task comments"""
    
    @staticmethod
    def get_comment_by_id(*, comment_id: str) -> Optional[TaskComment]:
        """
        Get a single comment by its ID
        
        Args:
            comment_id: ID of the comment to retrieve
            
        Returns:
            TaskComment or None if not found
        """
        try:
            comment_bson = TaskCommentRepository.collection().find_one({
                "_id": ObjectId(comment_id)
            })
            
            if comment_bson:
                return TaskCommentUtil.convert_comment_bson_to_comment(comment_bson)
            
            return None
            
        except Exception as e:
            Logger.error(message=f"Error retrieving comment {comment_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_comments_by_task(
        *,
        params: GetTaskCommentsParams,
        filters: Optional[TaskCommentFilters] = None
    ) -> List[TaskComment]:
        """
        Get all comments for a task with optional filtering and pagination
        
        Args:
            params: Parameters including task_id and pagination
            filters: Optional filters for the query
            
        Returns:
            List of TaskComment objects
        """
        # Build query
        query = {"task_id": params.task_id}
        
        # Apply filters if provided
        if filters:
            if filters.author_id:
                query["account_id"] = filters.author_id
            if filters.created_after:
                query["created_at"] = {"$gte": filters.created_after}
            if filters.created_before:
                if "created_at" in query:
                    query["created_at"]["$lte"] = filters.created_before
                else:
                    query["created_at"] = {"$lte": filters.created_before}
            if filters.search_text:
                query["$text"] = {"$search": filters.search_text}
        
        # Calculate pagination
        skip = 0
        limit = 20
        if params.pagination_params:
            skip = (params.pagination_params.page - 1) * params.pagination_params.size
            limit = params.pagination_params.size
        
        # Execute query
        cursor = TaskCommentRepository.collection().find(query).sort(
            "created_at", DESCENDING
        ).skip(skip).limit(limit)
        
        comments = []
        for comment_bson in cursor:
            comments.append(TaskCommentUtil.convert_comment_bson_to_comment(comment_bson))
        
        return comments
    
    @staticmethod
    def count_comments_by_task(*, task_id: str) -> int:
        """
        Count total comments for a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Total count of comments
        """
        return TaskCommentRepository.collection().count_documents({"task_id": task_id})
    
    @staticmethod
    def get_user_comments(
        *,
        account_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[TaskComment]:
        """
        Get all comments by a specific user
        
        Args:
            account_id: ID of the user
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of TaskComment objects
        """
        cursor = TaskCommentRepository.collection().find(
            {"account_id": account_id}
        ).sort(
            "created_at", DESCENDING
        ).skip(skip).limit(limit)
        
        comments = []
        for comment_bson in cursor:
            comments.append(TaskCommentUtil.convert_comment_bson_to_comment(comment_bson))
        
        return comments
    
    @staticmethod
    def search_comments(
        *,
        search_text: str,
        task_id: Optional[str] = None,
        account_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[TaskComment]:
        """
        Search comments using text search
        
        Args:
            search_text: Text to search for
            task_id: Optional task ID to limit search
            account_id: Optional account ID to limit search
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of TaskComment objects sorted by relevance
        """
        # Build query with text search
        query = {"$text": {"$search": search_text}}
        
        if task_id:
            query["task_id"] = task_id
        if account_id:
            query["account_id"] = account_id
        
        # Execute search with text score
        cursor = TaskCommentRepository.collection().find(
            query,
            {"score": {"$meta": "textScore"}}
        ).sort([
            ("score", {"$meta": "textScore"})
        ]).skip(skip).limit(limit)
        
        comments = []
        for comment_bson in cursor:
            comments.append(TaskCommentUtil.convert_comment_bson_to_comment(comment_bson))
        
        return comments
    
    @staticmethod
    def get_recent_comments(
        *,
        limit: int = 10,
        task_ids: Optional[List[str]] = None
    ) -> List[TaskComment]:
        """
        Get most recent comments across all tasks or specific tasks
        
        Args:
            limit: Number of recent comments to return
            task_ids: Optional list of task IDs to filter by
            
        Returns:
            List of most recent TaskComment objects
        """
        query = {}
        
        if task_ids:
            query["task_id"] = {"$in": task_ids}
        
        cursor = TaskCommentRepository.collection().find(query).sort(
            "created_at", DESCENDING
        ).limit(limit)
        
        comments = []
        for comment_bson in cursor:
            comments.append(TaskCommentUtil.convert_comment_bson_to_comment(comment_bson))
        
        return comments