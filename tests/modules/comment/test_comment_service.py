from modules.comment.comment_service import CommentService
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)
from modules.application.common.types import PaginationParams
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):

    def test_create_comment(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account.id)

        create_params = CreateCommentParams(
            task_id=task.id, account_id=account.id, content=self.DEFAULT_COMMENT_CONTENT
        )

        created_comment = CommentService.create_comment(params=create_params)

        assert created_comment.task_id == task.id
        assert created_comment.account_id == account.id
        assert created_comment.content == self.DEFAULT_COMMENT_CONTENT
        assert created_comment.id is not None

    def test_get_comment(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        get_params = GetCommentParams(task_id=task.id, account_id=account.id, comment_id=comment.id)

        retrieved_comment = CommentService.get_comment(params=get_params)

        assert retrieved_comment.id == comment.id
        assert retrieved_comment.task_id == task.id
        assert retrieved_comment.account_id == account.id
        assert retrieved_comment.content == comment.content

    def test_get_paginated_comments(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account.id)
        self.create_multiple_test_comments(task.id, account.id, 5)

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        get_params = GetPaginatedCommentsParams(
            task_id=task.id, account_id=account.id, pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=get_params)

        assert len(result.items) == 5
        assert result.total_count == 5
        assert result.pagination_params.page == 1
        assert result.pagination_params.size == 10

    def test_update_comment(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)
        updated_content = "Updated comment content"

        update_params = UpdateCommentParams(
            task_id=task.id, account_id=account.id, comment_id=comment.id, content=updated_content
        )

        updated_comment = CommentService.update_comment(params=update_params)

        assert updated_comment.id == comment.id
        assert updated_comment.task_id == task.id
        assert updated_comment.account_id == account.id
        assert updated_comment.content == updated_content

    def test_delete_comment(self) -> None:
        account = self.create_test_account()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        delete_params = DeleteCommentParams(task_id=task.id, account_id=account.id, comment_id=comment.id)

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.success is True
