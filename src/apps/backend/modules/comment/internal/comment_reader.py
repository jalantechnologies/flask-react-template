from bson.objectid import ObjectId
from pymongo import DESCENDING

from modules.application.common.types import PaginationResult, PaginationParams, SortParams
from modules.comment.errors import CommentNotFoundError
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import (
    Comment,
    GetCommentParams,
    GetPaginatedCommentsParams,
)


class CommentReader:
    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        comment_bson = CommentRepository.collection().find_one({
            "_id": ObjectId(params.comment_id),
            "task_id": params.task_id,
            "account_id": params.account_id,
            "active": True
        })
        
        if comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)

        return CommentUtil.convert_comment_bson_to_comment(comment_bson)

    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        # Build the query filter
        query_filter = {
            "task_id": params.task_id,
            "account_id": params.account_id,
            "active": True
        }

        # Setup sorting - default to newest first
        sort_order = DESCENDING
        sort_field = "created_at"
        
        if params.sort_params and params.sort_params.sort_by:
            sort_field = params.sort_params.sort_by
            sort_order = params.sort_params.sort_direction.numeric_value

        # Calculate pagination
        offset = (params.pagination_params.page - 1) * params.pagination_params.size
        
        # Get total count
        total_count = CommentRepository.collection().count_documents(query_filter)
        
        # Get paginated results
        comment_cursor = (
            CommentRepository.collection()
            .find(query_filter)
            .sort(sort_field, sort_order)
            .skip(offset)
            .limit(params.pagination_params.size)
        )

        comments = [CommentUtil.convert_comment_bson_to_comment(comment_bson) for comment_bson in comment_cursor]

        # Calculate total pages
        total_pages = (total_count + params.pagination_params.size - 1) // params.pagination_params.size

        return PaginationResult(
            items=comments,
            pagination_params=params.pagination_params,
            total_count=total_count,
            total_pages=total_pages
        )
