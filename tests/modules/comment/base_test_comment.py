import json
import unittest
from typing import Tuple

from server import app

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import Account, CreateAccountByUsernameAndPasswordParams
from modules.comment.comment_service import CommentService
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.rest_api.comment_rest_api_server import CommentRestApiServer
from modules.comment.types import Comment, CreateCommentParams
from modules.logger.logger_manager import LoggerManager
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams, Task


class BaseTestComment(unittest.TestCase):
    ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_COMMENT_CONTENT = "This is a test comment"
    DEFAULT_AUTHOR_NAME = "Test Author"
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
        TaskRepository.collection().delete_many({})
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

    def create_test_comment(
        self, task_id: str, account_id: str, content: str = None, author_name: str = None
    ) -> Comment:
        return CommentService.create_comment(
            params=CreateCommentParams(
                task_id=task_id,
                account_id=account_id,
                content=content or self.DEFAULT_COMMENT_CONTENT,
                author_name=author_name or self.DEFAULT_AUTHOR_NAME,
            )
        )

    def create_multiple_test_comments(self, task_id: str, account_id: str, count: int) -> list[Comment]:
        comments = []
        for i in range(count):
            comment = self.create_test_comment(
                task_id=task_id, account_id=account_id, content=f"Comment {i+1}", author_name=f"Author {i+1}"
            )
            comments.append(comment)
        return comments

    # HTTP REQUEST HELPER METHODS

    def make_authenticated_request(
        self,
        method: str,
        account_id: str,
        token: str,
        task_id: str,
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
            if method.upper() == "GET":
                return client.get(url, headers={"Authorization": f"Bearer {token}"})
            elif method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers={"Authorization": f"Bearer {token}"})

    def make_unauthenticated_request(
        self, method: str, account_id: str, task_id: str, comment_id: str = None, data: dict = None
    ):
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

    def make_cross_account_request(
        self,
        method: str,
        target_account_id: str,
        auth_token: str,
        task_id: str,
        comment_id: str = None,
        data: dict = None,
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(target_account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(target_account_id, task_id)

        headers = {**self.HEADERS, "Authorization": f"Bearer {auth_token}"}

        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers={"Authorization": f"Bearer {auth_token}"})
            elif method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers={"Authorization": f"Bearer {auth_token}"})

    # ASSERTION HELPER METHODS

    def assert_comment_response(self, response_json: dict, expected_comment: Comment = None, **expected_fields):
        assert response_json.get("id") is not None
        assert response_json.get("task_id") is not None
        assert response_json.get("account_id") is not None
        assert response_json.get("content") is not None
        assert response_json.get("author_name") is not None
        assert response_json.get("active") is not None
        assert response_json.get("created_at") is not None
        assert response_json.get("updated_at") is not None

        if expected_comment:
            assert response_json.get("id") == expected_comment.id
            assert response_json.get("task_id") == expected_comment.task_id
            assert response_json.get("account_id") == expected_comment.account_id
            assert response_json.get("content") == expected_comment.content
            assert response_json.get("author_name") == expected_comment.author_name
            assert response_json.get("active") == expected_comment.active

        for field, value in expected_fields.items():
            assert response_json.get(field) == value

    def assert_error_response(self, response, expected_status: int, expected_error_message: str = None):
        assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"
        if expected_error_message:
            assert response.json is not None, f"Expected JSON response, got None. Response data: {response.data}"
            assert expected_error_message in response.json.get(
                "error", ""
            ), f"Expected error message containing '{expected_error_message}', got '{response.json.get('error')}'"

    def assert_pagination_response(
        self,
        response_json: dict,
        expected_items_count: int,
        expected_total_count: int = None,
        expected_page: int = None,
        expected_size: int = None,
    ):
        assert "items" in response_json
        assert "pagination" in response_json
        assert "total_count" in response_json["pagination"]
        assert len(response_json["items"]) == expected_items_count

        if expected_total_count is not None:
            assert response_json["pagination"]["total_count"] == expected_total_count
        if expected_page is not None:
            assert response_json["pagination"]["page"] == expected_page
        if expected_size is not None:
            assert response_json["pagination"]["size"] == expected_size
