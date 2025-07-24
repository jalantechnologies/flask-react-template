import json

from server import app

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.types import AccessTokenErrorCode
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams, TaskErrorCode
from tests.modules.task.base_test_task import BaseTestTask

TASK_API_URL = "http://127.0.0.1:8080/api/tasks"
ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestTaskApi(BaseTestTask):
    def _create_account_and_get_token(self, username: str = "testuser", password: str = "testpassword") -> tuple:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password=password, username=username
            )
        )
        with app.test_client() as client:
            response = client.post(
                ACCESS_TOKEN_URL, headers=HEADERS, data=json.dumps({"username": username, "password": password})
            )
            token = response.json.get("token")
        return account, token

    def test_create_task_success(self) -> None:
        account, token = self._create_account_and_get_token()
        task_data = {"title": "Test Task", "description": "This is a test task description"}
        with app.test_client() as client:
            response = client.post(
                TASK_API_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"}, data=json.dumps(task_data)
            )
            assert response.status_code == 201
            assert response.json
            assert response.json.get("title") == "Test Task"
            assert response.json.get("description") == "This is a test task description"
            assert response.json.get("account_id") == account.id
            assert response.json.get("id") is not None

    def test_create_task_missing_title(self) -> None:
        account, token = self._create_account_and_get_token()
        task_data = {"description": "This is a test task description"}
        with app.test_client() as client:
            response = client.post(
                TASK_API_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"}, data=json.dumps(task_data)
            )
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == TaskErrorCode.BAD_REQUEST
            assert "Title is required" in response.json.get("message")

    def test_create_task_missing_description(self) -> None:
        account, token = self._create_account_and_get_token()
        task_data = {"title": "Test Task"}
        with app.test_client() as client:
            response = client.post(
                TASK_API_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"}, data=json.dumps(task_data)
            )
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == TaskErrorCode.BAD_REQUEST
            assert "Description is required" in response.json.get("message")

    def test_create_task_empty_body(self) -> None:
        account, token = self._create_account_and_get_token()
        with app.test_client() as client:
            response = client.post(
                TASK_API_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"}, data=json.dumps({})
            )
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == TaskErrorCode.BAD_REQUEST
            assert "Title is required" in response.json.get("message")

    def test_create_task_no_auth(self) -> None:
        task_data = {"title": "Test Task", "description": "This is a test task description"}
        with app.test_client() as client:
            response = client.post(TASK_API_URL, headers=HEADERS, data=json.dumps(task_data))
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_create_task_invalid_token(self) -> None:
        task_data = {"title": "Test Task", "description": "This is a test task description"}
        with app.test_client() as client:
            response = client.post(
                TASK_API_URL, headers={**HEADERS, "Authorization": "Bearer invalid_token"}, data=json.dumps(task_data)
            )
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_get_all_tasks_empty(self) -> None:
        account, token = self._create_account_and_get_token()
        with app.test_client() as client:
            response = client.get(TASK_API_URL, headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200
            assert response.json == []

    def test_get_all_tasks_with_tasks(self) -> None:
        account, token = self._create_account_and_get_token()
        for i in range(3):
            TaskService.create_task(
                params=CreateTaskParams(account_id=account.id, title=f"Task {i+1}", description=f"Description {i+1}")
            )
        with app.test_client() as client:
            response = client.get(TASK_API_URL, headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200
            assert len(response.json) == 3
            assert response.json[0]["title"] == "Task 3"
            assert response.json[1]["title"] == "Task 2"
            assert response.json[2]["title"] == "Task 1"

    def test_get_all_tasks_with_pagination(self) -> None:
        account, token = self._create_account_and_get_token()
        for i in range(5):
            TaskService.create_task(
                params=CreateTaskParams(account_id=account.id, title=f"Task {i+1}", description=f"Description {i+1}")
            )
        with app.test_client() as client:
            response = client.get(f"{TASK_API_URL}?page=1&size=2", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200
            assert len(response.json) == 2
            response2 = client.get(f"{TASK_API_URL}?page=2&size=2", headers={"Authorization": f"Bearer {token}"})
            assert response2.status_code == 200
            assert len(response2.json) == 2
            assert response.json[0]["id"] != response2.json[0]["id"]

    def test_get_all_tasks_no_auth(self) -> None:
        with app.test_client() as client:
            response = client.get(TASK_API_URL)
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_get_specific_task_success(self) -> None:
        account, token = self._create_account_and_get_token()
        created_task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Test Task", description="Test Description")
        )
        with app.test_client() as client:
            response = client.get(f"{TASK_API_URL}/{created_task.id}", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == created_task.id
            assert response.json.get("title") == "Test Task"
            assert response.json.get("description") == "Test Description"
            assert response.json.get("account_id") == account.id

    def test_get_specific_task_not_found(self) -> None:
        account, token = self._create_account_and_get_token()
        with app.test_client() as client:
            response = client.get(
                f"{TASK_API_URL}/507f1f77bcf86cd799439011", headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 404
            assert response.json
            assert response.json.get("code") == TaskErrorCode.NOT_FOUND

    def test_get_specific_task_no_auth(self) -> None:
        with app.test_client() as client:
            response = client.get(f"{TASK_API_URL}/507f1f77bcf86cd799439011")
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_update_task_success(self) -> None:
        account, token = self._create_account_and_get_token()
        created_task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Original Title", description="Original Description")
        )
        update_data = {"title": "Updated Title", "description": "Updated Description"}
        with app.test_client() as client:
            response = client.patch(
                f"{TASK_API_URL}/{created_task.id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(update_data),
            )
            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == created_task.id
            assert response.json.get("title") == "Updated Title"
            assert response.json.get("description") == "Updated Description"
            assert response.json.get("account_id") == account.id

    def test_update_task_missing_title(self) -> None:
        account, token = self._create_account_and_get_token()
        created_task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Original Title", description="Original Description")
        )
        update_data = {"description": "Updated Description"}
        with app.test_client() as client:
            response = client.patch(
                f"{TASK_API_URL}/{created_task.id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(update_data),
            )
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == TaskErrorCode.BAD_REQUEST
            assert "Title is required" in response.json.get("message")

    def test_update_task_missing_description(self) -> None:
        account, token = self._create_account_and_get_token()
        created_task = TaskService.create_task(
            params=CreateTaskParams(account_id=account.id, title="Original Title", description="Original Description")
        )
        update_data = {"title": "Updated Title"}
        with app.test_client() as client:
            response = client.patch(
                f"{TASK_API_URL}/{created_task.id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(update_data),
            )
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == TaskErrorCode.BAD_REQUEST
            assert "Description is required" in response.json.get("message")

    def test_update_task_not_found(self) -> None:
        account, token = self._create_account_and_get_token()
        update_data = {"title": "Updated Title", "description": "Updated Description"}
        with app.test_client() as client:
            response = client.patch(
                f"{TASK_API_URL}/507f1f77bcf86cd799439011",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(update_data),
            )
            assert response.status_code == 404
            assert response.json
            assert response.json.get("code") == TaskErrorCode.NOT_FOUND

    def test_update_task_no_auth(self) -> None:
        update_data = {"title": "Updated Title", "description": "Updated Description"}
        with app.test_client() as client:
            response = client.patch(
                f"{TASK_API_URL}/507f1f77bcf86cd799439011", headers=HEADERS, data=json.dumps(update_data)
            )
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_delete_task_success(self) -> None:
        account, token = self._create_account_and_get_token()
        created_task = TaskService.create_task(
            params=CreateTaskParams(
                account_id=account.id, title="Task to Delete", description="This task will be deleted"
            )
        )
        with app.test_client() as client:
            response = client.delete(f"{TASK_API_URL}/{created_task.id}", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 204
            assert response.data == b""
        with app.test_client() as client:
            get_response = client.get(f"{TASK_API_URL}/{created_task.id}", headers={"Authorization": f"Bearer {token}"})
            assert get_response.status_code == 404

    def test_delete_task_not_found(self) -> None:
        account, token = self._create_account_and_get_token()
        with app.test_client() as client:
            response = client.delete(
                f"{TASK_API_URL}/507f1f77bcf86cd799439011", headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 404
            assert response.json
            assert response.json.get("code") == TaskErrorCode.NOT_FOUND

    def test_delete_task_no_auth(self) -> None:
        with app.test_client() as client:
            response = client.delete(f"{TASK_API_URL}/507f1f77bcf86cd799439011")
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_tasks_are_account_isolated_via_api(self) -> None:
        account1, token1 = self._create_account_and_get_token("user1", "password1")
        account2, token2 = self._create_account_and_get_token("user2", "password2")
        task_data = {"title": "Account 1 Task", "description": "This belongs to account 1"}
        with app.test_client() as client:
            response = client.post(
                TASK_API_URL, headers={**HEADERS, "Authorization": f"Bearer {token1}"}, data=json.dumps(task_data)
            )
            account1_task_id = response.json.get("id")
        with app.test_client() as client:
            response = client.get(f"{TASK_API_URL}/{account1_task_id}", headers={"Authorization": f"Bearer {token2}"})
            assert response.status_code == 404
            assert response.json.get("code") == TaskErrorCode.NOT_FOUND
        with app.test_client() as client:
            response = client.patch(
                f"{TASK_API_URL}/{account1_task_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token2}"},
                data=json.dumps({"title": "Hacked", "description": "Hacked"}),
            )
            assert response.status_code == 404
            assert response.json.get("code") == TaskErrorCode.NOT_FOUND
        with app.test_client() as client:
            response = client.delete(
                f"{TASK_API_URL}/{account1_task_id}", headers={"Authorization": f"Bearer {token2}"}
            )
            assert response.status_code == 404
            assert response.json.get("code") == TaskErrorCode.NOT_FOUND
        with app.test_client() as client:
            response = client.get(f"{TASK_API_URL}/{account1_task_id}", headers={"Authorization": f"Bearer {token1}"})
            assert response.status_code == 200
            assert response.json.get("id") == account1_task_id

    def test_invalid_json_request_body(self) -> None:
        account, token = self._create_account_and_get_token()
        with app.test_client() as client:
            response = client.post(
                TASK_API_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"}, data="invalid json"
            )
            assert response.status_code == 400

    def test_no_request_body(self) -> None:
        account, token = self._create_account_and_get_token()
        with app.test_client() as client:
            response = client.post(TASK_API_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"})
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == TaskErrorCode.BAD_REQUEST
            assert "Request body is required" in response.json.get("message")
