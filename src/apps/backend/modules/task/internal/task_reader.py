from typing import List

from bson.objectid import ObjectId

from modules.task.errors import TaskNotFoundError
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.internal.task_util import TaskUtil
from modules.task.types import GetAllTasksParams, GetTaskParams, PaginationParams, Task


class TaskReader:
    @staticmethod
    def get_task_for_account(params: GetTaskParams) -> Task:
        task_bson = TaskRepository.collection().find_one(
            {"_id": ObjectId(params.task_id), "account_id": params.account_id, "active": True}
        )

        if task_bson is None:
            raise TaskNotFoundError(task_id=params.task_id)

        return TaskUtil.convert_task_bson_to_task(task_bson)

    @staticmethod
    def get_tasks_for_account(params: GetAllTasksParams) -> List[Task]:
        total_tasks_count = TaskRepository.collection().count_documents(
            {"account_id": params.account_id, "active": True}
        )

        pagination_params = PaginationParams(
            page=params.page if params.page else 1,
            size=params.size if params.size else total_tasks_count if total_tasks_count > 0 else 10,
        )

        start_index = (pagination_params.page - 1) * pagination_params.size

        tasks_cursor = (
            TaskRepository.collection()
            .find({"account_id": params.account_id, "active": True})
            .sort("created_at", -1)
            .skip(start_index)
            .limit(pagination_params.size)
        )

        tasks_bson = list(tasks_cursor)
        return [TaskUtil.convert_task_bson_to_task(task_bson) for task_bson in tasks_bson]
