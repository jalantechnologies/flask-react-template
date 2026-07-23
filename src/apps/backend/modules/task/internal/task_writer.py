from datetime import UTC, datetime

from modules.application.common.types import AuditActor
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.internal.task_reader import TaskReader
from modules.task.types import (
    CreateTaskParams,
    DeleteTaskParams,
    GetTaskParams,
    Task,
    TaskDeletionResult,
    UpdateTaskParams,
)


class TaskWriter:
    @staticmethod
    def create_task(*, params: CreateTaskParams, actor: AuditActor) -> Task:
        task = Task(id="", account_id=params.account_id, description=params.description, title=params.title)
        return TaskRepository.create(task, actor=actor)

    @staticmethod
    def update_task(*, params: UpdateTaskParams, actor: AuditActor) -> Task:
        # Confirm the task exists for this account (raises if not), keeping the update account-scoped.
        TaskReader.get_task(params=GetTaskParams(account_id=params.account_id, task_id=params.task_id))

        TaskRepository.update_fields(
            params.task_id, {"description": params.description, "title": params.title}, actor=actor
        )

        return TaskReader.get_task(params=GetTaskParams(account_id=params.account_id, task_id=params.task_id))

    @staticmethod
    def delete_task(*, params: DeleteTaskParams, actor: AuditActor) -> TaskDeletionResult:
        # Confirm the task exists for this account (raises if not) before soft-deleting it.
        task = TaskReader.get_task(params=GetTaskParams(account_id=params.account_id, task_id=params.task_id))

        deletion_time = datetime.now(UTC)
        TaskRepository.update_fields(task.id, {"active": False, "updated_at": deletion_time}, actor=actor)

        return TaskDeletionResult(task_id=params.task_id, deleted_at=deletion_time, success=True)
