from bson import ObjectId
from pymongo.errors import OperationFailure

from modules.application.common.types import PaginationResult
from modules.application.repository import ApplicationRepository
from modules.logger.logger import Logger
from modules.task.errors import TaskNotFoundError, CommentNotFoundError
from modules.task.internal.store.comment_model import CommentModel
from modules.task.internal.store.comment_repository import CommentRepository
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.types import Comment, GetCommentParams, GetPaginatedCommentsParams


class CommentReader:
    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        # First verify the task exists and belongs to the account
        task_collection = TaskRepository.collection()
        task = task_collection.find_one(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True}
        )
        if not task:
            raise TaskNotFoundError(params.task_id)

        # Get the comment
        comment_collection = CommentRepository.collection()
        comment = comment_collection.find_one(
            {"_id": ObjectId(params.comment_id), "task_id": params.task_id, "active": True}
        )
        if not comment:
            raise CommentNotFoundError(params.comment_id)

        comment_model = CommentModel.from_bson(comment)
        return Comment(
            id=str(comment_model.id),
            task_id=comment_model.task_id,
            account_id=comment_model.account_id,
            content=comment_model.content,
            created_at=comment_model.created_at,
            updated_at=comment_model.updated_at,
        )

    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        # First verify the task exists and belongs to the account
        task_collection = TaskRepository.collection()
        task = task_collection.find_one(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True}
        )
        if not task:
            raise TaskNotFoundError(params.task_id)

        # Get paginated comments
        comment_collection = CommentRepository.collection()
        
        # Calculate skip for pagination
        skip = (params.pagination_params.page - 1) * params.pagination_params.size
        
        # Build query
        query = {"task_id": params.task_id, "active": True}
        
        # Get total count
        total_count = comment_collection.count_documents(query)
        
        # Get comments with pagination
        cursor = comment_collection.find(query).skip(skip).limit(params.pagination_params.size)
        
        # Sort by created_at descending (newest first)
        cursor = cursor.sort("created_at", -1)
        
        comments = []
        for comment_doc in cursor:
            comment_model = CommentModel.from_bson(comment_doc)
            comment = Comment(
                id=str(comment_model.id),
                task_id=comment_model.task_id,
                account_id=comment_model.account_id,
                content=comment_model.content,
                created_at=comment_model.created_at,
                updated_at=comment_model.updated_at,
            )
            comments.append(comment)

        return PaginationResult(
            items=comments,
            total_count=total_count,
            page=params.pagination_params.page,
            size=params.pagination_params.size,
        ) 