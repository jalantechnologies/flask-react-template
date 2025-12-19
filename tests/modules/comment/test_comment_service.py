from datetime import datetime

from modules.application.common.types import PaginationParams
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentNotFoundError
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    CommentErrorCode,
    UpdateCommentParams,
)
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):
    def setUp(self) -> None:
        super().setUp()
        self.account = self.create_test_account()
        self.task = self.create_test_task(account_id=self.account.id)

    def test_create_comment(self) -> None:
        comment_params = CreateCommentParams(
            account_id=self.account.id, task_id=self.task.id, content=self.DEFAULT_COMMENT_CONTENT
        )

        comment = CommentService.create_comment(params=comment_params)

        assert comment.account_id == self.account.id
        assert comment.task_id == self.task.id
        assert comment.content == self.DEFAULT_COMMENT_CONTENT
        assert comment.id is not None

    def test_get_comment_for_task(self) -> None:
        created_comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)
        get_params = GetCommentParams(
            account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id
        )

        retrieved_comment = CommentService.get_comment(params=get_params)

        assert retrieved_comment.id == created_comment.id
        assert retrieved_comment.account_id == self.account.id
        assert retrieved_comment.task_id == self.task.id
        assert retrieved_comment.content == self.DEFAULT_COMMENT_CONTENT

    def test_get_comment_for_task_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        get_params = GetCommentParams(
            account_id=self.account.id, task_id=self.task.id, comment_id=non_existent_comment_id
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.get_comment(params=get_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_get_paginated_comments_empty(self) -> None:
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 0
        assert result.total_count == 0
        assert result.total_pages == 0
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10

    def test_get_paginated_comments_with_data(self) -> None:
        comments_count = 5
        self.create_multiple_test_comments(account_id=self.account.id, task_id=self.task.id, count=comments_count)
        pagination_params = PaginationParams(page=1, size=3, offset=0)
        get_params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 3
        assert result.total_count == 5
        assert result.total_pages == 2
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 3

        pagination_params = PaginationParams(page=2, size=3, offset=0)
        get_params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )
        result = CommentService.get_paginated_comments(params=get_params)
        assert len(result.items) == 2
        assert result.total_count == 5
        assert result.total_pages == 2

    def test_get_paginated_comments_default_pagination(self) -> None:
        self.create_test_comment(account_id=self.account.id, task_id=self.task.id)
        pagination_params = PaginationParams(page=1, size=1, offset=0)
        get_params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 1
        assert result.total_count == 1
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 1

    def test_update_comment(self) -> None:
        created_comment = self.create_test_comment(
            account_id=self.account.id, task_id=self.task.id, content="Original Content"
        )
        update_params = UpdateCommentParams(
            account_id=self.account.id,
            task_id=self.task.id,
            comment_id=created_comment.id,
            content="Updated Content",
        )

        updated_comment = CommentService.update_comment(params=update_params)

        assert updated_comment.id == created_comment.id
        assert updated_comment.account_id == self.account.id
        assert updated_comment.task_id == self.task.id
        assert updated_comment.content == "Updated Content"

    def test_update_comment_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_params = UpdateCommentParams(
            account_id=self.account.id,
            task_id=self.task.id,
            comment_id=non_existent_comment_id,
            content="Updated Content",
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.update_comment(params=update_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_delete_comment(self) -> None:
        created_comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)
        delete_params = DeleteCommentParams(
            account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id
        )

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.comment_id == created_comment.id
        assert deletion_result.success is True
        assert deletion_result.deleted_at is not None
        assert isinstance(deletion_result.deleted_at, datetime)

        get_params = GetCommentParams(
            account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id
        )
        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_delete_comment_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        delete_params = DeleteCommentParams(
            account_id=self.account.id, task_id=self.task.id, comment_id=non_existent_comment_id
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.delete_comment(params=delete_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_comment_isolation_between_accounts(self) -> None:
        other_account = self.create_test_account(username="otheruser@example.com")
        other_task = self.create_test_task(account_id=other_account.id)

        account1_comment = self.create_test_comment(
            account_id=self.account.id, task_id=self.task.id, content="Account 1 Comment"
        )
        account2_comment = self.create_test_comment(
            account_id=other_account.id, task_id=other_task.id, content="Account 2 Comment"
        )

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params1 = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )
        account1_result = CommentService.get_paginated_comments(params=get_params1)

        get_params2 = GetPaginatedCommentsParams(
            account_id=other_account.id, task_id=other_task.id, pagination_params=pagination_params
        )
        account2_result = CommentService.get_paginated_comments(params=get_params2)

        assert len(account1_result.items) == 1
        assert account1_result.items[0].id == account1_comment.id

        assert len(account2_result.items) == 1
        assert account2_result.items[0].id == account2_comment.id

        get_params = GetCommentParams(
            account_id=self.account.id, task_id=self.task.id, comment_id=account2_comment.id
        )
        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)

