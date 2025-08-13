from datetime import datetime

from modules.application.common.types import PaginationParams
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentNotFoundError
from modules.comment.types import (
    CommentErrorCode,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):
    def setUp(self) -> None:
        self.account = self.create_test_account()
        self.task = self.create_test_task(account_id=self.account.id)

    def test_create_comment(self) -> None:
        comment_params = CreateCommentParams(
            task_id=self.task.id,
            account_id=self.account.id,
            content=self.DEFAULT_COMMENT_CONTENT,
            author_name=self.DEFAULT_AUTHOR_NAME,
        )

        comment = CommentService.create_comment(params=comment_params)

        assert comment.task_id == self.task.id
        assert comment.account_id == self.account.id
        assert comment.content == self.DEFAULT_COMMENT_CONTENT
        assert comment.author_name == self.DEFAULT_AUTHOR_NAME
        assert comment.id is not None
        assert comment.active is True

    def test_get_comment_for_account(self) -> None:
        created_comment = self.create_test_comment(task_id=self.task.id, account_id=self.account.id)
        get_params = GetCommentParams(comment_id=created_comment.id, task_id=self.task.id, account_id=self.account.id)

        retrieved_comment = CommentService.get_comment(params=get_params)

        assert retrieved_comment.id == created_comment.id
        assert retrieved_comment.task_id == self.task.id
        assert retrieved_comment.account_id == self.account.id
        assert retrieved_comment.content == self.DEFAULT_COMMENT_CONTENT
        assert retrieved_comment.author_name == self.DEFAULT_AUTHOR_NAME

    def test_get_comment_for_account_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        get_params = GetCommentParams(
            comment_id=non_existent_comment_id, task_id=self.task.id, account_id=self.account.id
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.get_comment(params=get_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_get_paginated_comments_empty(self) -> None:
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedCommentsParams(
            task_id=self.task.id, account_id=self.account.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 0
        assert result.total_count == 0
        assert result.total_pages == 0
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10

    def test_get_paginated_comments_with_data(self) -> None:
        comments_count = 5
        self.create_multiple_test_comments(task_id=self.task.id, account_id=self.account.id, count=comments_count)
        pagination_params = PaginationParams(page=1, size=3, offset=0)
        get_params = GetPaginatedCommentsParams(
            task_id=self.task.id, account_id=self.account.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 3
        assert result.total_count == 5
        assert result.total_pages == 2
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 3

        pagination_params = PaginationParams(page=2, size=3, offset=0)
        get_params = GetPaginatedCommentsParams(
            task_id=self.task.id, account_id=self.account.id, pagination_params=pagination_params
        )
        result = CommentService.get_paginated_comments(params=get_params)
        assert len(result.items) == 2
        assert result.total_count == 5
        assert result.total_pages == 2

    def test_get_paginated_comments_default_pagination(self) -> None:
        self.create_test_comment(task_id=self.task.id, account_id=self.account.id)
        pagination_params = PaginationParams(page=1, size=1, offset=0)
        get_params = GetPaginatedCommentsParams(
            task_id=self.task.id, account_id=self.account.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 1
        assert result.total_count == 1
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 1

    def test_update_comment(self) -> None:
        created_comment = self.create_test_comment(
            task_id=self.task.id, account_id=self.account.id, content="Original Content", author_name="Original Author"
        )
        update_params = UpdateCommentParams(
            comment_id=created_comment.id, task_id=self.task.id, account_id=self.account.id, content="Updated Content"
        )

        updated_comment = CommentService.update_comment(params=update_params)

        assert updated_comment.id == created_comment.id
        assert updated_comment.task_id == self.task.id
        assert updated_comment.account_id == self.account.id
        assert updated_comment.content == "Updated Content"
        assert updated_comment.author_name == "Original Author"  # Should remain unchanged

    def test_update_comment_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_params = UpdateCommentParams(
            comment_id=non_existent_comment_id,
            task_id=self.task.id,
            account_id=self.account.id,
            content="Updated Content",
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.update_comment(params=update_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_delete_comment(self) -> None:
        created_comment = self.create_test_comment(task_id=self.task.id, account_id=self.account.id)
        delete_params = DeleteCommentParams(
            comment_id=created_comment.id, task_id=self.task.id, account_id=self.account.id
        )

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.comment_id == created_comment.id
        assert deletion_result.success is True
        assert deletion_result.deleted_at is not None
        assert isinstance(deletion_result.deleted_at, datetime)

        # Verify comment is soft deleted (should raise CommentNotFoundError)
        get_params = GetCommentParams(comment_id=created_comment.id, task_id=self.task.id, account_id=self.account.id)
        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_delete_comment_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        delete_params = DeleteCommentParams(
            comment_id=non_existent_comment_id, task_id=self.task.id, account_id=self.account.id
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.delete_comment(params=delete_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_comment_isolation_between_accounts(self) -> None:
        other_account = self.create_test_account(username="otheruser@example.com")
        other_task = self.create_test_task(account_id=other_account.id)

        account1_comment = self.create_test_comment(
            task_id=self.task.id,
            account_id=self.account.id,
            content="Account 1 Comment",
            author_name="Account 1 Author",
        )
        account2_comment = self.create_test_comment(
            task_id=other_task.id,
            account_id=other_account.id,
            content="Account 2 Comment",
            author_name="Account 2 Author",
        )

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params1 = GetPaginatedCommentsParams(
            task_id=self.task.id, account_id=self.account.id, pagination_params=pagination_params
        )
        account1_result = CommentService.get_paginated_comments(params=get_params1)

        get_params2 = GetPaginatedCommentsParams(
            task_id=other_task.id, account_id=other_account.id, pagination_params=pagination_params
        )
        account2_result = CommentService.get_paginated_comments(params=get_params2)

        assert len(account1_result.items) == 1
        assert account1_result.items[0].id == account1_comment.id

        assert len(account2_result.items) == 1
        assert account2_result.items[0].id == account2_comment.id

        # Verify account1 cannot access account2's comment
        get_params = GetCommentParams(comment_id=account2_comment.id, task_id=other_task.id, account_id=self.account.id)
        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_comment_isolation_between_tasks(self) -> None:
        task1 = self.create_test_task(account_id=self.account.id, title="Task 1")
        task2 = self.create_test_task(account_id=self.account.id, title="Task 2")

        task1_comment = self.create_test_comment(
            task_id=task1.id, account_id=self.account.id, content="Task 1 Comment", author_name="Task 1 Author"
        )
        task2_comment = self.create_test_comment(
            task_id=task2.id, account_id=self.account.id, content="Task 2 Comment", author_name="Task 2 Author"
        )

        # Verify comments are isolated by task
        pagination_params = PaginationParams(page=1, size=10, offset=0)

        get_params1 = GetPaginatedCommentsParams(
            task_id=task1.id, account_id=self.account.id, pagination_params=pagination_params
        )
        task1_result = CommentService.get_paginated_comments(params=get_params1)

        get_params2 = GetPaginatedCommentsParams(
            task_id=task2.id, account_id=self.account.id, pagination_params=pagination_params
        )
        task2_result = CommentService.get_paginated_comments(params=get_params2)

        assert len(task1_result.items) == 1
        assert task1_result.items[0].id == task1_comment.id
        assert task1_result.items[0].task_id == task1.id

        assert len(task2_result.items) == 1
        assert task2_result.items[0].id == task2_comment.id
        assert task2_result.items[0].task_id == task2.id

        # Verify comment from task1 cannot be accessed via task2's context
        get_params = GetCommentParams(comment_id=task1_comment.id, task_id=task2.id, account_id=self.account.id)
        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_comment_creation_with_whitespace_trimming(self) -> None:
        comment_params = CreateCommentParams(
            task_id=self.task.id,
            account_id=self.account.id,
            content="  Content with whitespace  ",
            author_name="  Author with whitespace  ",
        )

        comment = CommentService.create_comment(params=comment_params)

        # Note: Whitespace trimming happens in the API layer, not service layer
        assert comment.content == "  Content with whitespace  "
        assert comment.author_name == "  Author with whitespace  "

    def test_comment_update_with_whitespace_trimming(self) -> None:
        created_comment = self.create_test_comment(task_id=self.task.id, account_id=self.account.id)
        update_params = UpdateCommentParams(
            comment_id=created_comment.id,
            task_id=self.task.id,
            account_id=self.account.id,
            content="  Updated content with whitespace  ",
        )

        updated_comment = CommentService.update_comment(params=update_params)

        # Note: Whitespace trimming happens in the API layer, not service layer
        assert updated_comment.content == "  Updated content with whitespace  "
        assert updated_comment.author_name == created_comment.author_name  # Should remain unchanged
