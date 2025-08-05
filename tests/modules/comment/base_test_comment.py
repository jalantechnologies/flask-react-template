import json
import unittest
from typing import Tuple

from server import app
from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams, Account
from modules.logger.logger_manager import LoggerManager
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.rest_api.comment_rest_api_server import CommentRestApiServer
from modules.comment.comment_service import CommentService
from modules.comment.types import CreateCommentParams, Comment
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams, Task


class BaseTestComment(unittest.TestCase):
    ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_COMMENT_CONTENT = "This is a test comment"
    DEFAULT_TASK_TITLE = "Test Task"
    DEFAULT_TASK_DESCRIPTION = "This is a test task description"
    DEFAULT_USERNAME = "testuser@example.com"
    DEFAULT_PASSWORD = "testpassword"
    DEFAULT_FIRST_NAME = "Test"
    DEFAULT_LAST_NAME = "User"

    def setUp(self) -> None:
        LoggerManager.mount_logger()
        CommentRestApiServer.create_blueprint()

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    # URL HELPER METHODS

    def get_comment_api_url(self, account_id: str, task_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments"

    def get_comment_by_id_api_url(self, account_id: str, task_id: str, comment_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}"

    # ACCOUNT AND TOKEN HELPER METHODS

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

    # TASK HELPER METHODS

    def create_test_task(self, account_id: str, title: str = None, description: str = None) -> Task:
        return TaskService.create_task(
            params=CreateTaskParams(
                account_id=account_id,
                title=title or self.DEFAULT_TASK_TITLE,
                description=description or self.DEFAULT_TASK_DESCRIPTION,
            )
        )

    # COMMENT HELPER METHODS

    def create_test_comment(self, account_id: str, task_id: str, content: str = None) -> Comment:
        return CommentService.create_comment(
            params=CreateCommentParams(
                account_id=account_id,
                task_id=task_id,
                content=content or self.DEFAULT_COMMENT_CONTENT,
            )
        )

    def create_multiple_test_comments(self, account_id: str, task_id: str, count: int) -> list[Comment]:
        comments = []
        for i in range(count):
            comment = self.create_test_comment(
                account_id=account_id, 
                task_id=task_id, 
                content=f"Comment {i+1}"
            )
            comments.append(comment)
        return comments

    # HTTP REQUEST HELPER METHODS

    def make_authenticated_request(
        self, method: str, account_id: str, task_id: str, token: str, comment_id: str = None, data: dict = None, query_params: str = ""
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
                raise ValueError(f"Unsupported method: {method}")

    def make_unauthenticated_request(self, method: str, account_id: str, task_id: str, comment_id: str = None, data: dict = None):
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
                raise ValueError(f"Unsupported method: {method}")

    def make_cross_account_request(
        self, method: str, target_account_id: str, task_id: str, auth_token: str, comment_id: str = None, data: dict = None
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(target_account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(target_account_id, task_id)

        headers = {**self.HEADERS, "Authorization": f"Bearer {auth_token}"}

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
                raise ValueError(f"Unsupported method: {method}")

    # ASSERTION HELPER METHODS

    def assert_comment_response(self, response_json: dict, expected_comment: Comment = None, **expected_fields):
        self.assertIn("id", response_json)
        self.assertIn("task_id", response_json)
        self.assertIn("account_id", response_json)
        self.assertIn("content", response_json)
        self.assertIn("created_at", response_json)
        self.assertIn("updated_at", response_json)

        if expected_comment:
            self.assertEqual(response_json["id"], expected_comment.id)
            self.assertEqual(response_json["task_id"], expected_comment.task_id)
            self.assertEqual(response_json["account_id"], expected_comment.account_id)
            self.assertEqual(response_json["content"], expected_comment.content)

        for field, value in expected_fields.items():
            self.assertEqual(response_json[field], value)

    def assert_error_response(self, response, expected_status: int, expected_error_code: str):
        self.assertEqual(response.status_code, expected_status)
        response_json = response.get_json()
        self.assertIn("code", response_json)
        self.assertEqual(response_json["code"], expected_error_code)

    def assert_pagination_response(
        self,
        response_json: dict,
        expected_items_count: int,
        expected_total_count: int = None,
        expected_page: int = None,
        expected_size: int = None,
    ):
        self.assertIn("items", response_json)
        self.assertIn("total_count", response_json)
        self.assertIn("page", response_json)
        self.assertIn("per_page", response_json)

        self.assertEqual(len(response_json["items"]), expected_items_count)

        if expected_total_count is not None:
            self.assertEqual(response_json["total_count"], expected_total_count)
        if expected_page is not None:
            self.assertEqual(response_json["page"], expected_page)
        if expected_size is not None:
            self.assertEqual(response_json["per_page"], expected_size) 