import json
import unittest
from typing import Callable, Tuple

from server import app
from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams, Account
from modules.logger.logger_manager import LoggerManager
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.rest_api.task_rest_api_server import TaskRestApiServer
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams, Task


class BaseTestTask(unittest.TestCase):
    TASK_API_URL = "http://127.0.0.1:8080/api/tasks"
    ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_TASK_TITLE = "Test Task"
    DEFAULT_TASK_DESCRIPTION = "This is a test task description"
    DEFAULT_USERNAME = "testuser@example.com"
    DEFAULT_PASSWORD = "testpassword"
    DEFAULT_FIRST_NAME = "Test"
    DEFAULT_LAST_NAME = "User"

    def setup_method(self, method: Callable) -> None:
        print(f"Executing:: {method.__name__}")
        LoggerManager.mount_logger()
        TaskRestApiServer.create()

    def teardown_method(self, method: Callable) -> None:
        print(f"Executed:: {method.__name__}")
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    # COMMON HELPER METHODS

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

    def create_test_task(self, account_id: str, title: str = None, description: str = None) -> Task:
        return TaskService.create_task(
            params=CreateTaskParams(
                account_id=account_id,
                title=title or self.DEFAULT_TASK_TITLE,
                description=description or self.DEFAULT_TASK_DESCRIPTION,
            )
        )

    def create_multiple_test_tasks(self, account_id: str, count: int) -> list[Task]:
        tasks = []
        for i in range(count):
            task = self.create_test_task(account_id=account_id, title=f"Task {i+1}", description=f"Description {i+1}")
            tasks.append(task)
        return tasks

    def make_authenticated_request(self, method: str, url: str, token: str, data: dict = None):
        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}
        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers={"Authorization": f"Bearer {token}"})
            elif method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data else None)
            elif method.upper() == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers={"Authorization": f"Bearer {token}"})

    def make_unauthenticated_request(self, method: str, url: str, data: dict = None):
        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url)
            elif method.upper() == "POST":
                return client.post(url, headers=self.HEADERS, data=json.dumps(data) if data else None)
            elif method.upper() == "PATCH":
                return client.patch(url, headers=self.HEADERS, data=json.dumps(data) if data else None)
            elif method.upper() == "DELETE":
                return client.delete(url)

    # ASSERTION HELPERS

    def assert_task_response(self, response_json: dict, expected_task: Task = None, **expected_fields):
        assert response_json.get("id") is not None
        assert response_json.get("account_id") is not None

        if expected_task:
            assert response_json.get("id") == expected_task.id
            assert response_json.get("account_id") == expected_task.account_id
            assert response_json.get("title") == expected_task.title
            assert response_json.get("description") == expected_task.description

        for field, value in expected_fields.items():
            assert response_json.get(field) == value

    def assert_error_response(self, response, expected_status: int, expected_error_code: str):
        assert response.status_code == expected_status
        assert response.json is not None
        assert response.json.get("code") == expected_error_code

    def assert_pagination_response(
        self,
        response_json: dict,
        expected_items_count: int,
        expected_total_count: int = None,
        expected_page: int = None,
        expected_size: int = None,
    ):
        assert "items" in response_json
        assert "pagination_params" in response_json
        assert "total_count" in response_json
        assert len(response_json["items"]) == expected_items_count

        if expected_total_count is not None:
            assert response_json["total_count"] == expected_total_count
        if expected_page is not None:
            assert response_json["pagination_params"]["page"] == expected_page
        if expected_size is not None:
            assert response_json["pagination_params"]["size"] == expected_size
