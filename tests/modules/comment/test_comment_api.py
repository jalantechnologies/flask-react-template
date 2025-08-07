from server import app
from modules.authentication.errors import AccessTokenErrorCode
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
            response.json,
            content=self.DEFAULT_COMMENT_CONTENT,
            task_id=task.id,
            account_id=account.id,
        )

    def test_create_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {}

        response = self.make_authenticated_request("POST", account.id, task.id, token, data=comment_data)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_create_comment_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_authenticated_request("POST", account.id, task.id, token, data=None)

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

    def test_create_comment_nonexistent_task(self) -> None:
        account, token = self.create_account_and_get_token()
        nonexistent_task_id = "507f1f77bcf86cd799439011"
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_authenticated_request("POST", account.id, nonexistent_task_id, token, data=comment_data)

        self.assert_error_response(response, 404, CommentErrorCode.TASK_NOT_FOUND)

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

        assert response.json["items"][0]["content"] == "Comment 3"
        assert response.json["items"][1]["content"] == "Comment 2"
        assert response.json["items"][2]["content"] == "Comment 1"

    def test_get_all_comments_with_pagination(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=15)

        response = self.make_authenticated_request("GET", account.id, task.id, token, query_params="page=2&size=5")

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=5, expected_total_count=15)

    def test_get_all_comments_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_unauthenticated_request("GET", account.id, task.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_get_specific_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(
            account_id=account.id, task_id=task.id, content="Specific comment"
        )

        response = self.make_authenticated_request("GET", account.id, task.id, token, comment_id=created_comment.id)

        assert response.status_code == 200
        self.assert_comment_response(response.json, expected_comment=created_comment)

    def test_get_specific_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("GET", account.id, task.id, token, comment_id=non_existent_comment_id)

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_get_specific_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        response = self.make_unauthenticated_request("GET", account.id, task.id, comment_id=created_comment.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(
            account_id=account.id, task_id=task.id, content="Original comment"
        )
        update_data = {"content": "Updated comment"}

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=created_comment.id, data=update_data
        )

        assert response.status_code == 200
        assert response.json["content"] == "Updated comment"
        assert response.json["id"] == created_comment.id

    def test_update_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        update_data = {}

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=created_comment.id, data=update_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_update_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"content": "Updated content"}

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=non_existent_comment_id, data=update_data
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_update_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        update_data = {"content": "Updated content"}

        response = self.make_unauthenticated_request("PATCH", account.id, task.id, comment_id=created_comment.id, data=update_data)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(
            account_id=account.id, task_id=task.id, content="Comment to Delete"
        )

        delete_response = self.make_authenticated_request("DELETE", account.id, task.id, token, comment_id=created_comment.id)

        assert delete_response.status_code == 204
        assert delete_response.data == b""

        get_response = self.make_authenticated_request("GET", account.id, task.id, token, comment_id=created_comment.id)
        assert get_response.status_code == 404

    def test_delete_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("DELETE", account.id, task.id, token, comment_id=non_existent_comment_id)

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        response = self.make_unauthenticated_request("DELETE", account.id, task.id, comment_id=created_comment.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_comments_are_task_isolated_via_api(self) -> None:
        account, token = self.create_account_and_get_token()
        task1 = self.create_test_task(account_id=account.id, title="Task 1")
        task2 = self.create_test_task(account_id=account.id, title="Task 2")
        
        # Create comments on different tasks
        comment1 = self.create_test_comment(account_id=account.id, task_id=task1.id, content="Comment on Task 1")
        comment2 = self.create_test_comment(account_id=account.id, task_id=task2.id, content="Comment on Task 2")

        # Get comments for task1 - should only see comments for task1
        response1 = self.make_authenticated_request("GET", account.id, task1.id, token)
        assert response1.status_code == 200
        assert len(response1.json["items"]) == 1
        assert response1.json["items"][0]["content"] == "Comment on Task 1"

        # Get comments for task2 - should only see comments for task2
        response2 = self.make_authenticated_request("GET", account.id, task2.id, token)
        assert response2.status_code == 200
        assert len(response2.json["items"]) == 1
        assert response2.json["items"][0]["content"] == "Comment on Task 2"

    def test_invalid_json_request_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        with app.test_client() as client:
            response = client.post(
                self.get_comment_api_url(account.id, task.id),
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data="invalid json",
            )

        assert response.status_code == 400
