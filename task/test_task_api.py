from server import app

from modules.authentication.types import AccessTokenErrorCode
from modules.task.types import TaskErrorCode
from tests.modules.task.base_test_task import BaseTestTask


class TestTaskApi(BaseTestTask):

    def test_create_task_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task_data = {"title": self.DEFAULT_TASK_TITLE, "description": self.DEFAULT_TASK_DESCRIPTION}

        response = self.make_authenticated_request("POST", account.id, token, data=task_data)

        assert response.status_code == 201
        assert response.json is not None
        self.assert_task_response(
            response.json,
            title=self.DEFAULT_TASK_TITLE,
            description=self.DEFAULT_TASK_DESCRIPTION,
            account_id=account.id,
        )

    def test_create_task_missing_title(self) -> None:
        account, token = self.create_account_and_get_token()
        task_data = {"description": self.DEFAULT_TASK_DESCRIPTION}

        response = self.make_authenticated_request("POST", account.id, token, data=task_data)

        self.assert_error_response(response, 400, TaskErrorCode.BAD_REQUEST)
        assert "Title is required" in response.json.get("message")

    def test_create_task_missing_description(self) -> None:
        account, token = self.create_account_and_get_token()
        task_data = {"title": self.DEFAULT_TASK_TITLE}

        response = self.make_authenticated_request("POST", account.id, token, data=task_data)

        self.assert_error_response(response, 400, TaskErrorCode.BAD_REQUEST)
        assert "Description is required" in response.json.get("message")

    def test_create_task_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task_data = {}

        response = self.make_authenticated_request("POST", account.id, token, data=task_data)

        self.assert_error_response(response, 400, TaskErrorCode.BAD_REQUEST)
        assert "Title is required" in response.json.get("message")

    def test_create_task_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task_data = {"title": self.DEFAULT_TASK_TITLE, "description": self.DEFAULT_TASK_DESCRIPTION}

        response = self.make_unauthenticated_request("POST", account.id, data=task_data)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_create_task_invalid_token(self) -> None:
        account, _ = self.create_account_and_get_token()
        invalid_token = "invalid_token"
        task_data = {"title": self.DEFAULT_TASK_TITLE, "description": self.DEFAULT_TASK_DESCRIPTION}

        response = self.make_authenticated_request("POST", account.id, invalid_token, data=task_data)

        self.assert_error_response(response, 401, AccessTokenErrorCode.ACCESS_TOKEN_INVALID)

    def test_get_all_tasks_empty(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.make_authenticated_request("GET", account.id, token)

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=0, expected_total_count=0)

    def test_get_all_tasks_with_tasks(self) -> None:
        account, token = self.create_account_and_get_token()
        tasks = self.create_multiple_test_tasks(account_id=account.id, count=3)

        response = self.make_authenticated_request("GET", account.id, token)

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=3, expected_total_count=3)

        assert response.json["items"][0]["title"] == "Task 3"
        assert response.json["items"][1]["title"] == "Task 2"
        assert response.json["items"][2]["title"] == "Task 1"

    def test_get_all_tasks_with_pagination(self) -> None:
        account, token = self.create_account_and_get_token()
        self.create_multiple_test_tasks(account_id=account.id, count=5)

        response1 = self.make_authenticated_request("GET", account.id, token, query_params="page=1&size=2")
        response2 = self.make_authenticated_request("GET", account.id, token, query_params="page=2&size=2")

        assert response1.status_code == 200
        self.assert_pagination_response(
            response1.json, expected_items_count=2, expected_total_count=5, expected_page=1, expected_size=2
        )

        assert response2.status_code == 200
        self.assert_pagination_response(
            response2.json, expected_items_count=2, expected_total_count=5, expected_page=2, expected_size=2
        )

        assert response1.json["items"][0]["id"] != response2.json["items"][0]["id"]

    def test_get_all_tasks_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()

        response = self.make_unauthenticated_request("GET", account.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_get_specific_task_success(self) -> None:
        account, token = self.create_account_and_get_token()
        created_task = self.create_test_task(account_id=account.id)

        response = self.make_authenticated_request("GET", account.id, token, task_id=created_task.id)

        assert response.status_code == 200
        self.assert_task_response(response.json, expected_task=created_task)

    def test_get_specific_task_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("GET", account.id, token, task_id=non_existent_task_id)

        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_get_specific_task_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        fake_task_id = "507f1f77bcf86cd799439011"

        response = self.make_unauthenticated_request("GET", account.id, task_id=fake_task_id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_update_task_success(self) -> None:
        account, token = self.create_account_and_get_token()
        created_task = self.create_test_task(
            account_id=account.id, title="Original Title", description="Original Description"
        )
        update_data = {"title": "Updated Title", "description": "Updated Description"}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task_id=created_task.id, data=update_data
        )

        assert response.status_code == 200
        self.assert_task_response(
            response.json,
            id=created_task.id,
            account_id=account.id,
            title="Updated Title",
            description="Updated Description",
        )

    def test_update_task_missing_title(self) -> None:
        account, token = self.create_account_and_get_token()
        created_task = self.create_test_task(account_id=account.id)
        update_data = {"description": "Updated Description"}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task_id=created_task.id, data=update_data
        )

        self.assert_error_response(response, 400, TaskErrorCode.BAD_REQUEST)
        assert "Title is required" in response.json.get("message")

    def test_update_task_missing_description(self) -> None:
        account, token = self.create_account_and_get_token()
        created_task = self.create_test_task(account_id=account.id)
        update_data = {"title": "Updated Title"}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task_id=created_task.id, data=update_data
        )

        self.assert_error_response(response, 400, TaskErrorCode.BAD_REQUEST)
        assert "Description is required" in response.json.get("message")

    def test_update_task_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"
        update_data = {"title": "Updated Title", "description": "Updated Description"}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task_id=non_existent_task_id, data=update_data
        )

        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_update_task_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        fake_task_id = "507f1f77bcf86cd799439011"
        update_data = {"title": "Updated Title", "description": "Updated Description"}

        response = self.make_unauthenticated_request("PATCH", account.id, task_id=fake_task_id, data=update_data)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_delete_task_success(self) -> None:
        account, token = self.create_account_and_get_token()
        created_task = self.create_test_task(
            account_id=account.id, title="Task to Delete", description="This task will be deleted"
        )

        delete_response = self.make_authenticated_request("DELETE", account.id, token, task_id=created_task.id)

        assert delete_response.status_code == 204
        assert delete_response.data == b""

        get_response = self.make_authenticated_request("GET", account.id, token, task_id=created_task.id)
        assert get_response.status_code == 404

    def test_delete_task_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        non_existent_task_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("DELETE", account.id, token, task_id=non_existent_task_id)

        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_delete_task_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        fake_task_id = "507f1f77bcf86cd799439011"

        response = self.make_unauthenticated_request("DELETE", account.id, task_id=fake_task_id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_tasks_are_account_isolated_via_api(self) -> None:
        account1, token1 = self.create_account_and_get_token("user1@example.com", "password1")
        account2, token2 = self.create_account_and_get_token("user2@example.com", "password2")

        task_data = {"title": "Account 1 Task", "description": "This belongs to account 1"}
        create_response = self.make_authenticated_request("POST", account1.id, token1, data=task_data)
        account1_task_id = create_response.json.get("id")

        get_response = self.make_cross_account_request("GET", account1.id, token2, task_id=account1_task_id)
        patch_response = self.make_cross_account_request(
            "PATCH", account1.id, token2, task_id=account1_task_id, data={"title": "Hacked", "description": "Hacked"}
        )
        delete_response = self.make_cross_account_request("DELETE", account1.id, token2, task_id=account1_task_id)

        self.assert_error_response(get_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)
        self.assert_error_response(patch_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)
        self.assert_error_response(delete_response, 401, AccessTokenErrorCode.UNAUTHORIZED_ACCESS)

        verify_response = self.make_authenticated_request("GET", account1.id, token1, task_id=account1_task_id)
        assert verify_response.status_code == 200
        assert verify_response.json.get("id") == account1_task_id

    def test_invalid_json_request_body(self) -> None:
        account, token = self.create_account_and_get_token()
        invalid_json_data = "invalid json"

        with app.test_client() as client:
            response = client.post(
                self.get_task_api_url(account.id),
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=invalid_json_data,
            )

        assert response.status_code == 400
