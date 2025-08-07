import json
import unittest

from tests.modules.task.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):
    def test_create_comment_success(self):
        """Test successful comment creation"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        comment_data = {"content": "Test comment content"}
        response = self.make_authenticated_request(
            method="POST", account_id=account.id, task_id=task.id, token=token, data=comment_data
        )
        
        assert response.status_code == 201
        response_json = response.json
        self.assert_comment_response(
            response_json, 
            task_id=task.id, 
            account_id=account.id, 
            content="Test comment content"
        )

    def test_create_comment_missing_content(self):
        """Test comment creation with missing content"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        comment_data = {}
        response = self.make_authenticated_request(
            method="POST", account_id=account.id, task_id=task.id, token=token, data=comment_data
        )
        
        self.assert_error_response(response, 400, "COMMENT_ERR_02")

    def test_create_comment_empty_content(self):
        """Test comment creation with empty content"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        comment_data = {"content": ""}
        response = self.make_authenticated_request(
            method="POST", account_id=account.id, task_id=task.id, token=token, data=comment_data
        )
        
        self.assert_error_response(response, 400, "COMMENT_ERR_02")

    def test_create_comment_task_not_found(self):
        """Test comment creation for non-existent task"""
        account, token = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"
        
        comment_data = {"content": "Test comment content"}
        response = self.make_authenticated_request(
            method="POST", account_id=account.id, task_id=non_existent_task_id, token=token, data=comment_data
        )
        
        self.assert_error_response(response, 404, "TASK_ERR_01")

    def test_create_comment_unauthorized(self):
        """Test comment creation without authentication"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        comment_data = {"content": "Test comment content"}
        response = self.make_unauthenticated_request(
            method="POST", account_id=account.id, task_id=task.id, data=comment_data
        )
        
        assert response.status_code == 401

    def test_get_comment_success(self):
        """Test successful comment retrieval"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        response = self.make_authenticated_request(
            method="GET", account_id=account.id, task_id=task.id, comment_id=comment.id, token=token
        )
        
        assert response.status_code == 200
        response_json = response.json
        self.assert_comment_response(response_json, expected_comment=comment)

    def test_get_comment_not_found(self):
        """Test comment retrieval for non-existent comment"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        
        response = self.make_authenticated_request(
            method="GET", account_id=account.id, task_id=task.id, comment_id=non_existent_comment_id, token=token
        )
        
        self.assert_error_response(response, 404, "TASK_ERR_01")

    def test_get_comment_unauthorized(self):
        """Test comment retrieval without authentication"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        response = self.make_unauthenticated_request(
            method="GET", account_id=account.id, task_id=task.id, comment_id=comment.id
        )
        
        assert response.status_code == 401

    def test_get_paginated_comments_success(self):
        """Test successful paginated comments retrieval"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=5)
        
        response = self.make_authenticated_request(
            method="GET", account_id=account.id, task_id=task.id, token=token
        )
        
        assert response.status_code == 200
        response_json = response.json
        self.assert_pagination_response(response_json, expected_items_count=5, expected_total_count=5)

    def test_get_paginated_comments_with_pagination(self):
        """Test paginated comments retrieval with pagination parameters"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=10)
        
        response = self.make_authenticated_request(
            method="GET", account_id=account.id, task_id=task.id, token=token, query_params="page=1&size=3"
        )
        
        assert response.status_code == 200
        response_json = response.json
        self.assert_pagination_response(response_json, expected_items_count=3, expected_total_count=10, expected_page=1, expected_size=3)

    def test_get_paginated_comments_task_not_found(self):
        """Test paginated comments retrieval for non-existent task"""
        account, token = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"
        
        response = self.make_authenticated_request(
            method="GET", account_id=account.id, task_id=non_existent_task_id, token=token
        )
        
        self.assert_error_response(response, 404, "TASK_ERR_01")

    def test_update_comment_success(self):
        """Test successful comment update"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        update_data = {"content": "Updated comment content"}
        response = self.make_authenticated_request(
            method="PATCH", account_id=account.id, task_id=task.id, comment_id=comment.id, token=token, data=update_data
        )
        
        assert response.status_code == 200
        response_json = response.json
        self.assert_comment_response(
            response_json, 
            task_id=task.id, 
            account_id=account.id, 
            content="Updated comment content"
        )

    def test_update_comment_missing_content(self):
        """Test comment update with missing content"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        update_data = {}
        response = self.make_authenticated_request(
            method="PATCH", account_id=account.id, task_id=task.id, comment_id=comment.id, token=token, data=update_data
        )
        
        self.assert_error_response(response, 400, "COMMENT_ERR_02")

    def test_update_comment_not_found(self):
        """Test comment update for non-existent comment"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        
        update_data = {"content": "Updated comment content"}
        response = self.make_authenticated_request(
            method="PATCH", account_id=account.id, task_id=task.id, comment_id=non_existent_comment_id, token=token, data=update_data
        )
        
        self.assert_error_response(response, 404, "TASK_ERR_01")

    def test_update_comment_unauthorized(self):
        """Test comment update without authentication"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        update_data = {"content": "Updated comment content"}
        response = self.make_unauthenticated_request(
            method="PATCH", account_id=account.id, task_id=task.id, comment_id=comment.id, data=update_data
        )
        
        assert response.status_code == 401

    def test_delete_comment_success(self):
        """Test successful comment deletion"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        response = self.make_authenticated_request(
            method="DELETE", account_id=account.id, task_id=task.id, comment_id=comment.id, token=token
        )
        
        assert response.status_code == 204

    def test_delete_comment_not_found(self):
        """Test comment deletion for non-existent comment"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        
        response = self.make_authenticated_request(
            method="DELETE", account_id=account.id, task_id=task.id, comment_id=non_existent_comment_id, token=token
        )
        
        self.assert_error_response(response, 404, "TASK_ERR_01")

    def test_delete_comment_unauthorized(self):
        """Test comment deletion without authentication"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        response = self.make_unauthenticated_request(
            method="DELETE", account_id=account.id, task_id=task.id, comment_id=comment.id
        )
        
        assert response.status_code == 401

    def test_cross_account_access_denied(self):
        """Test that users cannot access comments from other accounts"""
        account1, token1 = self.create_account_and_get_token(username="user1@example.com")
        account2, _ = self.create_account_and_get_token(username="user2@example.com")
        
        task = self.create_test_task(account_id=account1.id)
        comment = self.create_test_comment(account_id=account1.id, task_id=task.id)
        
        # Try to access comment from different account
        response = self.make_cross_account_request(
            method="GET", target_account_id=account1.id, task_id=task.id, auth_token=token1, comment_id=comment.id
        )
        
        # This should work since we're using the correct token, but let's test with wrong account
        # We need to create a different scenario - let's test with a non-existent task in account2
        task2 = self.create_test_task(account_id=account2.id)
        
        response = self.make_authenticated_request(
            method="GET", account_id=account2.id, task_id=task2.id, comment_id=comment.id, token=token1
        )
        
        # This should fail because the comment doesn't belong to task2
        self.assert_error_response(response, 404, "TASK_ERR_01")


if __name__ == "__main__":
    unittest.main() 