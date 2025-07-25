import math
from typing import List

from bson.objectid import ObjectId

from modules.application.common.types import PaginationParams
from modules.task.errors import TaskNotFoundError
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.internal.task_util import TaskUtil
from modules.task.types import GetPaginatedTasksParams, GetTaskParams, PaginatedTasksResult, Task


class TaskReader:
    @staticmethod
    def get_task_for_account(*, params: GetTaskParams) -> Task:
        task_bson = TaskRepository.collection().find_one(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True}
        )

        if task_bson is None:
            raise TaskNotFoundError(task_id=params.task_id)

        return TaskUtil.convert_task_bson_to_task(task_bson)

    @staticmethod
    def get_paginated_tasks_for_account(*, params: GetPaginatedTasksParams) -> PaginatedTasksResult:
        total_tasks_count = TaskRepository.collection().count_documents(
            {"account_id": params.account_id, "active": True}
        )

        page = params.page if params.page else 1

        if params.size:
            size = params.size
        elif total_tasks_count > 0:
            size = total_tasks_count
        else:
            size = 10

        pagination_params = PaginationParams(page=page, size=size)

        total_pages = math.ceil(total_tasks_count / pagination_params.size) if pagination_params.size > 0 else 0

        start_index = (pagination_params.page - 1) * pagination_params.size

        tasks_cursor = (
            TaskRepository.collection()
            .find({"account_id": params.account_id, "active": True})
            .sort([("created_at", -1), ("_id", -1)])
            .skip(start_index)
            .limit(pagination_params.size)
        )

        tasks_bson = list(tasks_cursor)
        tasks = [TaskUtil.convert_task_bson_to_task(task_bson) for task_bson in tasks_bson]

        return PaginatedTasksResult(
            items=tasks, pagination_params=pagination_params, total_count=total_tasks_count, total_pages=total_pages
        )
