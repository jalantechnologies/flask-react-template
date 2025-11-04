import unittest

from modules.comment.types import CommentErrorCode
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentAPI(BaseTestComment):
    def test_create_comment_api_success(self):
        """Test successful comment creation via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        request_data = {"content": "This is a test comment via API"}
        response = self.make_authenticated_request(
            "POST", account.id, task.id, token, data=request_data
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json)
        self.assert_comment_response(response.json, content="This is a test comment via API")

    def test_create_comment_api_no_auth_fails(self):
        """Test that creating a comment without authentication fails"""
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        request_data = {"content": "This is a test comment"}
        response = self.make_unauthenticated_request(
            "POST", account.id, task.id, data=request_data
        )

        self.assertEqual(response.status_code, 401)

    def test_create_comment_api_no_body_fails(self):
        """Test that creating a comment with no request body fails"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request(
            "POST", account.id, task.id, token
        )

        self.assertEqual(response.status_code, 400)
        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_create_comment_api_empty_content_fails(self):
        """Test that creating a comment with empty content fails via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        request_data = {"content": ""}
        response = self.make_authenticated_request(
            "POST", account.id, task.id, token, data=request_data
        )

        self.assertEqual(response.status_code, 400)
        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_create_comment_api_whitespace_only_content_fails(self):
        """Test that creating a comment with whitespace-only content fails via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        request_data = {"content": "   "}
        response = self.make_authenticated_request(
            "POST", account.id, task.id, token, data=request_data
        )

        self.assertEqual(response.status_code, 400)
        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_create_comment_api_content_too_long_fails(self):
        """Test that creating a comment with content exceeding 2000 characters fails via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        long_content = "x" * 2001
        request_data = {"content": long_content}
        response = self.make_authenticated_request(
            "POST", account.id, task.id, token, data=request_data
        )

        self.assertEqual(response.status_code, 400)
        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_create_comment_api_cross_account_fails(self):
        """Test that creating a comment for another account's task fails"""
        account1, token1 = self.create_account_and_get_token(username="user1@test.com")
        account2, _ = self.create_account_and_get_token(username="user2@test.com")

        # Create task for account2 but try to comment with account1's token
        task = self.create_test_task(account2.id)

        request_data = {"content": "This should fail"}
        response = self.make_cross_account_request(
            "POST", account2.id, task.id, token1, data=request_data
        )

        self.assertEqual(response.status_code, 404)

    def test_get_comment_api_success(self):
        """Test successful comment retrieval via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        response = self.make_authenticated_request(
            "GET", account.id, task.id, token, comment_id=created_comment.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assert_comment_response(response.json, expected_comment=created_comment)

    def test_get_comment_api_not_found(self):
        """Test getting a non-existent comment via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request(
            "GET", account.id, task.id, token, comment_id="507f1f77bcf86cd799439011"
        )

        self.assertEqual(response.status_code, 404)
        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_get_comments_list_api_success(self):
        """Test successful comment list retrieval via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Create multiple comments
        self.create_multiple_test_comments(account.id, task.id, 5)

        response = self.make_authenticated_request(
            "GET", account.id, task.id, token
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assert_pagination_response(response.json, expected_items_count=5, expected_total_count=5)

    def test_get_comments_list_api_with_pagination(self):
        """Test paginated comment list retrieval via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Create multiple comments
        self.create_multiple_test_comments(account.id, task.id, 15)

        response = self.make_authenticated_request(
            "GET", account.id, task.id, token, query_params="page=1&size=5"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assert_pagination_response(
            response.json,
            expected_items_count=5,
            expected_total_count=15,
            expected_page=1,
            expected_size=5
        )

    def test_get_comments_list_api_empty(self):
        """Test comment list retrieval when no comments exist via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request(
            "GET", account.id, task.id, token
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assert_pagination_response(response.json, expected_items_count=0, expected_total_count=0)

    def test_update_comment_api_success(self):
        """Test successful comment update via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        request_data = {"content": "Updated comment via API"}
        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=created_comment.id, data=request_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assert_comment_response(response.json, content="Updated comment via API")

    def test_update_comment_api_no_body_fails(self):
        """Test that updating a comment with no request body fails via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=created_comment.id
        )

        self.assertEqual(response.status_code, 400)
        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_update_comment_api_empty_content_fails(self):
        """Test that updating a comment with empty content fails via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        request_data = {"content": ""}
        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=created_comment.id, data=request_data
        )

        self.assertEqual(response.status_code, 400)
        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_update_comment_api_not_found(self):
        """Test updating a non-existent comment via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        request_data = {"content": "Updated content"}
        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id="507f1f77bcf86cd799439011", data=request_data
        )

        self.assertEqual(response.status_code, 404)
        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_api_success(self):
        """Test successful comment deletion via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        created_comment = self.create_test_comment(account.id, task.id)

        response = self.make_authenticated_request(
            "DELETE", account.id, task.id, token, comment_id=created_comment.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assertTrue(response.json.get("success"))
        self.assertEqual(response.json.get("comment_id"), created_comment.id)

    def test_delete_comment_api_not_found(self):
        """Test deleting a non-existent comment via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request(
            "DELETE", account.id, task.id, token, comment_id="507f1f77bcf86cd799439011"
        )

        self.assertEqual(response.status_code, 404)
        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_pagination_edge_cases(self):
        """Test pagination edge cases via API"""
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Create exactly 10 comments
        self.create_multiple_test_comments(account.id, task.id, 10)

        # Test page 0 (should fail)
        response = self.make_authenticated_request(
            "GET", account.id, task.id, token, query_params="page=0"
        )
        self.assertEqual(response.status_code, 400)

        # Test size 0 (should fail)
        response = self.make_authenticated_request(
            "GET", account.id, task.id, token, query_params="size=0"
        )
        self.assertEqual(response.status_code, 400)

        # Test page beyond available (should return empty)
        response = self.make_authenticated_request(
            "GET", account.id, task.id, token, query_params="page=100"
        )
        self.assertEqual(response.status_code, 200)
        self.assert_pagination_response(response.json, expected_items_count=0, expected_total_count=10)

    def test_author_name_is_correct(self):
        """Test that author name is correctly populated from account"""
        # Create account with specific name
        account, token = self.create_account_and_get_token(
            first_name="John",
            last_name="Doe"
        )
        task = self.create_test_task(account.id)

        request_data = {"content": "Test comment"}
        response = self.make_authenticated_request(
            "POST", account.id, task.id, token, data=request_data
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json.get("author_name"), "John Doe")


if __name__ == "__main__":
    unittest.main()