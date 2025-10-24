from modules.comments.comments_service import CommentService
from modules.comments.types import CreateCommentParams, DeleteCommentParams, GetCommentsParams, UpdateCommentParams
from tests.modules.comments.base_test_comments import BaseTestComments


class TestCommentsService(BaseTestComments):
    def setUp(self) -> None:
        self.account = self.create_test_account()

    def test_create_comment(self) -> None:
        comment_params = CreateCommentParams(
            account_id=self.account.id, task_id=self.DEFAULT_TASK_ID, text=self.DEFAULT_COMMENT_TEXT
        )

        comment = CommentService.create_comment(params=comment_params)

        assert comment.account_id == self.account.id
        assert comment.task_id == self.DEFAULT_TASK_ID
        assert comment.text == self.DEFAULT_COMMENT_TEXT
        assert comment.id is not None
        assert comment.created_at is not None

    def test_get_comments_for_task(self) -> None:
        comments = self.create_multiple_test_comments(account_id=self.account.id, task_id=self.DEFAULT_TASK_ID, count=3)

        get_params = GetCommentsParams(account_id=self.account.id, task_id=self.DEFAULT_TASK_ID)

        retrieved_comments = CommentService.get_comments(params=get_params)

        assert len(retrieved_comments) == 3
        assert retrieved_comments[0].id == comments[2].id
        assert retrieved_comments[1].id == comments[1].id
        assert retrieved_comments[2].id == comments[0].id

    def test_get_comments_empty(self) -> None:
        get_params = GetCommentsParams(account_id=self.account.id, task_id=self.DEFAULT_TASK_ID)

        comments = CommentService.get_comments(params=get_params)

        assert len(comments) == 0

    def test_update_comment(self) -> None:
        created_comment = self.create_test_comment(
            account_id=self.account.id, task_id=self.DEFAULT_TASK_ID, text="Original text"
        )

        update_params = UpdateCommentParams(
            account_id=self.account.id, task_id=self.DEFAULT_TASK_ID, comment_id=created_comment.id, text="Updated text"
        )

        updated_comment = CommentService.update_comment(params=update_params)

        assert updated_comment.id == created_comment.id
        assert updated_comment.account_id == self.account.id
        assert updated_comment.task_id == self.DEFAULT_TASK_ID
        assert updated_comment.text == "Updated text"
        assert updated_comment.updated_at is not None

    def test_update_comment_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_params = UpdateCommentParams(
            account_id=self.account.id,
            task_id=self.DEFAULT_TASK_ID,
            comment_id=non_existent_comment_id,
            text="Updated text",
        )

        updated_comment = CommentService.update_comment(params=update_params)

        assert updated_comment is None

    def test_delete_comment(self) -> None:
        created_comment = self.create_test_comment(account_id=self.account.id, task_id=self.DEFAULT_TASK_ID)

        delete_params = DeleteCommentParams(
            account_id=self.account.id, task_id=self.DEFAULT_TASK_ID, comment_id=created_comment.id
        )

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.success is True
        assert deletion_result.comment_id == created_comment.id

        get_params = GetCommentsParams(account_id=self.account.id, task_id=self.DEFAULT_TASK_ID)
        comments = CommentService.get_comments(params=get_params)
        assert len(comments) == 0

    def test_delete_comment_not_found(self) -> None:
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        delete_params = DeleteCommentParams(
            account_id=self.account.id, task_id=self.DEFAULT_TASK_ID, comment_id=non_existent_comment_id
        )

        deletion_result = CommentService.delete_comment(params=delete_params)

        assert deletion_result.success is False
        assert deletion_result.comment_id == non_existent_comment_id

    def test_comment_isolation_between_accounts(self) -> None:
        other_account = self.create_test_account(username="otheruser@example.com")

        account1_comment = self.create_test_comment(
            account_id=self.account.id, task_id=self.DEFAULT_TASK_ID, text="Account 1 comment"
        )
        account2_comment = self.create_test_comment(
            account_id=other_account.id, task_id=self.DEFAULT_TASK_ID, text="Account 2 comment"
        )

        get_params1 = GetCommentsParams(account_id=self.account.id, task_id=self.DEFAULT_TASK_ID)
        account1_comments = CommentService.get_comments(params=get_params1)

        get_params2 = GetCommentsParams(account_id=other_account.id, task_id=self.DEFAULT_TASK_ID)
        account2_comments = CommentService.get_comments(params=get_params2)

        assert len(account1_comments) == 1
        assert account1_comments[0].id == account1_comment.id

        assert len(account2_comments) == 1
        assert account2_comments[0].id == account2_comment.id

    def test_comment_isolation_between_tasks(self) -> None:
        task1_id = "task-1"
        task2_id = "task-2"

        comment1 = self.create_test_comment(account_id=self.account.id, task_id=task1_id)
        comment2 = self.create_test_comment(account_id=self.account.id, task_id=task2_id)

        get_params1 = GetCommentsParams(account_id=self.account.id, task_id=task1_id)
        task1_comments = CommentService.get_comments(params=get_params1)

        get_params2 = GetCommentsParams(account_id=self.account.id, task_id=task2_id)
        task2_comments = CommentService.get_comments(params=get_params2)

        assert len(task1_comments) == 1
        assert task1_comments[0].id == comment1.id

        assert len(task2_comments) == 1
        assert task2_comments[0].id == comment2.id
