from bson.errors import InvalidId
from bson.objectid import ObjectId

from modules.application.common.types import PaginationResult
from modules.task.errors import CommentValidationError
from modules.task.internal.comment_util import CommentUtil
from modules.task.internal.store.comment_repository import CommentRepository
from modules.task.types import Comment, GetCommentParams, GetTaskCommentsParams


class CommentReader:
    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        try:
            object_id = ObjectId(params.comment_id)
        except InvalidId:
            raise CommentValidationError("Comment not found")

        comment_bson = CommentRepository.collection().find_one(
            {"_id": object_id, "task_id": params.task_id, "account_id": params.account_id, "active": True}
        )

        if not comment_bson:
            raise CommentValidationError("Comment not found")

        return CommentUtil.convert_comment_bson_to_comment(comment_bson)

    @staticmethod
    def get_task_comments(*, params: GetTaskCommentsParams) -> PaginationResult:
        CommentUtil.validate_task_exists(params.task_id, params.account_id)

        skip = (params.pagination_params.page - 1) * params.pagination_params.size
        limit = params.pagination_params.size

        comment_bsons = list(
            CommentRepository.collection().find(
                {"task_id": params.task_id, "active": True}, sort=[("created_at", -1)], skip=skip, limit=limit
            )
        )

        total_count = CommentRepository.collection().count_documents({"task_id": params.task_id, "active": True})
        total_pages = (total_count + params.pagination_params.size - 1) // params.pagination_params.size

        comments = [CommentUtil.convert_comment_bson_to_comment(comment_bson) for comment_bson in comment_bsons]

        return PaginationResult(
            items=comments, total_count=total_count, pagination_params=params.pagination_params, total_pages=total_pages
        )
