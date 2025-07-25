from datetime import datetime

from modules.application.common.types import PaginationParams
from modules.task.errors import TaskNotFoundError
from modules.task.task_service import TaskService
from modules.task.types import (
    CreateTaskParams,
    DeleteTaskParams,
    GetPaginatedTasksParams,
    GetTaskParams,
    TaskErrorCode,
    UpdateTaskParams,
)
from tests.modules.task.base_test_task import BaseTestTask


class TestTaskService(BaseTestTask):
    def setUp(self) -> None:
        self.account = self.create_test_account()

    def test_create_task(self) -> None:
        task_params = CreateTaskParams(
            account_id=self.account.id, title=self.DEFAULT_TASK_TITLE, description=self.DEFAULT_TASK_DESCRIPTION
        )

        task = TaskService.create_task(params=task_params)

        assert task.account_id == self.account.id
        assert task.title == self.DEFAULT_TASK_TITLE
        assert task.description == self.DEFAULT_TASK_DESCRIPTION
        assert task.id is not None

    def test_get_task_for_account(self) -> None:
        created_task = self.create_test_task(account_id=self.account.id)
        get_params = GetTaskParams(account_id=self.account.id, task_id=created_task.id)

        retrieved_task = TaskService.get_task(params=get_params)

        assert retrieved_task.id == created_task.id
        assert retrieved_task.account_id == self.account.id
        assert retrieved_task.title == self.DEFAULT_TASK_TITLE
        assert retrieved_task.description == self.DEFAULT_TASK_DESCRIPTION

    def test_get_task_for_account_not_found(self) -> None:
        non_existent_task_id = "507f1f77bcf86cd799439011"
        get_params = GetTaskParams(account_id=self.account.id, task_id=non_existent_task_id)

        with self.assertRaises(TaskNotFoundError) as context:
            TaskService.get_task(params=get_params)

        assert context.exception.code == TaskErrorCode.NOT_FOUND

    def test_get_paginated_tasks_empty(self) -> None:
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedTasksParams(account_id=self.account.id, pagination_params=pagination_params)

        result = TaskService.get_paginated_tasks(params=get_params)

        assert len(result.items) == 0
        assert result.total_count == 0
        assert result.total_pages == 0
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10

    def test_get_paginated_tasks_with_data(self) -> None:
        tasks_count = 5
        self.create_multiple_test_tasks(account_id=self.account.id, count=tasks_count)
        pagination_params = PaginationParams(page=1, size=3, offset=0)
        get_params = GetPaginatedTasksParams(account_id=self.account.id, pagination_params=pagination_params)

        result = TaskService.get_paginated_tasks(params=get_params)

        assert len(result.items) == 3
        assert result.total_count == 5
        assert result.total_pages == 2
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 3

        pagination_params = PaginationParams(page=2, size=3, offset=0)
        get_params = GetPaginatedTasksParams(account_id=self.account.id, pagination_params=pagination_params)
        result = TaskService.get_paginated_tasks(params=get_params)
        assert len(result.items) == 2
        assert result.total_count == 5
        assert result.total_pages == 2

    def test_get_paginated_tasks_default_pagination(self) -> None:
        self.create_test_task(account_id=self.account.id)
        pagination_params = PaginationParams(page=1, size=1, offset=0)
        get_params = GetPaginatedTasksParams(account_id=self.account.id, pagination_params=pagination_params)

        result = TaskService.get_paginated_tasks(params=get_params)

        assert len(result.items) == 1
        assert result.total_count == 1
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 1

    def test_update_task(self) -> None:
        created_task = self.create_test_task(
            account_id=self.account.id, title="Original Title", description="Original Description"
        )
        update_params = UpdateTaskParams(
            account_id=self.account.id,
            task_id=created_task.id,
            title="Updated Title",
            description="Updated Description",
        )

        updated_task = TaskService.update_task(params=update_params)

        assert updated_task.id == created_task.id
        assert updated_task.account_id == self.account.id
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"

    def test_update_task_not_found(self) -> None:
        non_existent_task_id = "507f1f77bcf86cd799439011"
        update_params = UpdateTaskParams(
            account_id=self.account.id,
            task_id=non_existent_task_id,
            title="Updated Title",
            description="Updated Description",
        )

        with self.assertRaises(TaskNotFoundError) as context:
            TaskService.update_task(params=update_params)

        assert context.exception.code == TaskErrorCode.NOT_FOUND

    def test_delete_task(self) -> None:
        created_task = self.create_test_task(account_id=self.account.id)
        delete_params = DeleteTaskParams(account_id=self.account.id, task_id=created_task.id)

        deletion_result = TaskService.delete_task(params=delete_params)

        assert deletion_result.task_id == created_task.id
        assert deletion_result.success is True
        assert deletion_result.deleted_at is not None
        assert isinstance(deletion_result.deleted_at, datetime)

        get_params = GetTaskParams(account_id=self.account.id, task_id=created_task.id)
        with self.assertRaises(TaskNotFoundError):
            TaskService.get_task(params=get_params)

    def test_delete_task_not_found(self) -> None:
        non_existent_task_id = "507f1f77bcf86cd799439011"
        delete_params = DeleteTaskParams(account_id=self.account.id, task_id=non_existent_task_id)

        with self.assertRaises(TaskNotFoundError) as context:
            TaskService.delete_task(params=delete_params)

        assert context.exception.code == TaskErrorCode.NOT_FOUND

    def test_task_isolation_between_accounts(self) -> None:
        other_account = self.create_test_account(username="otheruser@example.com")

        account1_task = self.create_test_task(
            account_id=self.account.id, title="Account 1 Task", description="Task for account 1"
        )
        account2_task = self.create_test_task(
            account_id=other_account.id, title="Account 2 Task", description="Task for account 2"
        )

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params1 = GetPaginatedTasksParams(account_id=self.account.id, pagination_params=pagination_params)
        account1_result = TaskService.get_paginated_tasks(params=get_params1)

        get_params2 = GetPaginatedTasksParams(account_id=other_account.id, pagination_params=pagination_params)
        account2_result = TaskService.get_paginated_tasks(params=get_params2)

        assert len(account1_result.items) == 1
        assert account1_result.items[0].id == account1_task.id

        assert len(account2_result.items) == 1
        assert account2_result.items[0].id == account2_task.id

        get_params = GetTaskParams(account_id=self.account.id, task_id=account2_task.id)
        with self.assertRaises(TaskNotFoundError):
            TaskService.get_task(params=get_params)
