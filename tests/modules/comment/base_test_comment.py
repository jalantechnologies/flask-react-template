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
        CommentRestApiServer.create()

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})
        from modules.task.internal.store.task_repository import TaskRepository
        TaskRepository.collection().delete_many({})

    def get_comment_api_url(self, account_id: str, task_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments"

    def get_comment_by_id_api_url(self, account_id: str, task_id: str, comment_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}"

    def create_test_account(
        self, username: str = None, password: str = None, first_name: str = None, last_name: str = None
    ) -> Account:
        if username is None:
            username = self.DEFAULT_USERNAME
        if password is None:
            password = self.DEFAULT_PASSWORD
        if first_name is None:
            first_name = self.DEFAULT_FIRST_NAME
        if last_name is None:
            last_name = self.DEFAULT_LAST_NAME

        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name=first_name, last_name=last_name, password=password, username=username
            )
        )

    def create_account_and_get_token(self) -> Tuple[Account, str]:
        account = self.create_test_account()
        with app.test_client() as client:
            response = client.post(
                self.ACCESS_TOKEN_URL,
                headers=self.HEADERS,
                data=json.dumps({"username": account.username, "password": self.DEFAULT_PASSWORD}),
            )
            assert response.status_code == 201
            return account, response.json.get("token")

    def create_test_task(self, account_id: str, title: str = None, description: str = None) -> Task:
        if title is None:
            title = self.DEFAULT_TASK_TITLE
        if description is None:
            description = self.DEFAULT_TASK_DESCRIPTION

        return TaskService.create_task(
            params=CreateTaskParams(account_id=account_id, title=title, description=description)
        )

    def create_test_comment(self, task_id: str, account_id: str, content: str = None) -> Comment:
        if content is None:
            content = self.DEFAULT_COMMENT_CONTENT

        return CommentService.create_comment(
            params=CreateCommentParams(task_id=task_id, account_id=account_id, content=content)
        )

    def create_multiple_test_comments(self, task_id: str, account_id: str, count: int) -> list[Comment]:
        comments = []
        for i in range(count):
            comment = self.create_test_comment(
                task_id=task_id, account_id=account_id, content=f"Comment {i+1}"
            )
            comments.append(comment)
        return comments

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
            if method.upper() == "GET":
                return client.get(url, headers={"Authorization": f"Bearer {token}"})
            elif method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers={"Authorization": f"Bearer {token}"})

    def make_unauthenticated_request(self, method: str, account_id: str, task_id: str, comment_id: str = None, data: dict = None):
        if comment_id:
            url = self.get_comment_by_id_api_url(account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(account_id, task_id)

        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url)
            elif method.upper() == "POST":
                return client.post(url, headers=self.HEADERS, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "PATCH":
                return client.patch(url, headers=self.HEADERS, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "DELETE":
                return client.delete(url)

    def assert_comment_response(self, response_data: dict, content: str, task_id: str, account_id: str):
        assert response_data.get("content") == content
        assert response_data.get("task_id") == task_id
        assert response_data.get("account_id") == account_id
        assert response_data.get("id") is not None

    def assert_error_response(self, response, expected_status_code: int, expected_error_code: str):
        assert response.status_code == expected_status_code
        assert response.json is not None
        assert response.json.get("code") == expected_error_code
