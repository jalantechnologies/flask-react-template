import unittest
from datetime import datetime

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.application.common.types import PaginationParams
from modules.logger.logger_manager import LoggerManager
from modules.task.errors import CommentNotFoundError
from modules.task.internal.store.comment_repository import CommentRepository
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.comment_service import CommentService
from modules.task.types import (
    CreateCommentParams,
    CreateTaskParams,
    DeleteCommentParams,
    GetCommentParams,
    GetCommentsForTaskParams,
    UpdateCommentParams,
)


class TestCommentService(unittest.TestCase):

    def setUp(self) -> None:
        LoggerManager.mount_logger()

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def create_test_account(self):
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser@example.com",
                password="testpassword",
                first_name="Test",
                last_name="User",
            )
        )

    def create_test_task(self, account_id: str):
        return TaskService.create_task(
            params=CreateTaskParams(
                account_id=account_id,
                title="Test Task",
                description="Test Description",
            )
        )

    def test_create_comment_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        params = CreateCommentParams(
            task_id=task.id,
            account_id=account.id,
            content="Test comment content"
        )

        comment = CommentService.create_comment(params=params)

        assert comment.id is not None
        assert comment.task_id == task.id
        assert comment.account_id == account.id
        assert comment.content == "Test comment content"
        assert isinstance(comment.created_at, datetime)
        assert isinstance(comment.updated_at, datetime)

    def test_get_comment_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task.id,
                account_id=account.id,
                content="Test comment"
            )
        )

        params = GetCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id
        )

        retrieved_comment = CommentService.get_comment(params=params)

        assert retrieved_comment.id == created_comment.id
        assert retrieved_comment.task_id == created_comment.task_id
        assert retrieved_comment.account_id == created_comment.account_id
        assert retrieved_comment.content == created_comment.content

    def test_get_comment_not_found(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        params = GetCommentParams(
            comment_id="507f1f77bcf86cd799439011",  # Non-existent ID
            task_id=task.id,
            account_id=account.id
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=params)

    def test_get_comment_unauthorized_different_account(self) -> None:
        account1 = self.create_test_account()
        account2 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser2@example.com",
                password="testpassword2",
                first_name="Test2",
                last_name="User2",
            )
        )
        task = self.create_test_task(account_id=account1.id)
        
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task.id,
                account_id=account1.id,
                content="Test comment"
            )
        )

        params = GetCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account2.id  # Different account
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=params)

    def test_get_task_comments_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        # Create multiple comments
        comment1 = CommentService.create_comment(
            params=CreateCommentParams(task_id=task.id, account_id=account.id, content="Comment 1")
        )
        comment2 = CommentService.create_comment(
            params=CreateCommentParams(task_id=task.id, account_id=account.id, content="Comment 2")
        )
        comment3 = CommentService.create_comment(
            params=CreateCommentParams(task_id=task.id, account_id=account.id, content="Comment 3")
        )

        params = GetCommentsForTaskParams(
            task_id=task.id,
            account_id=account.id,
            pagination_params=PaginationParams(page=1, size=10, offset=0)
        )

        result = CommentService.get_comments_for_task(params=params)

        assert result.total_count == 3
        assert len(result.items) == 3
        # Should be sorted by created_at desc
        assert result.items[0].content == "Comment 3"
        assert result.items[1].content == "Comment 2"
        assert result.items[2].content == "Comment 1"

    def test_get_task_comments_pagination(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        # Create 5 comments
        for i in range(5):
            CommentService.create_comment(
                params=CreateCommentParams(task_id=task.id, account_id=account.id, content=f"Comment {i+1}")
            )

        # Get first page
        params = GetCommentsForTaskParams(
            task_id=task.id,
            account_id=account.id,
            pagination_params=PaginationParams(page=1, size=2, offset=0)
        )

        result = CommentService.get_comments_for_task(params=params)

        assert result.total_count == 5
        assert len(result.items) == 2
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 2

    def test_update_comment_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task.id,
                account_id=account.id,
                content="Original content"
            )
        )

        params = UpdateCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id,
            content="Updated content"
        )

        updated_comment = CommentService.update_comment(params=params)

        assert updated_comment.id == created_comment.id
        assert updated_comment.content == "Updated content"
        assert updated_comment.updated_at > created_comment.updated_at

    def test_update_comment_not_found(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        params = UpdateCommentParams(
            comment_id="507f1f77bcf86cd799439011",  # Non-existent ID
            task_id=task.id,
            account_id=account.id,
            content="Updated content"
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.update_comment(params=params)

    def test_update_comment_unauthorized_different_account(self) -> None:
        account1 = self.create_test_account()
        account2 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser2@example.com",
                password="testpassword2",
                first_name="Test2",
                last_name="User2",
            )
        )
        task = self.create_test_task(account_id=account1.id)
        
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task.id,
                account_id=account1.id,
                content="Original content"
            )
        )

        params = UpdateCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account2.id,  # Different account
            content="Hacked content"
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.update_comment(params=params)

    def test_delete_comment_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task.id,
                account_id=account.id,
                content="Comment to delete"
            )
        )

        params = DeleteCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id
        )

        result = CommentService.delete_comment(params=params)

        assert result.comment_id == created_comment.id
        assert result.success is True
        assert isinstance(result.deleted_at, datetime)

        # Verify comment is soft deleted
        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(
                params=GetCommentParams(
                    comment_id=created_comment.id,
                    task_id=task.id,
                    account_id=account.id
                )
            )

    def test_delete_comment_not_found(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        
        params = DeleteCommentParams(
            comment_id="507f1f77bcf86cd799439011",  # Non-existent ID
            task_id=task.id,
            account_id=account.id
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.delete_comment(params=params)

    def test_delete_comment_unauthorized_different_account(self) -> None:
        account1 = self.create_test_account()
        account2 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="testuser2@example.com",
                password="testpassword2",
                first_name="Test2",
                last_name="User2",
            )
        )
        task = self.create_test_task(account_id=account1.id)
        
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task.id,
                account_id=account1.id,
                content="Comment to delete"
            )
        )

        params = DeleteCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account2.id  # Different account
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.delete_comment(params=params)