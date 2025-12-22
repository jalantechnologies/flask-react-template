import json
import unittest
from typing import Tuple

from server import app
from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams, Account
from modules.logger.logger_manager import LoggerManager
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams, Task
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.comment_service import CommentService
from modules.comment.rest_api.comment_rest_api_server import CommentRestApiServer
from modules.comment.types import CreateCommentParams, Comment


class BaseTestComment(unittest.TestCase):
    ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_TASK_TITLE = "Test Task"
    DEFAULT_TASK_DESCRIPTION = "Task Description"
    DEFAULT_COMMENT_CONTENT = "Test Comment Content"
    DEFAULT_USERNAME = "testuser@example.com"
    DEFAULT_PASSWORD = "testpassword"

    def setUp(self) -> None:
        LoggerManager.mount_logger()
        
        # Patch pymongo client with mongomock
        import mongomock
        from unittest.mock import patch
        self.mongo_patcher = patch('modules.application.repository.ApplicationRepositoryClient.get_client')
        self.mock_get_client = self.mongo_patcher.start()
        self.mock_client = mongomock.MongoClient("mongodb://localhost/test_db")
        self.mock_get_client.return_value = self.mock_client
        
        # Patch database command to avoid validation errors in mongomock
        self.orig_command = self.mock_client.get_database("test_db").command
        self.mock_client.get_database("test_db").command = lambda *args, **kwargs: None

        CommentRestApiServer.create()

    def tearDown(self) -> None:
        self.mongo_patcher.stop()
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    # URL HELPER METHODS

    def get_comment_list_url(self, account_id: str, task_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments"

    def get_comment_detail_url(self, account_id: str, comment_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/comments/{comment_id}"

    # ACCOUNT AND TOKEN HELPER METHODS

    def create_test_account(
        self, username: str = None, password: str = None
    ) -> Account:
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username=username or self.DEFAULT_USERNAME,
                password=password or self.DEFAULT_PASSWORD,
                first_name="Test",
                last_name="User",
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

    # TASK AND COMMENT HELPER METHODS

    def create_test_task(self, account_id: str) -> Task:
        return TaskService.create_task(
            params=CreateTaskParams(
                account_id=account_id,
                title=self.DEFAULT_TASK_TITLE,
                description=self.DEFAULT_TASK_DESCRIPTION,
            )
        )

    def create_test_comment(self, account_id: str, task_id: str, content: str = None) -> Comment:
        return CommentService.create_comment(
            params=CreateCommentParams(
                account_id=account_id,
                task_id=task_id,
                content=content or self.DEFAULT_COMMENT_CONTENT,
            )
        )

    # HTTP REQUEST HELPER METHODS

    def make_authenticated_request(
        self, method: str, account_id: str, token: str, url: str, data: dict = None
    ):
        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers=headers)
            elif method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers=headers)

    # ASSERTION HELPER METHODS

    def assert_comment_response(self, response_json: dict, expected_comment: Comment = None, **expected_fields):
        assert response_json.get("id") is not None
        
        if expected_comment:
            assert response_json.get("id") == expected_comment.id
            assert response_json.get("account_id") == expected_comment.account_id
            assert response_json.get("task_id") == expected_comment.task_id
            
            if "content" not in expected_fields:
                assert response_json.get("content") == expected_comment.content

        for field, value in expected_fields.items():
            assert response_json.get(field) == value
