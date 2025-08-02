import json
from typing import Tuple

from server import app

from modules.account.account_service import AccountService
from modules.account.types import Account, CreateAccountByUsernameAndPasswordParams
from modules.authentication.types import AccessTokenErrorCode
from tests.modules.task.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):
    ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_USERNAME = "testuser@example.com"
    DEFAULT_PASSWORD = "testpassword"
    DEFAULT_FIRST_NAME = "Test"
    DEFAULT_LAST_NAME = "User"

    def setUp(self):
        super().setUp()

    def get_comment_api_url(self, account_id: str, task_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments"

    def get_comment_by_id_api_url(self, account_id: str, task_id: str, comment_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}"

    def create_test_account(
        self, username: str = None, password: str = None, first_name: str = None, last_name: str = None
    ) -> Account:
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username=username or self.DEFAULT_USERNAME,
                password=password or self.DEFAULT_PASSWORD,
                first_name=first_name or self.DEFAULT_FIRST_NAME,
                last_name=last_name or self.DEFAULT_LAST_NAME,
            )
        )

    def get_access_token(self, username: str = None, password: str = None) -> str:
        with app.test_client() as client:
            response = client.post(
                self.ACCESS_TOKEN_URL,
                headers=self.HEADERS,
                data=json.dumps(
                    {"username": username or self.DEFAULT_USERNAME, "password": password or self.DEFAULT_PASSWORD}
                ),
            )
            return response.json.get("token")

    def create_account_and_get_token(self, username: str = None, password: str = None) -> Tuple[Account, str]:
        test_username = username or f"testuser_{id(self)}@example.com"
        test_password = password or self.DEFAULT_PASSWORD

        account = self.create_test_account(username=test_username, password=test_password)
        token = self.get_access_token(username=test_username, password=test_password)
        return account, token

    def make_authenticated_request(
        self,
        method: str,
        account_id: str,
        task_id: str,
        token: str,
        comment_id: str = None,
        data: dict = None,
        query_params: str = "",
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(account_id, task_id)

        if query_params:
            url += f"?{query_params}"

        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            if method == "GET":
                return client.get(url, headers=headers)
            elif method == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data else None)
            elif method == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data else None)
            elif method == "DELETE":
                return client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

    def make_unauthenticated_request(
        self, method: str, account_id: str, task_id: str, comment_id: str = None, data: dict = None
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(account_id, task_id)

        with app.test_client() as client:
            if method == "GET":
                return client.get(url, headers=self.HEADERS)
            elif method == "POST":
                return client.post(url, headers=self.HEADERS, data=json.dumps(data) if data else None)
            elif method == "PATCH":
                return client.patch(url, headers=self.HEADERS, data=json.dumps(data) if data else None)
            elif method == "DELETE":
                return client.delete(url, headers=self.HEADERS)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

    def assert_comment_response(self, response_json: dict, expected_comment: dict = None, **expected_fields):
        if expected_comment:
            for key, value in expected_comment.items():
                self.assertEqual(response_json.get(key), value)

        for key, value in expected_fields.items():
            self.assertEqual(response_json.get(key), value)

    def assert_error_response(self, response, expected_status: int, expected_error_code: str):
        self.assertEqual(response.status_code, expected_status)
        response_json = response.json
        self.assertIsNotNone(response_json)
        self.assertEqual(response_json.get("code"), expected_error_code)

    def test_create_comment_success(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment_data = {"content": "Test comment content"}

        # Act
        response = self.make_authenticated_request("POST", account.id, str(task.id), token, data=comment_data)

        # Assert
        self.assertEqual(response.status_code, 201)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertEqual(response_data["task_id"], str(task.id))
        self.assertEqual(response_data["account_id"], account.id)
        self.assertEqual(response_data["content"], "Test comment content")
        self.assertIn("id", response_data)

    def test_create_comment_empty_request_body(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Act
        response = self.make_authenticated_request("POST", account.id, str(task.id), token)

        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertIn("Request body is required", response_data.get("message", ""))

    def test_create_comment_missing_content(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment_data = {}

        # Act
        response = self.make_authenticated_request("POST", account.id, str(task.id), token, data=comment_data)

        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertIn("Content is required", response_data.get("message", ""))

    def test_create_comment_no_auth(self):
        # Arrange
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment_data = {"content": "Test comment content"}

        # Act
        response = self.make_unauthenticated_request("POST", account.id, str(task.id), data=comment_data)

        # Assert
        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_get_comment_success(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(str(task.id), account.id, "Test Comment")

        # Act
        response = self.make_authenticated_request("GET", account.id, str(task.id), token, str(comment.id))

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertEqual(response_data["id"], str(comment.id))
        self.assertEqual(response_data["task_id"], str(task.id))
        self.assertEqual(response_data["account_id"], account.id)
        self.assertEqual(response_data["content"], "Test Comment")

    def test_get_comment_not_found(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Act
        response = self.make_authenticated_request("GET", account.id, str(task.id), token, "non_existent_comment_id")

        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertIn("Comment not found", response_data.get("message", ""))

    def test_get_task_comments_success(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        self.create_test_comment(str(task.id), account.id, "Comment 1")
        self.create_test_comment(str(task.id), account.id, "Comment 2")

        # Act
        response = self.make_authenticated_request("GET", account.id, str(task.id), token)

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertEqual(response_data["total_count"], 2)
        self.assertEqual(len(response_data["items"]), 2)
        # Check that both comments are present (order may vary due to timing)
        comment_contents = [comment["content"] for comment in response_data["items"]]
        self.assertIn("Comment 1", comment_contents)
        self.assertIn("Comment 2", comment_contents)

    def test_get_task_comments_with_pagination(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        for i in range(5):
            self.create_test_comment(str(task.id), account.id, f"Comment {i}")

        # Act
        response = self.make_authenticated_request("GET", account.id, str(task.id), token, query_params="page=1&size=3")

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertEqual(response_data["total_count"], 5)
        self.assertEqual(len(response_data["items"]), 3)
        self.assertEqual(response_data["pagination_params"]["page"], 1)
        self.assertEqual(response_data["pagination_params"]["size"], 3)

    def test_update_comment_success(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(str(task.id), account.id)
        update_data = {"content": "Updated comment content"}

        # Act
        response = self.make_authenticated_request(
            "PATCH", account.id, str(task.id), token, str(comment.id), update_data
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertEqual(response_data["id"], str(comment.id))
        self.assertEqual(response_data["content"], "Updated comment content")

    def test_update_comment_missing_content(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(str(task.id), account.id)
        update_data = {}

        # Act
        response = self.make_authenticated_request(
            "PATCH", account.id, str(task.id), token, str(comment.id), update_data
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertIn("Content is required", response_data.get("message", ""))

    def test_update_comment_not_found(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        update_data = {"content": "Updated comment content"}

        # Act
        response = self.make_authenticated_request(
            "PATCH", account.id, str(task.id), token, "non_existent_comment_id", update_data
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertIn("Comment not found", response_data.get("message", ""))

    def test_delete_comment_success(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(str(task.id), account.id)

        # Act
        response = self.make_authenticated_request("DELETE", account.id, str(task.id), token, str(comment.id))

        # Assert
        self.assertEqual(response.status_code, 204)
        deleted_comment = self.get_comment_by_id(str(comment.id))
        self.assertIsNone(deleted_comment)

    def test_delete_comment_not_found(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Act
        response = self.make_authenticated_request("DELETE", account.id, str(task.id), token, "non_existent_comment_id")

        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = response.json
        self.assertIsNotNone(response_data)
        self.assertIn("Comment not found", response_data.get("message", ""))

    def test_invalid_pagination_parameters(self):
        # Arrange
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)

        # Act - Test invalid page
        response = self.make_authenticated_request("GET", account.id, str(task.id), token, query_params="page=0")

        # Assert
        self.assert_error_response(response, 400, "COMMENT_ERR_02")
        self.assertIn("Page must be greater than 0", response.json.get("message"))

        # Act - Test invalid size
        response = self.make_authenticated_request("GET", account.id, str(task.id), token, query_params="size=-1")

        # Assert
        self.assert_error_response(response, 400, "COMMENT_ERR_02")
        self.assertIn("Size must be greater than 0", response.json.get("message"))
