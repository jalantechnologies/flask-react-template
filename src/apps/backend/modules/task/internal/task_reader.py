from bson.objectid import ObjectId

from modules.application.common.base_model import BaseModel
from modules.application.common.types import PaginationResult
from modules.task.errors import TaskNotFoundError
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.internal.task_util import TaskUtil
from modules.task.types import GetPaginatedTasksParams, GetTaskParams, Task


class TaskReader:
    @staticmethod
    def get_task(*, params: GetTaskParams) -> Task:
        task_bson = TaskRepository.collection().find_one(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True}
        )
        if task_bson is None:
            raise TaskNotFoundError(task_id=params.task_id)
        return TaskUtil.convert_task_bson_to_task(task_bson)

    @staticmethod
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
