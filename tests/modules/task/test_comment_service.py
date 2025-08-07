import unittest
from datetime import datetime

from modules.task.comment_service import CommentService
from modules.task.task_service import TaskService
from modules.task.types import (
    CreateCommentParams,
    CreateTaskParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)
from modules.task.errors import TaskNotFoundError
from tests.modules.task.base_test_comment import BaseTestComment


class TestCommentService(BaseTestComment):
    def test_create_comment_success(self):
        """Test successful comment creation through service"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        create_params = CreateCommentParams(
            account_id=account.id,
            task_id=task.id,
            content="Test comment content"
        )
        
        comment = CommentService.create_comment(params=create_params)
        
        assert comment.task_id == task.id
        assert comment.account_id == account.id
        assert comment.content == "Test comment content"
        assert comment.created_at is not None
        assert comment.updated_at is not None

    def test_create_comment_task_not_found(self):
        """Test comment creation for non-existent task"""
        account, _ = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"
        
        create_params = CreateCommentParams(
            account_id=account.id,
            task_id=non_existent_task_id,
            content="Test comment content"
        )
        
        with self.assertRaises(TaskNotFoundError):
            CommentService.create_comment(params=create_params)

    def test_get_comment_success(self):
        """Test successful comment retrieval through service"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        get_params = GetCommentParams(
            account_id=account.id,
            task_id=task.id,
            comment_id=created_comment.id
        )
        
        comment = CommentService.get_comment(params=get_params)
        
        assert comment.id == created_comment.id
        assert comment.task_id == task.id
        assert comment.account_id == account.id
        assert comment.content == created_comment.content

    def test_get_comment_not_found(self):
        """Test comment retrieval for non-existent comment"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        
        get_params = GetCommentParams(
            account_id=account.id,
            task_id=task.id,
            comment_id=non_existent_comment_id
        )
        
        with self.assertRaises(TaskNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_get_comment_task_not_found(self):
        """Test comment retrieval for non-existent task"""
        account, _ = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"
        non_existent_comment_id = "507f1f77bcf86cd799439012"
        
        get_params = GetCommentParams(
            account_id=account.id,
            task_id=non_existent_task_id,
            comment_id=non_existent_comment_id
        )
        
        with self.assertRaises(TaskNotFoundError):
            CommentService.get_comment(params=get_params)

    def test_get_paginated_comments_success(self):
        """Test successful paginated comments retrieval through service"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=5)
        
        from modules.application.common.types import PaginationParams
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        
        get_params = GetPaginatedCommentsParams(
            account_id=account.id,
            task_id=task.id,
            pagination_params=pagination_params
        )
        
        result = CommentService.get_paginated_comments(params=get_params)
        
        assert len(result.items) == 5
        assert result.total_count == 5
        assert result.page == 1
        assert result.size == 10

    def test_get_paginated_comments_task_not_found(self):
        """Test paginated comments retrieval for non-existent task"""
        account, _ = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"
        
        from modules.application.common.types import PaginationParams
        pagination_params = PaginationParams(page=1, size=10, offset=0)
        
        get_params = GetPaginatedCommentsParams(
            account_id=account.id,
            task_id=non_existent_task_id,
            pagination_params=pagination_params
        )
        
        with self.assertRaises(TaskNotFoundError):
            CommentService.get_paginated_comments(params=get_params)

    def test_update_comment_success(self):
        """Test successful comment update through service"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        update_params = UpdateCommentParams(
            account_id=account.id,
            task_id=task.id,
            comment_id=comment.id,
            content="Updated comment content"
        )
        
        updated_comment = CommentService.update_comment(params=update_params)
        
        assert updated_comment.id == comment.id
        assert updated_comment.task_id == task.id
        assert updated_comment.account_id == account.id
        assert updated_comment.content == "Updated comment content"

    def test_update_comment_not_found(self):
        """Test comment update for non-existent comment"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        
        update_params = UpdateCommentParams(
            account_id=account.id,
            task_id=task.id,
            comment_id=non_existent_comment_id,
            content="Updated comment content"
        )
        
        with self.assertRaises(TaskNotFoundError):
            CommentService.update_comment(params=update_params)

    def test_update_comment_task_not_found(self):
        """Test comment update for non-existent task"""
        account, _ = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"
        non_existent_comment_id = "507f1f77bcf86cd799439012"
        
        update_params = UpdateCommentParams(
            account_id=account.id,
            task_id=non_existent_task_id,
            comment_id=non_existent_comment_id,
            content="Updated comment content"
        )
        
        with self.assertRaises(TaskNotFoundError):
            CommentService.update_comment(params=update_params)

    def test_delete_comment_success(self):
        """Test successful comment deletion through service"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        delete_params = DeleteCommentParams(
            account_id=account.id,
            task_id=task.id,
            comment_id=comment.id
        )
        
        result = CommentService.delete_comment(params=delete_params)
        
        assert result.comment_id == comment.id
        assert result.success is True
        assert result.deleted_at is not None

    def test_delete_comment_not_found(self):
        """Test comment deletion for non-existent comment"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        
        delete_params = DeleteCommentParams(
            account_id=account.id,
            task_id=task.id,
            comment_id=non_existent_comment_id
        )
        
        with self.assertRaises(TaskNotFoundError):
            CommentService.delete_comment(params=delete_params)

    def test_delete_comment_task_not_found(self):
        """Test comment deletion for non-existent task"""
        account, _ = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"
        non_existent_comment_id = "507f1f77bcf86cd799439012"
        
        delete_params = DeleteCommentParams(
            account_id=account.id,
            task_id=non_existent_task_id,
            comment_id=non_existent_comment_id
        )
        
        with self.assertRaises(TaskNotFoundError):
            CommentService.delete_comment(params=delete_params)


if __name__ == "__main__":
    unittest.main() 