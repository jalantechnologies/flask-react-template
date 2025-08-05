from bson.objectid import ObjectId

from modules.application.common.types import PaginationResult
from modules.comment.errors import CommentNotFoundError
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import Comment, GetCommentParams, GetPaginatedCommentsParams


class CommentReader:
    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        comment_bson = CommentRepository.collection().find_one(
            {
                "_id": ObjectId(params.comment_id),
                "task_id": params.task_id,
                "account_id": params.account_id,
                "active": True,
            }
        )

        if comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)

        return CommentUtil.convert_comment_bson_to_comment(comment_bson)

    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        skip = (params.pagination_params.page - 1) * params.pagination_params.per_page
        limit = params.pagination_params.per_page

        sort_field = "created_at"
        sort_direction = -1

        if params.sort_params:
            sort_field = params.sort_params.sort_by
            sort_direction = 1 if params.sort_params.sort_order == "asc" else -1

        cursor = CommentRepository.collection().find(
            {
                "task_id": params.task_id,
                "account_id": params.account_id,
                "active": True,
            }
        ).sort(sort_field, sort_direction).skip(skip).limit(limit)

        comments = [CommentUtil.convert_comment_bson_to_comment(comment_bson) for comment_bson in cursor]

        total_count = CommentRepository.collection().count_documents(
            {
                "task_id": params.task_id,
                "account_id": params.account_id,
                "active": True,
            }
        )

        return PaginationResult(
            items=comments,
            total_count=total_count,
            page=params.pagination_params.page,
            per_page=params.pagination_params.per_page,
        ) 