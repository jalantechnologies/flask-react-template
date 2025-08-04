from bson.objectid import ObjectId
from modules.application.common.base_model import BaseModel
from modules.application.common.types import PaginationResult
from modules.task.comments.errors import CommentNotFoundError
from modules.task.comments.internal.store.comment_repository import CommentRepository
from modules.task.comments.internal.comment_util import CommentUtil
from modules.task.comments.types import (
    GetPaginatedCommentsParams,
    GetCommentParams,
    Comment
)

class CommentReader:
    """
    Read operations for comment data access:
    Responsibility: Encapsulate all comment read operations
    - Single comment retrieval by ID
    - Paginated comment listing for tasks
    - Security filtering and validation
    - Data conversion and error handling

    """

    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        """
        Retrieve a specific comment by ID with security validations
        Security validation:
        - requires account_id, task_id and comment_id
        - ensure comment belings to specific task and account
        - prevent cross account and cross tasks access
        - return 404 for both missing and unauthoirised comments

        Query strategy:
        - use compound filter for efficeint lookup
        - leverage task_active_account_index for performance
        - single databse query with all constraints
        - fail fast approach for missing comments

        Error hanlding:
        - CommentNotFoundError for missing/unauthorised comments
        - Consistent error response regardless of failure reason
        - No information leakage about unauthorised resources
        """

        filter_query = {
            "_id": ObjectId(params.comment_id),
            "task_id": params.task_id,
            "account_id": params.account_id,
            "active": True, # Exclude soft deleted comments
        }

        comment_bson = CommentRepository.collection().find_one(filter_query)

        if comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)
        
        return CommentUtil.convert_comment_bson_to_comment(comment_bson)
    
    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        """
        Retrieve paginated list of comments for a specific task
        - uses skip/limit for database-level pagination
        - calculates total count for ui controls
        - provides total pages for navigation
        - efficient cursor iteration for large datasets

        Sorting
        - Default: created_at descending (newest first)
        - Secondary: _id descending (stable sort)
        - Allows custom sorting via SortParams
        - Optimized for chronological comment threads

        Security model:
        - Filters by account_id and task_id
        - Ensures only authorized comments are returned
        - No cross-account data leakage possible
        """

        filter_query = {
            "task_id": params.task_id,
            "account_id": params.account_id,
            "active": True, # Exclude soft deleted comments
        }

        total_count = CommentRepository.collection().count_documents(filter_query)

        pagination_params, skip, total_pages = BaseModel.calculate_pagination_values(
            params.pagination_params, total_count
        )

        # create base cursor
        cursor = CommentRepository.collection().find(filter_query)

        # Apply sorting logic
        if params.sort_params:
            cursor = BaseModel.apply_sort_params(cursor, params.sort_params)
        else:
            cursor = cursor.sort([("created_at", -1), ("_id", -1)])

        # Apply pagination and execute query
        comments_bson = list(cursor.skip(skip).limit(pagination_params.size))

        # convert all bson documents to business objects
        comments = [
            CommentUtil.convert_comment_bson_to_comment(comment_bson)
            for comment_bson in comments_bson
        ]

        return PaginationResult(
            items= comments,
            pagination_params= pagination_params,
            total_count=total_count,
            total_pages=total_pages
        )