import sys, os
sys.path.append(os.path.abspath("src/apps/backend"))

from server import app
import json
import unittest
from typing import Tuple

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams, Account
from modules.logger.logger_manager import LoggerManager
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams, Task
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.types import Comment, CreateCommentParams
from modules.comment.comment_service import CommentService


class BaseTestComment(unittest.TestCase):
    ACCESS_TOKEN_URL = "/api/access-tokens"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_TASK_TITLE = "Test Task"
    DEFAULT_TASK_DESCRIPTION = "This is a test task description"
    DEFAULT_USERNAME = "testuser@example.com"
    DEFAULT_PASSWORD = "testpassword"
    DEFAULT_FIRST_NAME = "Test"
    DEFAULT_LAST_NAME = "User"
    DEFAULT_COMMENT_CONTENT = "This is a test comment"

    def setUp(self) -> None:
        LoggerManager.mount_logger()
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})


    def get_comment_api_url(self, account_id: str, task_id: str) -> str:
        return f"/api/accounts/{account_id}/tasks/{task_id}/comments"

    def get_comment_by_id_api_url(self, account_id: str, task_id: str, comment_id: str) -> str:
        return f"/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}"

    # --- Account & Token Helpers ---
    def create_test_account(self) -> Account:
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username=self.DEFAULT_USERNAME,
                password=self.DEFAULT_PASSWORD,
                first_name=self.DEFAULT_FIRST_NAME,
                last_name=self.DEFAULT_LAST_NAME,
            )
        )

    def get_access_token(self) -> str:
        with app.test_client() as client:
            response = client.post(
                self.ACCESS_TOKEN_URL,
                headers=self.HEADERS,
                data=json.dumps({"username": self.DEFAULT_USERNAME, "password": self.DEFAULT_PASSWORD}),
            )
            return response.json.get("token")

    def create_account_and_get_token(self) -> Tuple[Account, str]:
        account = self.create_test_account()
        token = self.get_access_token()
        return account, token

    # --- Task & Comment Helpers ---
    def create_test_task(self, account_id: str) -> Task:
        return TaskService.create_task(
            params=CreateTaskParams(
                account_id=account_id,
                title=self.DEFAULT_TASK_TITLE,
                description=self.DEFAULT_TASK_DESCRIPTION,
            )
        )

    def create_test_comment(self, task_id: str, account_id: str) -> Comment:
        return CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task_id,
                account_id=account_id,
                content=self.DEFAULT_COMMENT_CONTENT,
            )
        )

    # --- HTTP Request Helper ---
    def make_authenticated_request(
        self, method: str, account_id: str, task_id: str, token: str, comment_id: str = None, data: dict = None
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(account_id, task_id)

        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers=headers)
            elif method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data else None)
            elif method.upper() == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers=headers)

    # --- Response Assertion Helper ---
    def assert_comment_response(self, response_json: dict, expected_content: str = None):
        assert "id" in response_json
        assert "task_id" in response_json
        assert "account_id" in response_json
        assert "content" in response_json

        if expected_content:
            assert response_json["content"] == expected_content
