from datetime import datetime

from modules.application.common.types import PaginationParams
from modules.comment.errors import CommentNotFoundError
from modules.comment.comment_service import CommentService
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetPaginatedCommentsParams,
    GetCommentParams,
    CommentErrorCode,
    UpdateCommentParams,
)
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
        get_params = GetCommentParams(account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id)

        retrieved_comment = CommentService.get_comment(params=get_params)

        assert retrieved_comment.id == created_comment.id
        assert retrieved_comment.task_id == self.task.id
        assert retrieved_comment.account_id == self.account.id
        assert retrieved_comment.content == self.DEFAULT_COMMENT_CONTENT

    def test_get_comment_for_task_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        get_params = GetCommentParams(account_id=self.account.id, task_id=self.task.id, comment_id=non_existent_comment_id)

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

    def test_get_paginated_comments_with_data(self) -> None:
        comments = self.create_multiple_test_comments(account_id=self.account.id, task_id=self.task.id, count=3)
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 3
        assert result.total_count == 3
        # Comments should be sorted by created_at in descending order
        assert result.items[0].content == "Comment 3"
        assert result.items[1].content == "Comment 2" 
        assert result.items[2].content == "Comment 1"

    def test_get_paginated_comments_default_pagination(self) -> None:
        # Create more comments than the default page size
        self.create_multiple_test_comments(account_id=self.account.id, task_id=self.task.id, count=15)
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 10
        assert result.total_count == 15

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
        delete_params = DeleteCommentParams(account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id)

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.comment_id == created_comment.id
        assert deletion_result.success is True
        assert deletion_result.deleted_at is not None
        assert isinstance(deletion_result.deleted_at, datetime)

        get_params = GetCommentParams(account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id)
        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_delete_comment_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        delete_params = DeleteCommentParams(account_id=self.account.id, task_id=self.task.id, comment_id=non_existent_comment_id)

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.delete_comment(params=delete_params)

        assert context.exception.code == CommentErrorCode.NOT_FOUND

    def test_comment_isolation_between_tasks(self) -> None:
        # Create another task
        task2 = self.create_test_task(account_id=self.account.id, title="Task 2")
        
        # Create comments on different tasks
        comment_task1 = self.create_test_comment(account_id=self.account.id, task_id=self.task.id, content="Comment on Task 1")
        comment_task2 = self.create_test_comment(account_id=self.account.id, task_id=task2.id, content="Comment on Task 2")

        # Get comments for task1 - should only see comment for task1
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params_task1 = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )
        result_task1 = CommentService.get_paginated_comments(params=get_params_task1)

        assert len(result_task1.items) == 1
        assert result_task1.items[0].content == "Comment on Task 1"
        assert result_task1.items[0].task_id == self.task.id

        # Get comments for task2 - should only see comment for task2
        get_params_task2 = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=task2.id, pagination_params=pagination_params
        )
        result_task2 = CommentService.get_paginated_comments(params=get_params_task2)

        assert len(result_task2.items) == 1
        assert result_task2.items[0].content == "Comment on Task 2"
        assert result_task2.items[0].task_id == task2.id
