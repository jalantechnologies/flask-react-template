from datetime import datetime

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
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
        self.account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="password", username="testuser@example.com"
            )
        )

    def test_create_task(self) -> None:
        task_params = CreateTaskParams(account_id=self.account.id, title="Test Task", description="This is a test task")
        task = TaskService.create_task(params=task_params)
        assert task.account_id == self.account.id
        assert task.title == "Test Task"
        assert task.description == "This is a test task"
        assert task.id is not None

    def test_get_task_for_account(self) -> None:
        task_params = CreateTaskParams(account_id=self.account.id, title="Test Task", description="This is a test task")
        created_task = TaskService.create_task(params=task_params)
        get_params = GetTaskParams(account_id=self.account.id, task_id=created_task.id)
        retrieved_task = TaskService.get_task_for_account(params=get_params)
        assert retrieved_task.id == created_task.id
        assert retrieved_task.account_id == self.account.id
        assert retrieved_task.title == "Test Task"
        assert retrieved_task.description == "This is a test task"

    def test_get_task_for_account_not_found(self) -> None:
        get_params = GetTaskParams(account_id=self.account.id, task_id="507f1f77bcf86cd799439011")
        with self.assertRaises(TaskNotFoundError) as context:
            TaskService.get_task_for_account(params=get_params)
        assert context.exception.code == TaskErrorCode.NOT_FOUND

    def test_get_paginated_tasks_for_account_empty(self) -> None:
        pagination_params = GetPaginatedTasksParams(account_id=self.account.id, page=1, size=10)
        result = TaskService.get_paginated_tasks_for_account(params=pagination_params)
        assert len(result.items) == 0
        assert result.total_count == 0
        assert result.total_pages == 0
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10

    def test_get_paginated_tasks_for_account_with_data(self) -> None:
        for i in range(5):
            task_params = CreateTaskParams(
                account_id=self.account.id, title=f"Task {i+1}", description=f"Description {i+1}"
            )
            TaskService.create_task(params=task_params)
        pagination_params = GetPaginatedTasksParams(account_id=self.account.id, page=1, size=3)
        result = TaskService.get_paginated_tasks_for_account(params=pagination_params)
        assert len(result.items) == 3
        assert result.total_count == 5
        assert result.total_pages == 2
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 3
        pagination_params = GetPaginatedTasksParams(account_id=self.account.id, page=2, size=3)
        result = TaskService.get_paginated_tasks_for_account(params=pagination_params)
        assert len(result.items) == 2
        assert result.total_count == 5
        assert result.total_pages == 2

    def test_get_paginated_tasks_default_pagination(self) -> None:
        task_params = CreateTaskParams(account_id=self.account.id, title="Test Task", description="This is a test task")
        TaskService.create_task(params=task_params)
        pagination_params = GetPaginatedTasksParams(account_id=self.account.id)
        result = TaskService.get_paginated_tasks_for_account(params=pagination_params)
        assert len(result.items) == 1
        assert result.total_count == 1
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 1

    def test_update_task(self) -> None:
        task_params = CreateTaskParams(
            account_id=self.account.id, title="Original Title", description="Original Description"
        )
        created_task = TaskService.create_task(params=task_params)
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
        update_params = UpdateTaskParams(
            account_id=self.account.id,
            task_id="507f1f77bcf86cd799439011",
            title="Updated Title",
            description="Updated Description",
        )
        with self.assertRaises(TaskNotFoundError) as context:
            TaskService.update_task(params=update_params)
        assert context.exception.code == TaskErrorCode.NOT_FOUND

    def test_delete_task(self) -> None:
        task_params = CreateTaskParams(account_id=self.account.id, title="Test Task", description="This is a test task")
        created_task = TaskService.create_task(params=task_params)
        delete_params = DeleteTaskParams(account_id=self.account.id, task_id=created_task.id)
        deletion_result = TaskService.delete_task(params=delete_params)
        assert deletion_result.task_id == created_task.id
        assert deletion_result.success is True
        assert deletion_result.deleted_at is not None
        assert isinstance(deletion_result.deleted_at, datetime)
        get_params = GetTaskParams(account_id=self.account.id, task_id=created_task.id)
        with self.assertRaises(TaskNotFoundError):
            TaskService.get_task_for_account(params=get_params)

    def test_delete_task_not_found(self) -> None:
        delete_params = DeleteTaskParams(account_id=self.account.id, task_id="507f1f77bcf86cd799439011")
        with self.assertRaises(TaskNotFoundError) as context:
            TaskService.delete_task(params=delete_params)
        assert context.exception.code == TaskErrorCode.NOT_FOUND

    def test_task_isolation_between_accounts(self) -> None:
        other_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Other", last_name="User", password="password", username="otheruser@example.com"
            )
        )
        task_params = CreateTaskParams(
            account_id=self.account.id, title="Account 1 Task", description="Task for account 1"
        )
        account1_task = TaskService.create_task(params=task_params)
        task_params = CreateTaskParams(
            account_id=other_account.id, title="Account 2 Task", description="Task for account 2"
        )
        account2_task = TaskService.create_task(params=task_params)
        pagination_params = GetPaginatedTasksParams(account_id=self.account.id)
        result = TaskService.get_paginated_tasks_for_account(params=pagination_params)
        assert len(result.items) == 1
        assert result.items[0].id == account1_task.id
        pagination_params = GetPaginatedTasksParams(account_id=other_account.id)
        result = TaskService.get_paginated_tasks_for_account(params=pagination_params)
        assert len(result.items) == 1
        assert result.items[0].id == account2_task.id
        get_params = GetTaskParams(account_id=self.account.id, task_id=account2_task.id)
        with self.assertRaises(TaskNotFoundError):
            TaskService.get_task_for_account(params=get_params)
