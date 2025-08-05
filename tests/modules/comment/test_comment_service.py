from datetime import datetime

from modules.application.common.types import PaginationParams
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentNotFoundError
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)
from modules.task.internal.store.task_model import TaskModel
from modules.task.internal.store.task_repository import TaskRepository
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):

    def test_create_comment_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)

        create_params = CreateCommentParams(
            task_id=task.id,
            account_id=account.id,
            content=self.DEFAULT_COMMENT_CONTENT,
        )

        comment = CommentService.create_comment(params=create_params)

        assert comment.id is not None
        assert comment.task_id == task.id
        assert comment.account_id == account.id
        assert comment.content == self.DEFAULT_COMMENT_CONTENT
        assert comment.created_at is not None
        assert comment.updated_at is not None

    def test_create_comment_task_not_found(self) -> None:
        account = self.create_test_account()
        non_existent_task_id = "507f1f77bcf86cd799439011"

        create_params = CreateCommentParams(
            task_id=non_existent_task_id,
            account_id=account.id,
            content=self.DEFAULT_COMMENT_CONTENT,
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.create_comment(params=create_params)

        assert "Task with id" in str(context.exception)

    def test_get_comment_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(task_id=task.id, account_id=account.id)

        get_params = GetCommentParams(task_id=task.id, comment_id=str(created_comment.id))

        comment = CommentService.get_comment(params=get_params)

        assert comment.id == str(created_comment.id)
        assert comment.task_id == task.id
        assert comment.account_id == account.id
        assert comment.content == self.DEFAULT_COMMENT_CONTENT

    def test_get_comment_not_found(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        get_params = GetCommentParams(task_id=task.id, comment_id=non_existent_comment_id)

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.get_comment(params=get_params)

        assert "Comment with id" in str(context.exception)

    def test_get_paginated_comments_empty(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedCommentsParams(
            task_id=task.id,
            pagination_params=pagination_params,
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert result.items == []
        assert result.total_count == 0
        assert result.page == 1
        assert result.size == 10

    def test_get_paginated_comments_with_comments(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(task_id=task.id, account_id=account.id, count=3)

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedCommentsParams(
            task_id=task.id,
            pagination_params=pagination_params,
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 3
        assert result.total_count == 3
        assert result.page == 1
        assert result.size == 10

        # Comments should be ordered by created_at desc (newest first)
        assert result.items[0].content == "Comment 3"
        assert result.items[1].content == "Comment 2"
        assert result.items[2].content == "Comment 1"

    def test_get_paginated_comments_with_pagination(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        self.create_multiple_test_comments(task_id=task.id, account_id=account.id, count=5)

        # First page
        pagination_params1 = PaginationParams(page=1, size=2, offset=0)
        get_params1 = GetPaginatedCommentsParams(
            task_id=task.id,
            pagination_params=pagination_params1,
        )

        result1 = CommentService.get_paginated_comments(params=get_params1)

        assert len(result1.items) == 2
        assert result1.total_count == 5
        assert result1.page == 1
        assert result1.size == 2

        # Second page
        pagination_params2 = PaginationParams(page=2, size=2, offset=0)
        get_params2 = GetPaginatedCommentsParams(
            task_id=task.id,
            pagination_params=pagination_params2,
        )

        result2 = CommentService.get_paginated_comments(params=get_params2)

        assert len(result2.items) == 2
        assert result2.total_count == 5
        assert result2.page == 2
        assert result2.size == 2

    def test_get_paginated_comments_task_not_found(self) -> None:
        account = self.create_test_account()
        non_existent_task_id = "507f1f77bcf86cd799439011"

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedCommentsParams(
            task_id=non_existent_task_id,
            pagination_params=pagination_params,
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.get_paginated_comments(params=get_params)

        assert "Task with id" in str(context.exception)

    def test_update_comment_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(task_id=task.id, account_id=account.id)
        updated_content = "Updated comment content"

        update_params = UpdateCommentParams(
            task_id=task.id,
            comment_id=str(created_comment.id),
            content=updated_content,
        )

        comment = CommentService.update_comment(params=update_params)

        assert comment.id == str(created_comment.id)
        assert comment.task_id == task.id
        assert comment.account_id == account.id
        assert comment.content == updated_content

    def test_update_comment_not_found(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        update_params = UpdateCommentParams(
            task_id=task.id,
            comment_id=non_existent_comment_id,
            content="Updated content",
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.update_comment(params=update_params)

        assert "Comment with id" in str(context.exception)

    def test_delete_comment_success(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(task_id=task.id, account_id=account.id)

        delete_params = DeleteCommentParams(
            task_id=task.id,
            comment_id=str(created_comment.id),
        )

        result = CommentService.delete_comment(params=delete_params)

        assert result.comment_id == str(created_comment.id)
        assert result.success is True
        assert result.deleted_at is not None

        # Verify comment is soft deleted
        deleted_comment = CommentRepository.get_comment(comment_id=str(created_comment.id))
        assert deleted_comment is None

    def test_delete_comment_not_found(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        delete_params = DeleteCommentParams(
            task_id=task.id,
            comment_id=non_existent_comment_id,
        )

        with self.assertRaises(CommentNotFoundError) as context:
            CommentService.delete_comment(params=delete_params)

        assert "Comment with id" in str(context.exception) 