from modules.comment.types import CommentErrorCode
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):
    def setUp(self) -> None:
        super().setUp()
        self.account, self.token = self.create_account_and_get_token()
        self.task = self.create_test_task(account_id=self.account.id)

    def test_create_comment_success(self) -> None:
        data = {"content": "This is a test comment"}

        response = self.make_authenticated_request("POST", self.account.id, self.task.id, self.token, data=data)

        assert response.status_code == 201
        self.assert_comment_response(
            response.json, account_id=self.account.id, task_id=self.task.id, content="This is a test comment"
        )

    def test_create_comment_missing_content(self) -> None:
        data = {}

        response = self.make_authenticated_request("POST", self.account.id, self.task.id, self.token, data=data)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_create_comment_empty_content(self) -> None:
        data = {"content": ""}

        response = self.make_authenticated_request("POST", self.account.id, self.task.id, self.token, data=data)

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_create_comment_nonexistent_task(self) -> None:
        data = {"content": "This is a test comment"}
        nonexistent_task_id = "64f123456789abcdef123456"

        response = self.make_authenticated_request("POST", self.account.id, nonexistent_task_id, self.token, data=data)

        self.assert_error_response(response, 404, CommentErrorCode.TASK_NOT_FOUND)

    def test_create_comment_unauthenticated(self) -> None:
        data = {"content": "This is a test comment"}

        response = self.make_unauthenticated_request("POST", self.account.id, self.task.id, data=data)

        assert response.status_code == 401

    def test_get_comment_success(self) -> None:
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        response = self.make_authenticated_request(
            "GET", self.account.id, self.task.id, self.token, comment_id=comment.id
        )

        assert response.status_code == 200
        self.assert_comment_response(response.json, expected_comment=comment)

    def test_get_comment_nonexistent_comment(self) -> None:
        nonexistent_comment_id = "64f123456789abcdef123456"

        response = self.make_authenticated_request(
            "GET", self.account.id, self.task.id, self.token, comment_id=nonexistent_comment_id
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_get_comment_nonexistent_task(self) -> None:
        nonexistent_task_id = "64f123456789abcdef123456"
        nonexistent_comment_id = "64f123456789abcdef123456"

        response = self.make_authenticated_request(
            "GET", self.account.id, nonexistent_task_id, self.token, comment_id=nonexistent_comment_id
        )

        self.assert_error_response(response, 404, CommentErrorCode.TASK_NOT_FOUND)

    def test_get_comment_unauthenticated(self) -> None:
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        response = self.make_unauthenticated_request("GET", self.account.id, self.task.id, comment_id=comment.id)

        assert response.status_code == 401

    def test_get_paginated_comments_success(self) -> None:
        self.create_multiple_test_comments(account_id=self.account.id, task_id=self.task.id, count=5)

        response = self.make_authenticated_request(
            "GET", self.account.id, self.task.id, self.token, query_params="page=1&size=3"
        )

        assert response.status_code == 200
        self.assert_pagination_response(
            response.json, expected_items_count=3, expected_total_count=5, expected_page=1, expected_size=3
        )

        for item in response.json["items"]:
            self.assert_comment_response(item, account_id=self.account.id, task_id=self.task.id)

    def test_get_paginated_comments_empty_results(self) -> None:
        response = self.make_authenticated_request(
            "GET", self.account.id, self.task.id, self.token, query_params="page=1&size=10"
        )

        assert response.status_code == 200
        self.assert_pagination_response(
            response.json, expected_items_count=0, expected_total_count=0, expected_page=1, expected_size=10
        )

    def test_get_paginated_comments_default_pagination(self) -> None:
        comments = self.create_multiple_test_comments(account_id=self.account.id, task_id=self.task.id, count=3)

        response = self.make_authenticated_request("GET", self.account.id, self.task.id, self.token)

        assert response.status_code == 200
        assert "pagination_params" in response.json
        assert len(response.json["items"]) == 3

    def test_get_paginated_comments_invalid_page(self) -> None:
        response = self.make_authenticated_request(
            "GET", self.account.id, self.task.id, self.token, query_params="page=0"
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_get_paginated_comments_invalid_size(self) -> None:
        response = self.make_authenticated_request(
            "GET", self.account.id, self.task.id, self.token, query_params="size=0"
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_get_paginated_comments_nonexistent_task(self) -> None:
        nonexistent_task_id = "64f123456789abcdef123456"

        response = self.make_authenticated_request(
            "GET", self.account.id, nonexistent_task_id, self.token, query_params="page=1&size=10"
        )

        self.assert_error_response(response, 404, CommentErrorCode.TASK_NOT_FOUND)

    def test_comment_ordering_by_created_at(self) -> None:
        self.create_multiple_test_comments(account_id=self.account.id, task_id=self.task.id, count=3)

        response = self.make_authenticated_request("GET", self.account.id, self.task.id, self.token)

        assert response.status_code == 200
        items = response.json["items"]

        for i in range(len(items) - 1):
            current_created_at = items[i]["created_at"]
            next_created_at = items[i + 1]["created_at"]
            assert current_created_at >= next_created_at, "Comments should be ordered by created_at descending"

    def test_update_comment_success(self) -> None:
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)
        data = {"content": "Updated comment content"}

        response = self.make_authenticated_request(
            "PATCH", self.account.id, self.task.id, self.token, comment_id=comment.id, data=data
        )

        assert response.status_code == 200
        self.assert_comment_response(
            response.json, account_id=self.account.id, task_id=self.task.id, content="Updated comment content"
        )

    def test_update_comment_missing_content(self) -> None:
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)
        data = {}

        response = self.make_authenticated_request(
            "PATCH", self.account.id, self.task.id, self.token, comment_id=comment.id, data=data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_update_comment_empty_content(self) -> None:
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)
        data = {"content": ""}

        response = self.make_authenticated_request(
            "PATCH", self.account.id, self.task.id, self.token, comment_id=comment.id, data=data
        )

        self.assert_error_response(response, 400, CommentErrorCode.BAD_REQUEST)

    def test_update_comment_nonexistent_comment(self) -> None:
        data = {"content": "Updated content"}
        nonexistent_comment_id = "64f123456789abcdef123456"

        response = self.make_authenticated_request(
            "PATCH", self.account.id, self.task.id, self.token, comment_id=nonexistent_comment_id, data=data
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_update_comment_nonexistent_task(self) -> None:
        data = {"content": "Updated content"}
        nonexistent_task_id = "64f123456789abcdef123456"
        nonexistent_comment_id = "64f123456789abcdef123456"

        response = self.make_authenticated_request(
            "PATCH", self.account.id, nonexistent_task_id, self.token, comment_id=nonexistent_comment_id, data=data
        )

        self.assert_error_response(response, 404, CommentErrorCode.TASK_NOT_FOUND)

    def test_update_comment_unauthenticated(self) -> None:
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)
        data = {"content": "Updated content"}

        response = self.make_unauthenticated_request(
            "PATCH", self.account.id, self.task.id, comment_id=comment.id, data=data
        )

        assert response.status_code == 401

    def test_delete_comment_success(self) -> None:
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        response = self.make_authenticated_request(
            "DELETE", self.account.id, self.task.id, self.token, comment_id=comment.id
        )

        assert response.status_code == 204

        get_response = self.make_authenticated_request(
            "GET", self.account.id, self.task.id, self.token, comment_id=comment.id
        )
        self.assert_error_response(get_response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_nonexistent_comment(self) -> None:
        nonexistent_comment_id = "64f123456789abcdef123456"

        response = self.make_authenticated_request(
            "DELETE", self.account.id, self.task.id, self.token, comment_id=nonexistent_comment_id
        )

        self.assert_error_response(response, 404, CommentErrorCode.NOT_FOUND)

    def test_delete_comment_nonexistent_task(self) -> None:
        nonexistent_task_id = "64f123456789abcdef123456"
        nonexistent_comment_id = "64f123456789abcdef123456"

        response = self.make_authenticated_request(
            "DELETE", self.account.id, nonexistent_task_id, self.token, comment_id=nonexistent_comment_id
        )

        self.assert_error_response(response, 404, CommentErrorCode.TASK_NOT_FOUND)

    def test_delete_comment_unauthenticated(self) -> None:
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        response = self.make_unauthenticated_request("DELETE", self.account.id, self.task.id, comment_id=comment.id)

        assert response.status_code == 401

    def test_cross_account_comment_operations_denied(self) -> None:
        other_account, other_token = self.create_account_and_get_token(username="other@example.com")
        comment = self.create_test_comment(account_id=self.account.id, task_id=self.task.id)

        get_response = self.make_cross_account_request(
            "GET", self.account.id, self.task.id, other_token, comment_id=comment.id
        )
        assert get_response.status_code == 401

        update_data = {"content": "Unauthorized update"}
        update_response = self.make_cross_account_request(
            "PATCH", self.account.id, self.task.id, other_token, comment_id=comment.id, data=update_data
        )
        assert update_response.status_code == 401

        delete_response = self.make_cross_account_request(
            "DELETE", self.account.id, self.task.id, other_token, comment_id=comment.id
        )
        assert delete_response.status_code == 401

