from server import app

from modules.comment.errors import CommentErrorCode
from modules.authentication.types import AccessTokenErrorCode
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):

    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
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
        task = self.create_test_task(account.id)
        comment_data = {}

        response = self.make_authenticated_request("POST", account.id, task.id, token, data=comment_data)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_create_comment_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request("POST", account.id, task.id, token, data={})

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_create_comment_unauthenticated(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_unauthenticated_request("POST", account.id, task.id, data=comment_data)

        self.assert_error_response(response, 401, "ACCESS_TOKEN_ERR_03")

    def test_get_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        response = self.make_authenticated_request("GET", account.id, task.id, token, comment_id=comment.id)

        assert response.status_code == 200
        assert response.json is not None
        self.assert_comment_response(
            response.json,
            content=comment.content,
            task_id=task.id,
            account_id=account.id,
        )

    def test_get_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("GET", account.id, task.id, token, comment_id=fake_comment_id)

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_get_comment_unauthenticated(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        response = self.make_unauthenticated_request("GET", account.id, task.id, comment_id=comment.id)

        self.assert_error_response(response, 401, "ACCESS_TOKEN_ERR_03")

    def test_get_paginated_comments_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        self.create_multiple_test_comments(task.id, account.id, 5)

        response = self.make_authenticated_request("GET", account.id, task.id, token)

        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json.get("items", [])) == 5
        assert response.json.get("total_count") == 5

    def test_get_paginated_comments_with_pagination(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        self.create_multiple_test_comments(task.id, account.id, 10)

        response = self.make_authenticated_request("GET", account.id, task.id, token, query_params="page=1&size=3")

        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json.get("items", [])) == 3
        assert response.json.get("total_count") == 10

    def test_get_paginated_comments_invalid_page(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request("GET", account.id, task.id, token, query_params="page=0")

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Page must be greater than 0" in response.json.get("message")

    def test_get_paginated_comments_invalid_size(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        response = self.make_authenticated_request("GET", account.id, task.id, token, query_params="size=0")

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Size must be greater than 0" in response.json.get("message")

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)
        updated_content = "Updated comment content"

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=comment.id, data={"content": updated_content}
        )

        assert response.status_code == 200
        assert response.json is not None
        self.assert_comment_response(
            response.json,
            content=updated_content,
            task_id=task.id,
            account_id=account.id,
        )

    def test_update_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        response = self.make_authenticated_request("PATCH", account.id, task.id, token, comment_id=comment.id, data={})

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)
        assert "Content is required" in response.json.get("message")

    def test_update_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request(
            "PATCH", account.id, task.id, token, comment_id=fake_comment_id, data={"content": "Updated content"}
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_update_comment_unauthenticated(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        response = self.make_unauthenticated_request(
            "PATCH", account.id, task.id, comment_id=comment.id, data={"content": "Updated content"}
        )

        self.assert_error_response(response, 401, "ACCESS_TOKEN_ERR_03")

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        response = self.make_authenticated_request("DELETE", account.id, task.id, token, comment_id=comment.id)

        assert response.status_code == 204

    def test_delete_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("DELETE", account.id, task.id, token, comment_id=fake_comment_id)

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_unauthenticated(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(task.id, account.id)

        response = self.make_unauthenticated_request("DELETE", account.id, task.id, comment_id=comment.id)

        self.assert_error_response(response, 401, "ACCESS_TOKEN_ERR_03")
