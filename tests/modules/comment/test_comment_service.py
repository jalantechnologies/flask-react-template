from datetime import datetime

from modules.comment.types import (
    CreateCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
)
from modules.comment.comment_service import CommentService
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):
    def setUp(self) -> None:

        self.account = self.create_test_account()
        self.task = self.create_test_task(account_id=self.account.id)

    def test_create_comment(self) -> None:
        params = CreateCommentParams(
            task_id=self.task.id,
            account_id=self.account.id,
            content="Test comment",
        )

        comment = CommentService.create_comment(params=params)

        assert comment.task_id == self.task.id
        assert comment.account_id == self.account.id
        assert comment.content == "Test comment"
        assert comment.id is not None


    def test_update_comment(self) -> None:
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(
                task_id=self.task.id,
                account_id=self.account.id,
                content="Original content",
            )
        )

        update_params = UpdateCommentParams(
            task_id=self.task.id,
            comment_id=created_comment.id,
            content="Updated content",
        )

        updated_comment = CommentService.update_comment(params=update_params)

        assert updated_comment.id == created_comment.id
        assert updated_comment.content == "Updated content"


    def test_delete_comment(self) -> None:
        created_comment = CommentService.create_comment(
            params=CreateCommentParams(
                task_id=self.task.id,
                account_id=self.account.id,
                content="Comment to delete",
            )
        )

        delete_params = DeleteCommentParams(
            task_id=self.task.id,
            comment_id=created_comment.id,
        )

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.comment_id == created_comment.id
        assert deletion_result.success is True
        assert isinstance(deletion_result.deleted_at, datetime)


    def test_get_comments_by_task_id(self) -> None:

        CommentService.create_comment(
            params=CreateCommentParams(
                task_id=self.task.id, account_id=self.account.id, content="Comment 1"
            )
        )
        CommentService.create_comment(
            params=CreateCommentParams(
                task_id=self.task.id, account_id=self.account.id, content="Comment 2"
            )
        )

        comments = CommentService.get_comments_by_task_id(self.task.id)

        assert len(comments) == 2
        assert comments[0].content == "Comment 1"
        assert comments[1].content == "Comment 2"
