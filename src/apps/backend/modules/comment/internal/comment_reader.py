from bson.objectid import ObjectId
from modules.application.common.base_model import BaseModel
from modules.application.common.types import PaginationResult
from modules.comment.errors import CommentNotFoundError
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.types import GetPaginatedCommentsParams, GetCommentParams, Comment


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
        filter_query = {
            "task_id": params.task_id,
            "account_id": params.account_id,
            "active": True
        }
        
        total_count = CommentRepository.collection().count_documents(filter_query)
        pagination_params, skip, total_pages = BaseModel.calculate_pagination_values(
            params.pagination_params, total_count
        )

        # Default sort by created_at descending (newest first)
        sort_criteria = [("created_at", -1)]
        if params.sort_params:
            sort_criteria = [(params.sort_params.field, 1 if params.sort_params.order == "asc" else -1)]

        cursor = CommentRepository.collection().find(filter_query).sort(sort_criteria).skip(skip).limit(
            pagination_params.size
        )
        
        comments = [CommentUtil.convert_comment_bson_to_comment(comment_bson) for comment_bson in cursor]

        return PaginationResult(
            items=comments,
            pagination_params=pagination_params,
            total_count=total_count,
            total_pages=total_pages,
        )