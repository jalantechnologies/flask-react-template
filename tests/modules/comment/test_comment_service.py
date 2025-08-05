from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.application.common.types import PaginationParams
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentNotFoundError
from modules.comment.types import (
    CommentErrorCode,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentParams,
    UpdateCommentParams,
)
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):

    def test_create_comment(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )

        comment = CommentService.create_comment(
            params=CreateCommentParams(account_id=account.id, task_id=task.id, content="Test comment")
        )

        assert comment.account_id == account.id
        assert comment.task_id == task.id
        assert comment.content == "Test comment"
        assert comment.id is not None

    def test_get_comment_for_account(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(account_id=account.id, task_id=task.id, content="Test comment")
        )

        comment = CommentService.get_comment(
            params=GetCommentParams(account_id=account.id, task_id=task.id, comment_id=created_comment.id)
        )

        assert comment.id == created_comment.id
        assert comment.account_id == account.id
        assert comment.task_id == task.id
        assert comment.content == "Test comment"

    def test_get_comment_for_account_not_found(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )
        fake_comment_id = "507f1f77bcf86cd799439011"

        try:
            CommentService.get_comment(
                params=GetCommentParams(account_id=account.id, task_id=task.id, comment_id=fake_comment_id)
            )
            assert False, "Should have raised CommentNotFoundError"
        except CommentNotFoundError as exc:
            assert exc.code == CommentErrorCode.NOT_FOUND

    def test_get_paginated_comments_empty(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        result = CommentService.get_paginated_comments(
            params=GetPaginatedCommentParams(
                account_id=account.id, task_id=task.id, pagination_params=pagination_params
            )
        )

        assert len(result.items) == 0
        assert result.total_count == 0
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10

    def test_get_paginated_comments_with_data(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )

        # Create multiple comments
        for i in range(5):
            CommentService.create_comment(
                params=CreateCommentParams(account_id=account.id, task_id=task.id, content=f"Comment {i+1}")
            )

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        result = CommentService.get_paginated_comments(
            params=GetPaginatedCommentParams(
                account_id=account.id, task_id=task.id, pagination_params=pagination_params
            )
        )

        assert len(result.items) == 5
        assert result.total_count == 5
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10

    def test_get_paginated_comments_default_pagination(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )

        # Create multiple comments
        for i in range(15):
            CommentService.create_comment(
                params=CreateCommentParams(account_id=account.id, task_id=task.id, content=f"Comment {i+1}")
            )

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        result = CommentService.get_paginated_comments(
            params=GetPaginatedCommentParams(
                account_id=account.id, task_id=task.id, pagination_params=pagination_params
            )
        )

        assert len(result.items) == 10  # Page size limit
        assert result.total_count == 15
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10

    def test_update_comment(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(account_id=account.id, task_id=task.id, content="Original content")
        )

        updated_comment = CommentService.update_comment(
            params=UpdateCommentParams(
                account_id=account.id, task_id=task.id, comment_id=created_comment.id, content="Updated content"
            )
        )

        assert updated_comment.id == created_comment.id
        assert updated_comment.account_id == account.id
        assert updated_comment.task_id == task.id
        assert updated_comment.content == "Updated content"

    def test_update_comment_not_found(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )
        fake_comment_id = "507f1f77bcf86cd799439011"

        try:
            CommentService.update_comment(
                params=UpdateCommentParams(
                    account_id=account.id, task_id=task.id, comment_id=fake_comment_id, content="Updated content"
                )
            )
            assert False, "Should have raised CommentNotFoundError"
        except CommentNotFoundError as exc:
            assert exc.code == CommentErrorCode.NOT_FOUND

    def test_delete_comment(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(account_id=account.id, task_id=task.id, content="Test comment")
        )

        deletion_result = CommentService.delete_comment(
            params=DeleteCommentParams(account_id=account.id, task_id=task.id, comment_id=created_comment.id)
        )

        assert deletion_result.comment_id == created_comment.id
        assert deletion_result.success is True
        assert deletion_result.deleted_at is not None

        # Verify comment is actually deleted
        try:
            CommentService.get_comment(
                params=GetCommentParams(account_id=account.id, task_id=task.id, comment_id=created_comment.id)
            )
            assert False, "Should have raised CommentNotFoundError after deletion"
        except CommentNotFoundError:
            pass  # Expected

    def test_delete_comment_not_found(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )
        fake_comment_id = "507f1f77bcf86cd799439011"

        try:
            CommentService.delete_comment(
                params=DeleteCommentParams(account_id=account.id, task_id=task.id, comment_id=fake_comment_id)
            )
            assert False, "Should have raised CommentNotFoundError"
        except CommentNotFoundError as exc:
            assert exc.code == CommentErrorCode.NOT_FOUND

    def test_comment_isolation_between_accounts(self) -> None:
        # Create two accounts
        account1 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="user1", password="password", first_name="User", last_name="One"
            )
        )
        account2 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="user2", password="password", first_name="User", last_name="Two"
            )
        )

        # Create tasks for each account
        task1 = TaskService.create_task(
            params=CreateTaskParams(account_id=account1.id, title="Task 1", description="Description 1")
        )
        task2 = TaskService.create_task(
            params=CreateTaskParams(account_id=account2.id, title="Task 2", description="Description 2")
        )

        # Create comments for each account
        comment1 = CommentService.create_comment(
            params=CreateCommentParams(account_id=account1.id, task_id=task1.id, content="Comment by user 1")
        )
        comment2 = CommentService.create_comment(
            params=CreateCommentParams(account_id=account2.id, task_id=task2.id, content="Comment by user 2")
        )

        # Account1 should only see their own comments
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        result1 = CommentService.get_paginated_comments(
            params=GetPaginatedCommentParams(
                account_id=account1.id, task_id=task1.id, pagination_params=pagination_params
            )
        )
        assert len(result1.items) == 1
        assert result1.items[0].content == "Comment by user 1"

        # Account2 should only see their own comments
        result2 = CommentService.get_paginated_comments(
            params=GetPaginatedCommentParams(
                account_id=account2.id, task_id=task2.id, pagination_params=pagination_params
            )
        )
        assert len(result2.items) == 1
        assert result2.items[0].content == "Comment by user 2"

    def test_comment_isolation_between_tasks(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser", password="password", first_name="Test", last_name="User"
            )
        )

        # Create two tasks
        task1 = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Task 1", description="Description 1")
        )
        task2 = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Task 2", description="Description 2")
        )

        # Create comments for each task
        comment1 = CommentService.create_comment(
            params=CreateCommentParams(account_id=account.id, task_id=task1.id, content="Comment for task 1")
        )
        comment2 = CommentService.create_comment(
            params=CreateCommentParams(account_id=account.id, task_id=task2.id, content="Comment for task 2")
        )

        # Task1 should only show its own comments
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        result1 = CommentService.get_paginated_comments(
            params=GetPaginatedCommentParams(
                account_id=account.id, task_id=task1.id, pagination_params=pagination_params
            )
        )
        assert len(result1.items) == 1
        assert result1.items[0].content == "Comment for task 1"

        # Task2 should only show its own comments
        result2 = CommentService.get_paginated_comments(
            params=GetPaginatedCommentParams(
                account_id=account.id, task_id=task2.id, pagination_params=pagination_params
            )
        )
        assert len(result2.items) == 1
        assert result2.items[0].content == "Comment for task 2"
