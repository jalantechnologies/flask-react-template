import unittest

from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):
    def test_create_comment_success(self):
        """Test successful comment creation"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        comment_data = {"content": "This is a new comment"}
        response = self.make_authenticated_request(
            method="POST", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            data=comment_data
        )
        
        self.assertEqual(response.status_code, 201)
        response_json = response.get_json()
        self.assert_comment_response(
            response_json, 
            task_id=task.id, 
            account_id=account.id, 
            content="This is a new comment"
        )

    def test_create_comment_missing_content(self):
        """Test comment creation with missing content"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        comment_data = {}
        response = self.make_authenticated_request(
            method="POST", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            data=comment_data
        )
        
        self.assert_error_response(response, 400, "COMMENT_ERR_02")

    def test_create_comment_missing_request_body(self):
        """Test comment creation with missing request body"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        response = self.make_authenticated_request(
            method="POST", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            data=None
        )
        
        self.assert_error_response(response, 400, "COMMENT_ERR_02")

    def test_create_comment_unauthenticated(self):
        """Test comment creation without authentication"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        comment_data = {"content": "This is a new comment"}
        response = self.make_unauthenticated_request(
            method="POST", 
            account_id=account.id, 
            task_id=task.id, 
            data=comment_data
        )
        
        self.assertEqual(response.status_code, 401)

    def test_get_comment_success(self):
        """Test successful comment retrieval"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        response = self.make_authenticated_request(
            method="GET", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            comment_id=comment.id
        )
        
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assert_comment_response(response_json, expected_comment=comment)

    def test_get_comment_not_found(self):
        """Test comment retrieval with non-existent comment"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        response = self.make_authenticated_request(
            method="GET", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            comment_id="507f1f77bcf86cd799439011"
        )
        
        self.assert_error_response(response, 404, "COMMENT_ERR_01")

    def test_get_comment_unauthenticated(self):
        """Test comment retrieval without authentication"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        response = self.make_unauthenticated_request(
            method="GET", 
            account_id=account.id, 
            task_id=task.id, 
            comment_id=comment.id
        )
        
        self.assertEqual(response.status_code, 401)

    def test_get_paginated_comments_success(self):
        """Test successful paginated comments retrieval"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=5)
        
        response = self.make_authenticated_request(
            method="GET", 
            account_id=account.id, 
            task_id=task.id, 
            token=token
        )
        
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assert_pagination_response(
            response_json, 
            expected_items_count=5, 
            expected_total_count=5, 
            expected_page=1, 
            expected_size=10
        )

    def test_get_paginated_comments_with_pagination(self):
        """Test paginated comments retrieval with pagination parameters"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=15)
        
        response = self.make_authenticated_request(
            method="GET", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            query_params="page=2&per_page=5"
        )
        
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assert_pagination_response(
            response_json, 
            expected_items_count=5, 
            expected_total_count=15, 
            expected_page=2, 
            expected_size=5
        )

    def test_update_comment_success(self):
        """Test successful comment update"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        update_data = {"content": "Updated comment content"}
        response = self.make_authenticated_request(
            method="PATCH", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            comment_id=comment.id, 
            data=update_data
        )
        
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
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
            method="PATCH", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            comment_id=comment.id, 
            data=update_data
        )
        
        self.assert_error_response(response, 400, "COMMENT_ERR_02")

    def test_update_comment_not_found(self):
        """Test comment update with non-existent comment"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        update_data = {"content": "Updated comment content"}
        response = self.make_authenticated_request(
            method="PATCH", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            comment_id="507f1f77bcf86cd799439011", 
            data=update_data
        )
        
        self.assert_error_response(response, 404, "COMMENT_ERR_01")

    def test_update_comment_unauthenticated(self):
        """Test comment update without authentication"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        update_data = {"content": "Updated comment content"}
        response = self.make_unauthenticated_request(
            method="PATCH", 
            account_id=account.id, 
            task_id=task.id, 
            comment_id=comment.id, 
            data=update_data
        )
        
        self.assertEqual(response.status_code, 401)

    def test_delete_comment_success(self):
        """Test successful comment deletion"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        response = self.make_authenticated_request(
            method="DELETE", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            comment_id=comment.id
        )
        
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIn("comment_id", response_json)
        self.assertIn("deleted_at", response_json)
        self.assertIn("success", response_json)
        self.assertEqual(response_json["comment_id"], comment.id)
        self.assertTrue(response_json["success"])

    def test_delete_comment_not_found(self):
        """Test comment deletion with non-existent comment"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        
        response = self.make_authenticated_request(
            method="DELETE", 
            account_id=account.id, 
            task_id=task.id, 
            token=token, 
            comment_id="507f1f77bcf86cd799439011"
        )
        
        self.assert_error_response(response, 404, "COMMENT_ERR_01")

    def test_delete_comment_unauthenticated(self):
        """Test comment deletion without authentication"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        
        response = self.make_unauthenticated_request(
            method="DELETE", 
            account_id=account.id, 
            task_id=task.id, 
            comment_id=comment.id
        )
        
        self.assertEqual(response.status_code, 401)

    def test_cross_account_access_denied(self):
        """Test that users cannot access comments from other accounts"""
        account1, token1 = self.create_account_and_get_token(username="user1@example.com")
        account2, _ = self.create_account_and_get_token(username="user2@example.com")
        
        task1 = self.create_test_task(account_id=account1.id)
        task2 = self.create_test_task(account_id=account2.id)
        comment1 = self.create_test_comment(account_id=account1.id, task_id=task1.id)
        comment2 = self.create_test_comment(account_id=account2.id, task_id=task2.id)
        
        # Try to access comment from account2 using token from account1
        response = self.make_cross_account_request(
            method="GET", 
            target_account_id=account2.id, 
            task_id=task2.id, 
            auth_token=token1, 
            comment_id=comment2.id
        )
        
        self.assert_error_response(response, 404, "COMMENT_ERR_01")


if __name__ == "__main__":
    unittest.main() 