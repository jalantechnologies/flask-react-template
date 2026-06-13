from typing import Optional

from modules.application.common.types import PaginationResult
from modules.application.repository import SortSpec
from modules.task.errors import TaskNotFoundError
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.types import GetPaginatedTasksParams, GetTaskParams, Task, TaskQuery


class TaskReader:
    @staticmethod
    def get_task(*, params: GetTaskParams) -> Task:
        task = TaskRepository.query_one(TaskQuery(id=params.task_id, account_id=params.account_id))
        if task is None:
            raise TaskNotFoundError(task_id=params.task_id)
        return task

    @staticmethod
    def get_paginated_tasks(*, params: GetPaginatedTasksParams) -> PaginationResult[Task]:
        # An explicit sort request wins; otherwise the repository's default ordering (newest first) applies.
        sort: Optional[SortSpec] = None
        if params.sort_params:
            direction = params.sort_params.sort_direction.numeric_value
            sort = [(params.sort_params.sort_by, direction), ("_id", direction)]

        return TaskRepository.query_paginated(
            TaskQuery(account_id=params.account_id), params.pagination_params, sort=sort
        )
