from server import app

from modules.authentication.types import AccessTokenErrorCode
from modules.comments.types import CommentErrorCode
from tests.modules.comments.base_test_comments import BaseTestComments


class TestCommentsApi(BaseTestComments):

    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        comment_data = {"text": self.DEFAULT_COMMENT_TEXT}

        response = self.make_authenticated_comment_request(
            "POST", account.id, self.DEFAULT_TASK_ID, token, data=comment_data
        )

        assert response.status_code == 201
        assert response.json is not None
        self.assert_comment_response(
            response.json, text=self.DEFAULT_COMMENT_TEXT, account_id=account.id, task_id=self.DEFAULT_TASK_ID
        )

    def test_create_comment_missing_text(self) -> None:
        account, token = self.create_account_and_get_token()
        comment_data = {}

        response = self.make_authenticated_comment_request(
            "POST", account.id, self.DEFAULT_TASK_ID, token, data=comment_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Text is required" in response.json.get("message")

    def test_create_comment_empty_text(self) -> None:
        account, token = self.create_account_and_get_token()
        comment_data = {"text": ""}

        response = self.make_authenticated_comment_request(
            "POST", account.id, self.DEFAULT_TASK_ID, token, data=comment_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Text cannot be empty" in response.json.get("message")

    def test_create_comment_whitespace_text(self) -> None:
        account, token = self.create_account_and_get_token()
        comment_data = {"text": "   "}

        response = self.make_authenticated_comment_request(
            "POST", account.id, self.DEFAULT_TASK_ID, token, data=comment_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Text cannot be empty" in response.json.get("message")

    def test_create_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        comment_data = {"text": self.DEFAULT_COMMENT_TEXT}

        response = self.make_unauthenticated_comment_request(
            "POST", account.id, self.DEFAULT_TASK_ID, data=comment_data
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_create_comment_invalid_token(self) -> None:
        account, _ = self.create_account_and_get_token()
        invalid_token = "invalid_token"
        comment_data = {"text": self.DEFAULT_COMMENT_TEXT}

        response = self.make_authenticated_comment_request(
            "POST", account.id, self.DEFAULT_TASK_ID, invalid_token, data=comment_data
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.ACCESS_TOKEN_INVALID)

    def test_get_comments_empty(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.make_authenticated_comment_request("GET", account.id, self.DEFAULT_TASK_ID, token)

        assert response.status_code == 200
        assert response.json == []

    def test_get_comments_with_comments(self) -> None:
        account, token = self.create_account_and_get_token()
        comments = self.create_multiple_test_comments(account_id=account.id, task_id=self.DEFAULT_TASK_ID, count=3)

        response = self.make_authenticated_comment_request("GET", account.id, self.DEFAULT_TASK_ID, token)

        assert response.status_code == 200
        assert len(response.json) == 3

        assert response.json[0]["text"] == "Comment 3"
        assert response.json[1]["text"] == "Comment 2"
        assert response.json[2]["text"] == "Comment 1"

    def test_get_comments_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()

        response = self.make_unauthenticated_comment_request("GET", account.id, self.DEFAULT_TASK_ID)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        created_comment = self.create_test_comment(account_id=account.id, task_id=self.DEFAULT_TASK_ID)
        update_data = {"text": "Updated comment text"}

        response = self.make_authenticated_comment_request(
            "PUT", account.id, self.DEFAULT_TASK_ID, token, comment_id=created_comment.id, data=update_data
        )

        assert response.status_code == 200
        self.assert_comment_response(
            response.json,
            id=created_comment.id,
            account_id=account.id,
            task_id=self.DEFAULT_TASK_ID,
            text="Updated comment text",
        )
        assert response.json.get("updated_at") is not None

    def test_update_comment_missing_text(self) -> None:
        account, token = self.create_account_and_get_token()
        created_comment = self.create_test_comment(account_id=account.id, task_id=self.DEFAULT_TASK_ID)
        update_data = {}

        response = self.make_authenticated_comment_request(
            "PUT", account.id, self.DEFAULT_TASK_ID, token, comment_id=created_comment.id, data=update_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Text is required" in response.json.get("message")

    def test_update_comment_empty_text(self) -> None:
        account, token = self.create_account_and_get_token()
        created_comment = self.create_test_comment(account_id=account.id, task_id=self.DEFAULT_TASK_ID)
        update_data = {"text": ""}

        response = self.make_authenticated_comment_request(
            "PUT", account.id, self.DEFAULT_TASK_ID, token, comment_id=created_comment.id, data=update_data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Text cannot be empty" in response.json.get("message")

    def test_update_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"text": "Updated text"}

        response = self.make_authenticated_comment_request(
            "PUT", account.id, self.DEFAULT_TASK_ID, token, comment_id=non_existent_comment_id, data=update_data
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_update_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        fake_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"text": "Updated text"}

        response = self.make_unauthenticated_comment_request(
            "PUT", account.id, self.DEFAULT_TASK_ID, comment_id=fake_comment_id, data=update_data
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        created_comment = self.create_test_comment(account_id=account.id, task_id=self.DEFAULT_TASK_ID)

        delete_response = self.make_authenticated_comment_request(
            "DELETE", account.id, self.DEFAULT_TASK_ID, token, comment_id=created_comment.id
        )

        assert delete_response.status_code == 200
        assert delete_response.json == {"status": "deleted"}

        comments_response = self.make_authenticated_comment_request("GET", account.id, self.DEFAULT_TASK_ID, token)
        assert len(comments_response.json) == 0

    def test_delete_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_comment_request(
            "DELETE", account.id, self.DEFAULT_TASK_ID, token, comment_id=non_existent_comment_id
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_unauthenticated_comment_request(
            "DELETE", account.id, self.DEFAULT_TASK_ID, comment_id=fake_comment_id
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_comments_are_account_isolated_via_api(self) -> None:
        print("DEBUG: Starting test")
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        account1, token1 = self.create_account_and_get_token(f"user1_{unique_id}@example.com", "password1")
        account2, token2 = self.create_account_and_get_token(f"user2_{unique_id}@example.com", "password2")

        comment_data = {"text": "Account 1 Comment"}
        create_response = self.make_authenticated_comment_request(
            "POST", account1.id, self.DEFAULT_TASK_ID, token1, data=comment_data
        )
        account1_comment_id = create_response.json.get("id")

        get_response = self.make_cross_account_comment_request(
            "GET", account1.id, self.DEFAULT_TASK_ID, token2, comment_id=account1_comment_id
        )
        put_response = self.make_cross_account_comment_request(
            "PUT", account1.id, self.DEFAULT_TASK_ID, token2, comment_id=account1_comment_id, data={"text": "Hacked"}
        )
        delete_response = self.make_cross_account_comment_request(
            "DELETE", account1.id, self.DEFAULT_TASK_ID, token2, comment_id=account1_comment_id
        )

        self.assert_error_response(get_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)
        self.assert_error_response(put_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)
        self.assert_error_response(delete_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)

        verify_response = self.make_authenticated_comment_request(
            "GET", account1.id, self.DEFAULT_TASK_ID, token1, comment_id=account1_comment_id
        )
        assert verify_response.status_code == 200
        assert verify_response.json.get("id") == account1_comment_id

    def test_comments_are_task_isolated(self) -> None:
        account, token = self.create_account_and_get_token()
        task1_id = "task-1"
        task2_id = "task-2"

        comment1 = self.create_test_comment(account_id=account.id, task_id=task1_id)
        comment2 = self.create_test_comment(account_id=account.id, task_id=task2_id)

        response1 = self.make_authenticated_comment_request("GET", account.id, task1_id, token)
        assert len(response1.json) == 1
        assert response1.json[0]["id"] == comment1.id

        response2 = self.make_authenticated_comment_request("GET", account.id, task2_id, token)
        assert len(response2.json) == 1
        assert response2.json[0]["id"] == comment2.id

    def test_invalid_json_request_body(self) -> None:
        account, token = self.create_account_and_get_token()
        invalid_json_data = "invalid json"

        with app.test_client() as client:
            response = client.post(
                self.get_comments_api_url(account.id, self.DEFAULT_TASK_ID),
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=invalid_json_data,
            )

        assert response.status_code == 400
