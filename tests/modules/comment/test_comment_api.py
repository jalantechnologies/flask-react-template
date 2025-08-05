import json

from server import app

from modules.authentication.types import AccessTokenErrorCode
from modules.comment.types import CommentErrorCode
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):

    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_authenticated_request("POST", account.id, task.id, token, data=comment_data)

        assert response.status_code == 201
        assert response.json is not None
        self.assert_comment_response(
            response.json, content=self.DEFAULT_COMMENT_CONTENT, account_id=account.id, task_id=task.id
        )

    def test_create_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"task_id": task.id}

        response = self.make_authenticated_request("POST", account.id, task.id, token, data=comment_data)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_create_comment_missing_task_id(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        # Remove task_id from the request data by using empty data and manual request
        with app.test_client() as client:
            response = client.post(
                f"http://127.0.0.1:8080/api/accounts/{account.id}/comments",
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(comment_data),
            )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Task ID is required" in response.json.get("message")

    def test_create_comment_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        # Make request with None data to test empty body
        with app.test_client() as client:
            response = client.post(
                f"http://127.0.0.1:8080/api/accounts/{account.id}/comments",
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=None,
            )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Request body is required" in response.json.get("message")

    def test_create_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_unauthenticated_request("POST", account.id, task.id, data=comment_data)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_create_comment_invalid_token(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        invalid_token = "invalid_token"
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_authenticated_request("POST", account.id, task.id, invalid_token, data=comment_data)

        self.assert_error_response(response, 401, AccessTokenErrorCode.ACCESS_TOKEN_INVALID)

    def test_get_all_comments_empty(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_authenticated_request("GET", account.id, task.id, token)

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=0, expected_total_count=0)

    def test_get_all_comments_with_comments(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=3)

        response = self.make_authenticated_request("GET", account.id, task.id, token)

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=3, expected_total_count=3)

        # Comments should be in the response (order may vary based on implementation)
        response_comments = response.json["items"]
        assert len(response_comments) == 3
        for comment in response_comments:
            assert comment["account_id"] == account.id
            assert comment["task_id"] == task.id

    def test_get_all_comments_with_pagination(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=5)

        response1 = self.make_authenticated_request("GET", account.id, task.id, token, query_params="page=1&size=2")
        response2 = self.make_authenticated_request("GET", account.id, task.id, token, query_params="page=2&size=2")

        assert response1.status_code == 200
        self.assert_pagination_response(
            response1.json, expected_items_count=2, expected_total_count=5, expected_page=1, expected_size=2
        )

        assert response2.status_code == 200
        self.assert_pagination_response(
            response2.json, expected_items_count=2, expected_total_count=5, expected_page=2, expected_size=2
        )

    def test_get_all_comments_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_unauthenticated_request("GET", account.id, task.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_get_specific_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        response = self.make_authenticated_request("GET", account.id, task.id, token, comment_id=comment.id)

        assert response.status_code == 200
        self.assert_comment_response(response.json, expected_comment=comment)

    def test_get_specific_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("GET", account.id, task.id, token, comment_id=fake_comment_id)

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_get_specific_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        response = self.make_unauthenticated_request("GET", account.id, task.id, comment_id=comment.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        update_data = {"content": "Updated comment content"}

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=comment.id, data=update_data
        )

        assert response.status_code == 200
        self.assert_comment_response(
            response.json, content="Updated comment content", account_id=account.id, task_id=task.id
        )

    def test_update_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        update_data = {"task_id": task.id}

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=comment.id, data=update_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_update_comment_missing_task_id(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        update_data = {"content": "Updated content"}

        # Make request without task_id
        with app.test_client() as client:
            response = client.patch(
                f"http://127.0.0.1:8080/api/accounts/{account.id}/comments/{comment.id}",
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(update_data),
            )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Task ID is required" in response.json.get("message")

    def test_update_comment_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        # Make request with None data
        with app.test_client() as client:
            response = client.patch(
                f"http://127.0.0.1:8080/api/accounts/{account.id}/comments/{comment.id}",
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=None,
            )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Request body is required" in response.json.get("message")

    def test_update_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"content": "Updated content"}

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=fake_comment_id, data=update_data
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_update_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        update_data = {"content": "Updated content"}

        response = self.make_unauthenticated_request(
            "PATCH", account.id, task.id, comment_id=comment.id, data=update_data
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        response = self.make_authenticated_request("DELETE", account.id, task.id, token, comment_id=comment.id)

        assert response.status_code == 204
        assert response.data == b""

    def test_delete_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("DELETE", account.id, task.id, token, comment_id=fake_comment_id)

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        response = self.make_unauthenticated_request("DELETE", account.id, task.id, comment_id=comment.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_cross_account_comment_access_denied(self) -> None:
        # Create two accounts
        account1, token1 = self.create_account_and_get_token(username="user1@example.com")
        account2, _ = self.create_account_and_get_token(username="user2@example.com")

        # Create task and comment for account2
        task2 = self.create_test_task(account_id=account2.id)
        comment2 = self.create_test_comment(account_id=account2.id, task_id=task2.id)

        # Try to access account2's comment with account1's token
        response = self.make_cross_account_request("GET", account2.id, task2.id, token1, comment_id=comment2.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)

    def test_comment_isolation_between_tasks(self) -> None:
        account, token = self.create_account_and_get_token()
        task1 = self.create_test_task(account_id=account.id, title="Task 1")
        task2 = self.create_test_task(account_id=account.id, title="Task 2")

        # Create comments for different tasks
        comment1 = self.create_test_comment(account_id=account.id, task_id=task1.id, content="Comment for task 1")
        comment2 = self.create_test_comment(account_id=account.id, task_id=task2.id, content="Comment for task 2")

        # Get comments for task1 - should only see task1's comment
        response1 = self.make_authenticated_request("GET", account.id, task1.id, token)
        assert response1.status_code == 200
        assert len(response1.json["items"]) == 1
        assert response1.json["items"][0]["content"] == "Comment for task 1"

        # Get comments for task2 - should only see task2's comment
        response2 = self.make_authenticated_request("GET", account.id, task2.id, token)
        assert response2.status_code == 200
        assert len(response2.json["items"]) == 1
        assert response2.json["items"][0]["content"] == "Comment for task 2"

    def test_pagination_with_invalid_parameters(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        # Test invalid page (negative)
        response1 = self.make_authenticated_request("GET", account.id, task.id, token, query_params="page=-1")
        self.assert_error_response(response1, 400, CommentErrorCode.BAD_REQUEST)
        assert "Page must be greater than 0" in response1.json.get("message")

        # Test invalid size (negative)
        response2 = self.make_authenticated_request("GET", account.id, task.id, token, query_params="size=-1")
        self.assert_error_response(response2, 400, CommentErrorCode.BAD_REQUEST)
        assert "Size must be greater than 0" in response2.json.get("message")

        # Test invalid page (zero)
        response3 = self.make_authenticated_request("GET", account.id, task.id, token, query_params="page=0")
        self.assert_error_response(response3, 400, CommentErrorCode.BAD_REQUEST)
        assert "Page must be greater than 0" in response3.json.get("message")

        # Test invalid size (zero)
        response4 = self.make_authenticated_request("GET", account.id, task.id, token, query_params="size=0")
        self.assert_error_response(response4, 400, CommentErrorCode.BAD_REQUEST)
        assert "Size must be greater than 0" in response4.json.get("message")
