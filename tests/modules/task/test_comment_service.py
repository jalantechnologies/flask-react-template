from modules.task.comment_service import CommentService
from modules.task.errors import CommentValidationError
from modules.task.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetTaskCommentsParams,
    UpdateCommentParams,
)
from tests.modules.task.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):
    def setUp(self):
        super().setUp()

    def test_create_comment_success(self):
        # Arrange
        task = self.create_test_task()
        create_params = CreateCommentParams(
            account_id="test_account_id", task_id=str(task.id), content="Test comment content"
        )

        # Act
        result = CommentService.create_comment(params=create_params)

        # Assert
        self.assertEqual(result.task_id, str(task.id))
        self.assertEqual(result.account_id, "test_account_id")
        self.assertEqual(result.content, "Test comment content")
        self.assertIsNotNone(result.id)

    def test_create_comment_empty_content(self):
        # Arrange
        task = self.create_test_task()
        create_params = CreateCommentParams(account_id="test_account_id", task_id=str(task.id), content="")

        # Act & Assert
        with self.assertRaises(CommentValidationError) as context:
            CommentService.create_comment(params=create_params)
        self.assertIn("Comment content cannot be empty", str(context.exception))

    def test_create_comment_task_not_found(self):
        # Arrange
        create_params = CreateCommentParams(
            account_id="test_account_id", task_id="non_existent_task_id", content="Test comment content"
        )

        # Act & Assert
        with self.assertRaises(CommentValidationError) as context:
            CommentService.create_comment(params=create_params)
        self.assertIn("Task not found", str(context.exception))

    def test_get_comment_success(self):
        # Arrange
        task = self.create_test_task()
        comment = self.create_test_comment(str(task.id))
        get_params = GetCommentParams(account_id="test_account_id", task_id=str(task.id), comment_id=str(comment.id))

        # Act
        result = CommentService.get_comment(params=get_params)

        # Assert
        self.assertEqual(result.id, str(comment.id))
        self.assertEqual(result.task_id, str(task.id))
        self.assertEqual(result.account_id, "test_account_id")
        self.assertEqual(result.content, "Test Comment")

    def test_get_comment_not_found(self):
        # Arrange
        task = self.create_test_task()
        get_params = GetCommentParams(
            account_id="test_account_id", task_id=str(task.id), comment_id="non_existent_comment_id"
        )

        # Act & Assert
        with self.assertRaises(CommentValidationError) as context:
            CommentService.get_comment(params=get_params)
        self.assertIn("Comment not found", str(context.exception))

    def test_get_task_comments_success(self):
        # Arrange
        task = self.create_test_task()
        comment1 = self.create_test_comment(str(task.id), content="Comment 1")
        comment2 = self.create_test_comment(str(task.id), content="Comment 2")
        get_params = GetTaskCommentsParams(
            account_id="test_account_id", task_id=str(task.id), pagination_params=self.create_pagination_params()
        )

        # Act
        result = CommentService.get_task_comments(params=get_params)

        # Assert
        self.assertEqual(result.total_count, 2)
        self.assertEqual(len(result.items), 2)
        # Check that both comments are present (order may vary due to timing)
        comment_contents = [comment.content for comment in result.items]
        self.assertIn("Comment 1", comment_contents)
        self.assertIn("Comment 2", comment_contents)

    def test_update_comment_success(self):
        # Arrange
        task = self.create_test_task()
        comment = self.create_test_comment(str(task.id))
        update_params = UpdateCommentParams(
            account_id="test_account_id",
            task_id=str(task.id),
            comment_id=str(comment.id),
            content="Updated comment content",
        )

        # Act
        result = CommentService.update_comment(params=update_params)

        # Assert
        self.assertEqual(result.id, str(comment.id))
        self.assertEqual(result.content, "Updated comment content")
        self.assertNotEqual(result.updated_at, comment.updated_at)

    def test_update_comment_not_found(self):
        # Arrange
        task = self.create_test_task()
        update_params = UpdateCommentParams(
            account_id="test_account_id",
            task_id=str(task.id),
            comment_id="non_existent_comment_id",
            content="Updated comment content",
        )

        # Act & Assert
        with self.assertRaises(CommentValidationError) as context:
            CommentService.update_comment(params=update_params)
        self.assertIn("Comment not found", str(context.exception))

    def test_delete_comment_success(self):
        # Arrange
        task = self.create_test_task()
        comment = self.create_test_comment(str(task.id))
        delete_params = DeleteCommentParams(
            account_id="test_account_id", task_id=str(task.id), comment_id=str(comment.id)
        )

        # Act
        result = CommentService.delete_comment(params=delete_params)

        # Assert
        self.assertTrue(result)
        deleted_comment = self.get_comment_by_id(str(comment.id))
        self.assertIsNone(deleted_comment)

    def test_delete_comment_not_found(self):
        # Arrange
        task = self.create_test_task()
        delete_params = DeleteCommentParams(
            account_id="test_account_id", task_id=str(task.id), comment_id="non_existent_comment_id"
        )

        # Act & Assert
        with self.assertRaises(CommentValidationError) as context:
            CommentService.delete_comment(params=delete_params)
        self.assertIn("Comment not found", str(context.exception))
