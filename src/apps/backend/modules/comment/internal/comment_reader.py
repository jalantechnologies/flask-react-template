from dataclasses import asdict

from bson.objectid import ObjectId

from modules.application.common.base_model import BaseModel
from modules.application.common.types import PaginationResult
from modules.comment.internal.comment_util import CommentUtil
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import Comment, GetCommentParams
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.internal.task_util import TaskUtil
from modules.task.types import GetPaginatedTasksParams, GetTaskParams, Task


class CommentReader:
    @staticmethod
    def get_comment(*, params: GetTaskParams):
        comment_bsons = CommentRepository.collection().find(
            {"account_id": params.account_id, "task_id": params.task_id}
        )
        return {
            "items": [
                asdict(CommentUtil.convert_comment_bson_to_comment(comment_bson))
                for comment_bson in list(comment_bsons)
            ]
        }

    @staticmethod
    def get_comment_by_id(*, params: GetCommentParams) -> Comment:
        comment_bsons = CommentRepository.collection().find_one(
            {"account_id": params.account_id, "task_id": params.task_id, "_id": ObjectId(params.comment_id)}
        )
        return CommentUtil.convert_comment_bson_to_comment(comment_bsons)

    def get_paginated_tasks(*, params: GetPaginatedTasksParams) -> PaginationResult[Task]:
        filter_query = {"account_id": params.account_id, "active": True}
        total_count = TaskRepository.collection().count_documents(filter_query)
        pagination_params, skip, total_pages = BaseModel.calculate_pagination_values(
            params.pagination_params, total_count
        )
        cursor = TaskRepository.collection().find(filter_query)

        if params.sort_params:
            cursor = BaseModel.apply_sort_params(cursor, params.sort_params)
        else:
            cursor = cursor.sort([("created_at", -1), ("_id", -1)])

        tasks_bson = list(cursor.skip(skip).limit(pagination_params.size))
        tasks = [TaskUtil.convert_task_bson_to_task(task_bson) for task_bson in tasks_bson]
        return PaginationResult(
            items=tasks, pagination_params=pagination_params, total_count=total_count, total_pages=total_pages
        )
