from bson.objectid import ObjectId

from modules.application.common.base_model import BaseModel
from modules.application.common.types import PaginationResult
from modules.comment.errors import CommentNotFoundError
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import Comment, GetCommentParams, GetPaginatedCommentsParams


class CommentReader:
    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        # If task_id is provided, use it for filtering, otherwise just get by comment_id
        if params.task_id:
            comment_bson = CommentRepository.collection().find_one(
                {"_id": ObjectId(params.comment_id), "task_id": params.task_id, "active": True}
            )
        else:
            comment_bson = CommentRepository.collection().find_one({"_id": ObjectId(params.comment_id), "active": True})
        if comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)
        return CommentUtil.convert_comment_bson_to_comment(comment_bson)

    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        filter_query = {"task_id": params.task_id, "active": True}
        total_count = CommentRepository.collection().count_documents(filter_query)
        pagination_params, skip, total_pages = BaseModel.calculate_pagination_values(
            params.pagination_params, total_count
        )
        cursor = CommentRepository.collection().find(filter_query)

        if params.sort_params:
            cursor = BaseModel.apply_sort_params(cursor, params.sort_params)
        else:
            cursor = cursor.sort([("created_at", -1), ("_id", -1)])

        comments_bson = list(cursor.skip(skip).limit(pagination_params.size))
        comments = [CommentUtil.convert_comment_bson_to_comment(comment_bson) for comment_bson in comments_bson]
        return PaginationResult(
            items=comments, pagination_params=pagination_params, total_count=total_count, total_pages=total_pages
        )
