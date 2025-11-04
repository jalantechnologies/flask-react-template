import unittest
from datetime import datetime

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.application.common.types import PaginationParams
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentNotFoundError
from modules.comment.types import (
    CreateCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
    DeleteCommentParams,
)
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):
    def test_create_comment_success(self):
        """Test successful comment creation"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        params = CreateCommentParams(
            task_id=task.id,
            account_id=account.id,
            content="This is a test comment"
        )

        comment = CommentService.create_comment(params=params)

        self.assertIsNotNone(comment.id)
        self.assertEqual(comment.task_id, task.id)
        self.assertEqual(comment.account_id, account.id)
        self.assertEqual(comment.content, "This is a test comment")
        self.assertEqual(comment.author_name, "Test User")
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)

    def test_create_comment_with_whitespace_content(self):
        """Test comment creation with content that has whitespace"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        params = CreateCommentParams(
            task_id=task.id,
            account_id=account.id,
            content="  This is a test comment with whitespace  "
        )

        comment = CommentService.create_comment(params=params)

        self.assertEqual(comment.content, "This is a test comment with whitespace")

    def test_create_comment_empty_content_fails(self):
        """Test that creating a comment with empty content fails"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        params = CreateCommentParams(
            task_id=task.id,
            account_id=account.id,
            content=""
        )

        with self.assertRaises(ValueError) as context:
            CommentService.create_comment(params=params)

        self.assertIn("content cannot be empty", str(context.exception))

    def test_create_comment_whitespace_only_content_fails(self):
        """Test that creating a comment with whitespace-only content fails"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        params = CreateCommentParams(
            task_id=task.id,
            account_id=account.id,
            content="   "
        )

        with self.assertRaises(ValueError) as context:
            CommentService.create_comment(params=params)

        self.assertIn("content cannot be empty", str(context.exception))

    def test_create_comment_content_too_long_fails(self):
        """Test that creating a comment with content exceeding 2000 characters fails"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        long_content = "x" * 2001
        params = CreateCommentParams(
            task_id=task.id,
            account_id=account.id,
            content=long_content
        )

        with self.assertRaises(ValueError) as context:
            CommentService.create_comment(params=params)

        self.assertIn("cannot exceed 2000 characters", str(context.exception))

    def test_get_comment_success(self):
        """Test successful comment retrieval"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        params = GetCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id
        )

        retrieved_comment = CommentService.get_comment(params=params)

        self.assertEqual(retrieved_comment.id, created_comment.id)
        self.assertEqual(retrieved_comment.task_id, task.id)
        self.assertEqual(retrieved_comment.account_id, account.id)
        self.assertEqual(retrieved_comment.content, created_comment.content)

    def test_get_comment_not_found(self):
        """Test getting a non-existent comment fails"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        params = GetCommentParams(
            comment_id="507f1f77bcf86cd799439011",  # Non-existent ObjectId
            task_id=task.id,
            account_id=account.id
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=params)

    def test_get_comment_wrong_task_fails(self):
        """Test getting a comment with wrong task_id fails"""
        account, _ = self.create_account_and_get_token()
        task1 = self.create_test_task(account.id)
        task2 = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task1.id)

        params = GetCommentParams(
            comment_id=created_comment.id,
            task_id=task2.id,  # Wrong task
            account_id=account.id
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=params)

    def test_get_comment_wrong_account_fails(self):
        """Test getting a comment with wrong account_id fails"""
        account1, _ = self.create_account_and_get_token(username="user1@test.com")
        account2, _ = self.create_account_and_get_token(username="user2@test.com")
        task = self.create_test_task(account1.id)
        created_comment = self.create_test_comment(account1.id, task.id)

        params = GetCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account2.id  # Wrong account
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=params)

    def test_get_paginated_comments_success(self):
        """Test successful paginated comment retrieval"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Create multiple comments
        created_comments = self.create_multiple_test_comments(account.id, task.id, 5)

        pagination_params = PaginationParams(page=1, size=3, offset=0)
        params = GetPaginatedCommentsParams(
            task_id=task.id,
            account_id=account.id,
            pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=params)

        self.assertEqual(len(result.items), 3)
        self.assertEqual(result.total_count, 5)
        self.assertEqual(result.total_pages, 2)
        self.assertEqual(result.pagination_params.page, 1)
        self.assertEqual(result.pagination_params.size, 3)

    def test_get_paginated_comments_empty(self):
        """Test paginated comment retrieval when no comments exist"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        pagination_params = PaginationParams(page=1, size=10, offset=0)
        params = GetPaginatedCommentsParams(
            task_id=task.id,
            account_id=account.id,
            pagination_params=pagination_params
        )

        result = CommentService.get_paginated_comments(params=params)

        self.assertEqual(len(result.items), 0)
        self.assertEqual(result.total_count, 0)
        self.assertEqual(result.total_pages, 0)

    def test_update_comment_success(self):
        """Test successful comment update"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        params = UpdateCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id,
            content="Updated comment content"
        )

        updated_comment = CommentService.update_comment(params=params)

        self.assertEqual(updated_comment.id, created_comment.id)
        self.assertEqual(updated_comment.content, "Updated comment content")
        self.assertGreater(updated_comment.updated_at, created_comment.updated_at)

    def test_update_comment_with_whitespace_content(self):
        """Test comment update with content that has whitespace"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        params = UpdateCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id,
            content="  Updated comment with whitespace  "
        )

        updated_comment = CommentService.update_comment(params=params)

        self.assertEqual(updated_comment.content, "Updated comment with whitespace")

    def test_update_comment_empty_content_fails(self):
        """Test that updating a comment with empty content fails"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        params = UpdateCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id,
            content=""
        )

        with self.assertRaises(ValueError) as context:
            CommentService.update_comment(params=params)

        self.assertIn("content cannot be empty", str(context.exception))

    def test_update_comment_not_found(self):
        """Test updating a non-existent comment fails"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        params = UpdateCommentParams(
            comment_id="507f1f77bcf86cd799439011",  # Non-existent ObjectId
            task_id=task.id,
            account_id=account.id,
            content="Updated content"
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.update_comment(params=params)

    def test_delete_comment_success(self):
        """Test successful comment deletion"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        params = DeleteCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id
        )

        result = CommentService.delete_comment(params=params)

        self.assertTrue(result.success)
        self.assertEqual(result.comment_id, created_comment.id)
        self.assertIsNotNone(result.deleted_at)

    def test_delete_comment_not_found(self):
        """Test deleting a non-existent comment fails"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        params = DeleteCommentParams(
            comment_id="507f1f77bcf86cd799439011",  # Non-existent ObjectId
            task_id=task.id,
            account_id=account.id
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.delete_comment(params=params)

    def test_deleted_comment_not_accessible(self):
        """Test that deleted comments are not accessible"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        # Delete the comment
        delete_params = DeleteCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id
        )
        CommentService.delete_comment(params=delete_params)

        # Try to get the deleted comment
        get_params = GetCommentParams(
            comment_id=created_comment.id,
            task_id=task.id,
            account_id=account.id
        )

        with self.assertRaises(CommentNotFoundError):
            CommentService.get_comment(params=get_params)


if __name__ == "__main__":
    unittest.main()