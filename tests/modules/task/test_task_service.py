from modules.task.types import TaskErrorCode
from tests.modules.task.base_test_task import BaseTestTask, TaskRequestBody


class TestTaskService(BaseTestTask):
    def setUp(self) -> None:
        super().setUp()
        self.account, self.token = self.create_account_and_get_token()

    def test_create_task(self) -> None:
        task_data: TaskRequestBody = {"title": self.DEFAULT_TASK_TITLE, "description": self.DEFAULT_TASK_DESCRIPTION}

        response = self.make_authenticated_request("POST", self.account.id, self.token, data=task_data)

        assert response.status_code == 201
        assert response.json is not None
        assert response.json.get("id") is not None
        assert response.json.get("account_id") == self.account.id
        assert response.json.get("title") == self.DEFAULT_TASK_TITLE
        assert response.json.get("description") == self.DEFAULT_TASK_DESCRIPTION

    def test_get_task_for_account(self) -> None:
        created_task = self.create_test_task(account_id=self.account.id)

        response = self.make_authenticated_request("GET", self.account.id, self.token, task_id=created_task.id)

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == created_task.id
        assert response.json.get("account_id") == self.account.id
        assert response.json.get("title") == self.DEFAULT_TASK_TITLE
        assert response.json.get("description") == self.DEFAULT_TASK_DESCRIPTION

    def test_get_task_for_account_not_found(self) -> None:
        non_existent_task_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("GET", self.account.id, self.token, task_id=non_existent_task_id)

        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_get_paginated_tasks_empty(self) -> None:
        response = self.make_authenticated_request("GET", self.account.id, self.token, query_params="page=1&size=10")

        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json["items"]) == 0
        assert response.json["total_count"] == 0
        assert response.json["pagination_params"]["page"] == 1
        assert response.json["pagination_params"]["size"] == 10

    def test_get_paginated_tasks_with_data(self) -> None:
        self.create_multiple_test_tasks(account_id=self.account.id, count=5)

        page_one = self.make_authenticated_request("GET", self.account.id, self.token, query_params="page=1&size=3")
        assert page_one.status_code == 200
        assert page_one.json is not None
        assert len(page_one.json["items"]) == 3
        assert page_one.json["total_count"] == 5
        assert page_one.json["pagination_params"]["page"] == 1
        assert page_one.json["pagination_params"]["size"] == 3

        page_two = self.make_authenticated_request("GET", self.account.id, self.token, query_params="page=2&size=3")
        assert page_two.status_code == 200
        assert page_two.json is not None
        assert len(page_two.json["items"]) == 2
        assert page_two.json["total_count"] == 5

    def test_get_paginated_tasks_default_pagination(self) -> None:
        self.create_test_task(account_id=self.account.id)

        response = self.make_authenticated_request("GET", self.account.id, self.token, query_params="page=1&size=1")

        assert response.status_code == 200
        assert response.json is not None
        assert len(response.json["items"]) == 1
        assert response.json["total_count"] == 1
        assert response.json["pagination_params"]["page"] == 1
        assert response.json["pagination_params"]["size"] == 1

    def test_update_task(self) -> None:
        created_task = self.create_test_task(
            account_id=self.account.id, title="Original Title", description="Original Description"
        )
        update_data: TaskRequestBody = {"title": "Updated Title", "description": "Updated Description"}

        response = self.make_authenticated_request(
            "PATCH", self.account.id, self.token, task_id=created_task.id, data=update_data
        )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == created_task.id
        assert response.json.get("account_id") == self.account.id
        assert response.json.get("title") == "Updated Title"
        assert response.json.get("description") == "Updated Description"

    def test_update_task_not_found(self) -> None:
        non_existent_task_id = "507f1f77bcf86cd799439011"
        update_data: TaskRequestBody = {"title": "Updated Title", "description": "Updated Description"}

        response = self.make_authenticated_request(
            "PATCH", self.account.id, self.token, task_id=non_existent_task_id, data=update_data
        )

        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_delete_task(self) -> None:
        created_task = self.create_test_task(account_id=self.account.id)

        delete_response = self.make_authenticated_request(
            "DELETE", self.account.id, self.token, task_id=created_task.id
        )

        assert delete_response.status_code == 204
        assert delete_response.data == b""

        get_response = self.make_authenticated_request("GET", self.account.id, self.token, task_id=created_task.id)
        self.assert_error_response(get_response, 404, TaskErrorCode.NOT_FOUND)

    def test_delete_task_not_found(self) -> None:
        non_existent_task_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request("DELETE", self.account.id, self.token, task_id=non_existent_task_id)

        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_update_task_belonging_to_another_account_is_not_found_and_leaves_it_unchanged(self) -> None:
        other_account, other_token = self.create_account_and_get_token(username="otheruser@example.com")
        victim_task = self.create_test_task(
            account_id=other_account.id, title="Owner Title", description="Owner Description"
        )
        update_data: TaskRequestBody = {"title": "Hijacked", "description": "Hijacked"}

        response = self.make_cross_account_request(
            "PATCH", other_account.id, self.token, task_id=victim_task.id, data=update_data
        )

        assert response.status_code == 401

        unchanged = self.make_authenticated_request("GET", other_account.id, other_token, task_id=victim_task.id)
        assert unchanged.status_code == 200
        assert unchanged.json is not None
        assert unchanged.json.get("title") == "Owner Title"
        assert unchanged.json.get("description") == "Owner Description"

    def test_delete_task_belonging_to_another_account_is_not_found_and_leaves_it_intact(self) -> None:
        other_account, other_token = self.create_account_and_get_token(username="otheruser@example.com")
        victim_task = self.create_test_task(account_id=other_account.id)

        response = self.make_cross_account_request("DELETE", other_account.id, self.token, task_id=victim_task.id)

        assert response.status_code == 401

        still_there = self.make_authenticated_request("GET", other_account.id, other_token, task_id=victim_task.id)
        assert still_there.status_code == 200
        assert still_there.json is not None
        assert still_there.json.get("id") == victim_task.id

    def test_task_isolation_between_accounts(self) -> None:
        other_account, other_token = self.create_account_and_get_token(username="otheruser@example.com")

        account1_task = self.create_test_task(
            account_id=self.account.id, title="Account 1 Task", description="Task for account 1"
        )
        account2_task = self.create_test_task(
            account_id=other_account.id, title="Account 2 Task", description="Task for account 2"
        )

        account1_list = self.make_authenticated_request("GET", self.account.id, self.token)
        assert account1_list.json is not None
        assert len(account1_list.json["items"]) == 1
        assert account1_list.json["items"][0]["id"] == account1_task.id

        account2_list = self.make_authenticated_request("GET", other_account.id, other_token)
        assert account2_list.json is not None
        assert len(account2_list.json["items"]) == 1
        assert account2_list.json["items"][0]["id"] == account2_task.id

        cross_read = self.make_cross_account_request("GET", other_account.id, self.token, task_id=account2_task.id)
        assert cross_read.status_code == 401
