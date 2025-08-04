from server import app

from modules.authentication.types import AccessTokenErrorCode
from modules.comments.types import CommentErrorCode
from tests.modules.comments.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):

    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": "This is a test comment"}

        response = self.make_authenticated_comment_request(
            "POST", account.id, token, task_id=task.id, data=comment_data
        )

        assert response.status_code == 201
        assert response.json is not None
        self.assert_comment_response(
            response.json, content=comment_data["content"], account_id=account.id, task_id=task.id
        )

    def test_create_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {}

        response = self.make_authenticated_comment_request(
            "POST", account.id, token, task_id=task.id, data=comment_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_create_comment_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_authenticated_comment_request("POST", account.id, token, task_id=task.id)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Request body is required" in response.json.get("message")

    def test_create_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_unauthenticated_comment_request("POST", account.id, task_id=task.id, data=comment_data)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_create_comment_invalid_token(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        invalid_token = "invalid_token"
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_authenticated_comment_request(
            "POST", account.id, invalid_token, task_id=task.id, data=comment_data
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.ACCESS_TOKEN_INVALID)

    def test_get_all_comments_empty(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_authenticated_comment_request("GET", account.id, token, task_id=task.id)

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=0, expected_total_count=0)

    def test_get_all_comments_with_comments(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=3)

        response = self.make_authenticated_comment_request("GET", account.id, token, task_id=task.id)

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=3, expected_total_count=3)

        assert response.json["items"][0]["content"] == "Comment 3"
        assert response.json["items"][1]["content"] == "Comment 2"
        assert response.json["items"][2]["content"] == "Comment 1"

    def test_get_all_comments_with_pagination(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        self.create_multiple_test_comments(account_id=account.id, task_id=task.id, count=5)

        response1 = self.make_authenticated_comment_request(
            "GET", account.id, token, task_id=task.id, query_params="page=1&size=2"
        )
        response2 = self.make_authenticated_comment_request(
            "GET", account.id, token, task_id=task.id, query_params="page=2&size=2"
        )

        assert response1.status_code == 200
        self.assert_pagination_response(
            response1.json, expected_items_count=2, expected_total_count=5, expected_page=1, expected_size=2
        )

        assert response2.status_code == 200
        self.assert_pagination_response(
            response2.json, expected_items_count=2, expected_total_count=5, expected_page=2, expected_size=2
        )

        assert response1.json["items"][0]["id"] != response2.json["items"][0]["id"]

    def test_get_all_comments_invalid_page(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_authenticated_comment_request(
            "GET", account.id, token, task_id=task.id, query_params="page=0"
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Page must be greater than 0" in response.json.get("message")

    def test_get_all_comments_invalid_size(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_authenticated_comment_request(
            "GET", account.id, token, task_id=task.id, query_params="size=0"
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Size must be greater than 0" in response.json.get("message")

    def test_get_all_comments_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_unauthenticated_comment_request("GET", account.id, task_id=task.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_get_specific_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        response = self.make_authenticated_comment_request(
            "GET", account.id, token, task_id=task.id, comment_id=created_comment.id
        )

        assert response.status_code == 200
        self.assert_comment_response(response.json, expected_comment=created_comment)

    def test_get_specific_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_comment_request(
            "GET", account.id, token, task_id=task.id, comment_id=non_existent_comment_id
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_get_specific_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_unauthenticated_comment_request(
            "GET", account.id, task_id=task.id, comment_id=fake_comment_id
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id, content="Original content")
        update_data = {"content": "Updated content"}

        response = self.make_authenticated_comment_request(
            "PATCH", account.id, token, task_id=task.id, comment_id=created_comment.id, data=update_data
        )

        assert response.status_code == 200
        self.assert_comment_response(
            response.json, id=created_comment.id, account_id=account.id, task_id=task.id, content=update_data["content"]
        )

    def test_update_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)
        update_data = {}

        response = self.make_authenticated_comment_request(
            "PATCH", account.id, token, task_id=task.id, comment_id=created_comment.id, data=update_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_update_comment_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        response = self.make_authenticated_comment_request(
            "PATCH", account.id, token, task_id=task.id, comment_id=created_comment.id
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Request body is required" in response.json.get("message")

    def test_update_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"content": "Updated content"}

        response = self.make_authenticated_comment_request(
            "PATCH", account.id, token, task_id=task.id, comment_id=non_existent_comment_id, data=update_data
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_update_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"content": "Updated content"}

        response = self.make_unauthenticated_comment_request(
            "PATCH", account.id, task_id=task.id, comment_id=fake_comment_id, data=update_data
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(account_id=account.id, task_id=task.id)

        delete_response = self.make_authenticated_comment_request(
            "DELETE", account.id, token, task_id=task.id, comment_id=created_comment.id
        )

        assert delete_response.status_code == 204
        assert delete_response.data == b""

        get_response = self.make_authenticated_comment_request(
            "GET", account.id, token, task_id=task.id, comment_id=created_comment.id
        )
        assert get_response.status_code == 404

    def test_delete_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_comment_request(
            "DELETE", account.id, token, task_id=task.id, comment_id=non_existent_comment_id
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_unauthenticated_comment_request(
            "DELETE", account.id, task_id=task.id, comment_id=fake_comment_id
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_comments_are_account_isolated_via_api(self) -> None:
        account1, token1 = self.create_account_and_get_token("user1@example.com", "password1")
        account2, token2 = self.create_account_and_get_token("user2@example.com", "password2")
        task1 = self.create_test_task(account_id=account1.id)
        response = self.make_authenticated_comment_request(
            "POST", account1.id, token1, task_id=task1.id, data={"content": "Private comment"}
        )
        comment_id = response.json.get("id")

        get_response = self.make_cross_account_comment_request(
            "GET", account1.id, token2, task_id=task1.id, comment_id=comment_id
        )
        patch_response = self.make_cross_account_comment_request(
            "PATCH", account1.id, token2, task_id=task1.id, comment_id=comment_id, data={"content": "Hacked"}
        )
        delete_response = self.make_cross_account_comment_request(
            "DELETE", account1.id, token2, task_id=task1.id, comment_id=comment_id
        )

        self.assert_error_response(get_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)
        self.assert_error_response(patch_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)
        self.assert_error_response(delete_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)

        verify_response = self.make_authenticated_comment_request(
            "GET", account1.id, token1, task_id=task1.id, comment_id=comment_id
        )
        assert verify_response.status_code == 200
        assert verify_response.json.get("id") == comment_id

    def test_invalid_json_request_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        invalid_json_data = "invalid json"

        with app.test_client() as client:
            response = client.post(
                self.get_comments_api_url(account.id, task.id),
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=invalid_json_data,
            )

        assert response.status_code == 400
