import json

from server import app
from modules.authentication.types import AccessTokenErrorCode
from modules.task.types import TaskErrorCode
from tests.modules.task.base_test_task import BaseTestTask


class TestTaskCommentApi(BaseTestTask):
    def get_comment_api_url(self, account_id: str, task_id: str) -> str:
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments"

    def get_comment_by_id_api_url(self, account_id: str, task_id: str, comment_id: str) -> str:
        return f"{self.get_comment_api_url(account_id, task_id)}/{comment_id}"

    def make_authenticated_comment_request(
        self,
        method: str,
        account_id: str,
        task_id: str,
        token: str,
        comment_id: str | None = None,
        data: dict | None = None,
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(account_id, task_id)
        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}
        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers={"Authorization": f"Bearer {token}"})
            elif method.upper() == "POST":
                return client.post(
                    url,
                    headers=headers,
                    data=json.dumps(data) if data is not None else None,
                )
            elif method.upper() == "PATCH":
                return client.patch(
                    url,
                    headers=headers,
                    data=json.dumps(data) if data is not None else None,
                )
            elif method.upper() == "DELETE":
                return client.delete(url, headers={"Authorization": f"Bearer {token}"})

    def make_unauthenticated_comment_request(
        self,
        method: str,
        account_id: str,
        task_id: str,
        comment_id: str | None = None,
        data: dict | None = None,
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(account_id, task_id)
        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url)
            elif method.upper() == "POST":
                return client.post(
                    url,
                    headers=self.HEADERS,
                    data=json.dumps(data) if data is not None else None,
                )
            elif method.upper() == "PATCH":
                return client.patch(
                    url,
                    headers=self.HEADERS,
                    data=json.dumps(data) if data is not None else None,
                )
            elif method.upper() == "DELETE":
                return client.delete(url)

    def make_cross_account_comment_request(
        self,
        method: str,
        target_account_id: str,
        task_id: str,
        auth_token: str,
        comment_id: str | None = None,
        data: dict | None = None,
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
                return client.post(
                    url,
                    headers=headers,
                    data=json.dumps(data) if data is not None else None,
                )
            elif method.upper() == "PATCH":
                return client.patch(
                    url,
                    headers=headers,
                    data=json.dumps(data) if data is not None else None,
                )
            elif method.upper() == "DELETE":
                return client.delete(
                    url,
                    headers={"Authorization": f"Bearer {auth_token}"},
                )

    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        data = {"text": "First comment"}
        response = self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            token,
            data=data,
        )
        assert response.status_code == 201
        assert response.json is not None
        assert response.json.get("id") is not None
        assert response.json.get("task_id") == task.id
        assert response.json.get("account_id") == account.id
        assert response.json.get("text") == "First comment"

    def test_create_comment_missing_text(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        data = {}
        response = self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            token,
            data=data,
        )
        self.assert_error_response(response, 400, TaskErrorCode.BAD_REQUEST)
        assert "Text is required" in response.json.get("message")

    def test_create_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        data = {"text": "No auth"}
        response = self.make_unauthenticated_comment_request(
            "POST",
            account.id,
            task.id,
            data=data,
        )
        self.assert_error_response(
            response,
            401,
            AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND,
        )

    def test_create_comment_invalid_token(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        data = {"text": "Invalid token"}
        response = self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            "invalid_token",
            data=data,
        )
        self.assert_error_response(
            response,
            401,
            AccessTokenErrorCode.ACCESS_TOKEN_INVALID,
        )

    def test_get_comments_empty(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        response = self.make_authenticated_comment_request(
            "GET",
            account.id,
            task.id,
            token,
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("items") == []
        assert response.json.get("total_count") == 0

    def test_get_comments_with_items(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        data1 = {"text": "Comment 1"}
        data2 = {"text": "Comment 2"}
        self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            token,
            data=data1,
        )
        self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            token,
            data=data2,
        )
        response = self.make_authenticated_comment_request(
            "GET",
            account.id,
            task.id,
            token,
        )
        assert response.status_code == 200
        assert response.json is not None
        items = response.json.get("items")
        assert len(items) == 2
        texts = {item["text"] for item in items}
        assert "Comment 1" in texts
        assert "Comment 2" in texts
        assert response.json.get("total_count") == 2

    def test_get_single_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        data = {"text": "Single comment"}
        create_response = self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            token,
            data=data,
        )
        comment_id = create_response.json.get("id")
        response = self.make_authenticated_comment_request(
            "GET",
            account.id,
            task.id,
            token,
            comment_id=comment_id,
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json.get("id") == comment_id
        assert response.json.get("text") == "Single comment"

    def test_get_single_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        response = self.make_authenticated_comment_request(
            "GET",
            account.id,
            task.id,
            token,
            comment_id="nonexistent",
        )
        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        create_response = self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            token,
            data={"text": "Old text"},
        )
        comment_id = create_response.json.get("id")
        update_response = self.make_authenticated_comment_request(
            "PATCH",
            account.id,
            task.id,
            token,
            comment_id=comment_id,
            data={"text": "Updated text"},
        )
        assert update_response.status_code == 200
        assert update_response.json is not None
        assert update_response.json.get("id") == comment_id
        assert update_response.json.get("text") == "Updated text"

    def test_update_comment_missing_text(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        create_response = self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            token,
            data={"text": "Old text"},
        )
        comment_id = create_response.json.get("id")
        response = self.make_authenticated_comment_request(
            "PATCH",
            account.id,
            task.id,
            token,
            comment_id=comment_id,
            data={},
        )
        self.assert_error_response(response, 400, TaskErrorCode.BAD_REQUEST)
        assert "Text is required" in response.json.get("message")

    def test_update_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        response = self.make_authenticated_comment_request(
            "PATCH",
            account.id,
            task.id,
            token,
            comment_id="nonexistent",
            data={"text": "Updated text"},
        )
        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        create_response = self.make_authenticated_comment_request(
            "POST",
            account.id,
            task.id,
            token,
            data={"text": "To delete"},
        )
        comment_id = create_response.json.get("id")
        delete_response = self.make_authenticated_comment_request(
            "DELETE",
            account.id,
            task.id,
            token,
            comment_id=comment_id,
        )
        assert delete_response.status_code == 204
        assert delete_response.data == b""
        list_response = self.make_authenticated_comment_request(
            "GET",
            account.id,
            task.id,
            token,
        )
        assert list_response.status_code == 200
        assert list_response.json.get("total_count") == 0

    def test_delete_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        response = self.make_authenticated_comment_request(
            "DELETE",
            account.id,
            task.id,
            token,
            comment_id="nonexistent",
        )
        self.assert_error_response(response, 404, TaskErrorCode.NOT_FOUND)

    def test_comments_are_account_isolated_via_api(self) -> None:
        account1, token1 = self.create_account_and_get_token(
            "user1@example.com",
            "password1",
        )
        account2, token2 = self.create_account_and_get_token(
            "user2@example.com",
            "password2",
        )
        task = self.create_test_task(account_id=account1.id)
        create_response = self.make_authenticated_comment_request(
            "POST",
            account1.id,
            task.id,
            token1,
            data={"text": "Account 1 comment"},
        )
        comment_id = create_response.json.get("id")
        get_response = self.make_cross_account_comment_request(
            "GET",
            account1.id,
            task.id,
            token2,
            comment_id=comment_id,
        )
        patch_response = self.make_cross_account_comment_request(
            "PATCH",
            account1.id,
            task.id,
            token2,
            comment_id=comment_id,
            data={"text": "Hacked"},
        )
        delete_response = self.make_cross_account_comment_request(
            "DELETE",
            account1.id,
            task.id,
            token2,
            comment_id=comment_id,
        )
        self.assert_error_response(
            get_response,
            401,
            AccessTokenErrorCode.UNAUTHORIZED_ACCESS,
        )
        self.assert_error_response(
            patch_response,
            401,
            AccessTokenErrorCode.UNAUTHORIZED_ACCESS,
        )
        self.assert_error_response(
            delete_response,
            401,
            AccessTokenErrorCode.UNAUTHORIZED_ACCESS,
        )
        verify_response = self.make_authenticated_comment_request(
            "GET",
            account1.id,
            task.id,
            token1,
            comment_id=comment_id,
        )
        assert verify_response.status_code == 200
        assert verify_response.json.get("id") == comment_id
