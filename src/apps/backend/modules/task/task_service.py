from modules.application.common.types import AuditActor, PaginationResult
from modules.task.internal.task_reader import TaskReader
from modules.task.internal.task_writer import TaskWriter
from modules.task.types import (
    CreateTaskParams,
    DeleteTaskParams,
    GetPaginatedTasksParams,
    GetTaskParams,
    Task,
    TaskDeletionResult,
    UpdateTaskParams,
)


class TaskService:
    @staticmethod
    def create_task(*, params: CreateTaskParams, actor: AuditActor) -> Task:
        return TaskWriter.create_task(params=params, actor=actor)

    @staticmethod
    def get_task(*, params: GetTaskParams, actor: AuditActor) -> Task:
        return TaskReader.get_task(params=params, actor=actor)

    @staticmethod
    def get_paginated_tasks(*, params: GetPaginatedTasksParams, actor: AuditActor) -> PaginationResult[Task]:
        return TaskReader.get_paginated_tasks(params=params, actor=actor)

    @staticmethod
    def update_task(*, params: UpdateTaskParams, actor: AuditActor) -> Task:
        return TaskWriter.update_task(params=params, actor=actor)

    @staticmethod
    def delete_task(*, params: DeleteTaskParams, actor: AuditActor) -> TaskDeletionResult:
        return TaskWriter.delete_task(params=params, actor=actor)
