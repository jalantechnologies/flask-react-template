from datetime import datetime

from modules.application.common.types import PaginationParams
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentNotFoundError, CommentTaskNotFoundError
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

    def test_create_comment_success(self) -> None:
        params = CreateCommentParams(account_id=self.account.id, task_id=self.task.id, content="Test comment content")

        comment = CommentService.create_comment(params=params)

        assert comment.account_id == self.account.id
        assert comment.task_id == self.task.id
        assert comment.content == "Test comment content"
        assert comment.id is not None

    def test_create_comment_nonexistent_task(self) -> None:
        params = CreateCommentParams(
            account_id=self.account.id, task_id="64f123456789abcdef123456", content="Test comment"
        )

        try:
            CommentService.create_comment(params=params)
            assert False, "Expected CommentTaskNotFoundError"
        except CommentTaskNotFoundError as e:
            assert e.code == CommentErrorCode.TASK_NOT_FOUND
            assert e.http_code == 404

    def test_get_comment_success(self) -> None:
        created_comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        params = GetCommentParams(account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id)
        retrieved_comment = CommentService.get_comment(params=params)

        assert retrieved_comment.id == created_comment.id
        assert retrieved_comment.account_id == created_comment.account_id
        assert retrieved_comment.task_id == created_comment.task_id
        assert retrieved_comment.content == created_comment.content

    def test_get_comment_nonexistent_comment(self) -> None:
        params = GetCommentParams(
            account_id=self.account.id, task_id=self.task.id, comment_id="64f123456789abcdef123456"
        )

        try:
            CommentService.get_comment(params=params)
            assert False, "Expected CommentNotFoundError"
        except CommentNotFoundError as e:
            assert e.code == CommentErrorCode.NOT_FOUND
            assert e.http_code == 404

    def test_get_comment_nonexistent_task(self) -> None:
        params = GetCommentParams(
            account_id=self.account.id, task_id="64f123456789abcdef123456", comment_id="64f123456789abcdef123456"
        )

        try:
            CommentService.get_comment(params=params)
            assert False, "Expected CommentTaskNotFoundError"
        except CommentTaskNotFoundError as e:
            assert e.code == CommentErrorCode.TASK_NOT_FOUND
            assert e.http_code == 404

    def test_get_paginated_comments_success(self) -> None:
        self.create_multiple_test_comments(account_id=self.account.id, task_id=self.task.id, count=5)

        pagination_params = PaginationParams(page=1, size=3, offset=0)
        params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=params)

        assert result.total_count == 5
        assert len(result.items) == 3
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 3

        for comment in result.items:
            assert comment.account_id == self.account.id
            assert comment.task_id == self.task.id

    def test_get_paginated_comments_empty_results(self) -> None:
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id=self.task.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=params)

        assert result.total_count == 0
        assert len(result.items) == 0

    def test_get_paginated_comments_nonexistent_task(self) -> None:
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        params = GetPaginatedCommentsParams(
            account_id=self.account.id, task_id="64f123456789abcdef123456", pagination_params=pagination_params
        )

        try:
            CommentService.get_paginated_comments(params=params)
            assert False, "Expected CommentTaskNotFoundError"
        except CommentTaskNotFoundError as e:
            assert e.code == CommentErrorCode.TASK_NOT_FOUND
            assert e.http_code == 404

    def test_update_comment_success(self) -> None:
        created_comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        params = UpdateCommentParams(
            account_id=self.account.id,
            task_id=self.task.id,
            comment_id=created_comment.id,
            content="Updated comment content",
        )

        updated_comment = CommentService.update_comment(params=params)

        assert updated_comment.id == created_comment.id
        assert updated_comment.account_id == created_comment.account_id
        assert updated_comment.task_id == created_comment.task_id
        assert updated_comment.content == "Updated comment content"

    def test_update_comment_nonexistent_comment(self) -> None:
        params = UpdateCommentParams(
            account_id=self.account.id,
            task_id=self.task.id,
            comment_id="64f123456789abcdef123456",
            content="Updated content",
        )

        try:
            CommentService.update_comment(params=params)
            assert False, "Expected CommentNotFoundError"
        except CommentNotFoundError as e:
            assert e.code == CommentErrorCode.NOT_FOUND
            assert e.http_code == 404

    def test_update_comment_nonexistent_task(self) -> None:
        params = UpdateCommentParams(
            account_id=self.account.id,
            task_id="64f123456789abcdef123456",
            comment_id="64f123456789abcdef123456",
            content="Updated content",
        )

        try:
            CommentService.update_comment(params=params)
            assert False, "Expected CommentTaskNotFoundError"
        except CommentTaskNotFoundError as e:
            assert e.code == CommentErrorCode.TASK_NOT_FOUND
            assert e.http_code == 404

    def test_delete_comment_success(self) -> None:
        created_comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        params = DeleteCommentParams(account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id)

        result = CommentService.delete_comment(params=params)

        assert result.comment_id == created_comment.id
        assert result.success is True
        assert isinstance(result.deleted_at, datetime)

        try:
            CommentService.get_comment(
                params=GetCommentParams(account_id=self.account.id, task_id=self.task.id, comment_id=created_comment.id)
            )
            assert False, "Expected CommentNotFoundError after deletion"
        except CommentNotFoundError:
            pass

    def test_delete_comment_nonexistent_comment(self) -> None:
        params = DeleteCommentParams(
            account_id=self.account.id, task_id=self.task.id, comment_id="64f123456789abcdef123456"
        )

        try:
            CommentService.delete_comment(params=params)
            assert False, "Expected CommentNotFoundError"
        except CommentNotFoundError as e:
            assert e.code == CommentErrorCode.NOT_FOUND
            assert e.http_code == 404

    def test_cross_task_comment_access_denied(self) -> None:
        other_task = self.create_test_task(account_id=self.account.id, title="Other task")
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        params = GetCommentParams(account_id=self.account.id, task_id=other_task.id, comment_id=comment.id)

        try:
            CommentService.get_comment(params=params)
            assert False, "Expected CommentNotFoundError for cross-task access"
        except CommentNotFoundError as e:
            assert e.code == CommentErrorCode.NOT_FOUND
            assert e.http_code == 404
