from datetime import UTC, datetime

from modules.core.common.types import AuditActor, ResourceAction
from modules.task.errors import TaskNotFoundError
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.types import CreateTaskParams, DeleteTaskParams, Task, TaskDeletionResult, TaskQuery, UpdateTaskParams


class TaskWriter:
    @staticmethod
    def create_task(*, params: CreateTaskParams, actor: AuditActor) -> Task:
        task = Task(id="", account_id=params.account_id, description=params.description, title=params.title)
        return TaskRepository.create(task, actor=actor)

    @staticmethod
    def update_task(*, params: UpdateTaskParams, actor: AuditActor) -> Task:
        updated = TaskRepository.update_by_query(
            TaskQuery(id=params.task_id, account_id=params.account_id),
            {"description": params.description, "title": params.title},
            actor=actor,
        )
        if updated is None:
            raise TaskNotFoundError(task_id=params.task_id)
        return updated

    @staticmethod
    def delete_task(*, params: DeleteTaskParams, actor: AuditActor) -> TaskDeletionResult:
        deletion_time = datetime.now(UTC)
        deleted = TaskRepository.update_by_query(
            TaskQuery(id=params.task_id, account_id=params.account_id),
            {"active": False, "updated_at": deletion_time},
            actor=actor,
            action=ResourceAction.DELETE,
        )
        if deleted is None:
            raise TaskNotFoundError(task_id=params.task_id)

        return TaskDeletionResult(task_id=params.task_id, deleted_at=deletion_time, success=True)
