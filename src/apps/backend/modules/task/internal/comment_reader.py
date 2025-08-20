from bson.objectid import ObjectId

from modules.application.common.base_model import BaseModel
from modules.application.common.types import PaginationResult
from modules.task.errors import CommentNotFoundError
from modules.task.internal.store.comment_repository import CommentRepository
from modules.task.internal.comment_util import CommentUtil
from modules.task.types import GetCommentParams, GetCommentsForTaskParams, Comment


class CommentReader:
    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        comment_bson = CommentRepository.collection().find_one(
            {
                "_id": ObjectId(params.comment_id),
                "task_id": params.task_id,
                "account_id": params.account_id,
                "active": True
            }
        )
        if comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)
        return CommentUtil.convert_comment_bson_to_comment(comment_bson)

    @staticmethod
    def get_comments_for_task(*, params: GetCommentsForTaskParams) -> PaginationResult[Comment]:
        filter_query = {"task_id": params.task_id, "account_id": params.account_id, "active": True}
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