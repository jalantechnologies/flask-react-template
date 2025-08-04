import json

from server import app

from modules.comments.comment_service import CommentService
from modules.comments.internal.store.comment_repository import CommentRepository
from modules.comments.rest_api.comment_rest_api_server import CommentRestApiServer
from modules.comments.types import Comment, CreateCommentParams
from modules.logger.logger_manager import LoggerManager
from tests.modules.task.base_test_task import BaseTestTask


class BaseTestComment(BaseTestTask):
    DEFAULT_COMMENT_CONTENT = "Test comment"

    def setUp(self) -> None:
        LoggerManager.mount_logger()
        CommentRestApiServer.create()

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        super().tearDown()

    def get_comments_api_url(self, account_id: str, task_id: str) -> str:
        return f"{self.get_task_by_id_api_url(account_id, task_id)}/comments"

    def get_comment_by_id_api_url(self, account_id: str, task_id: str, comment_id: str) -> str:
        return f"{self.get_comments_api_url(account_id, task_id)}/{comment_id}"

    def create_test_comment(self, account_id: str, task_id: str, content: str = None) -> Comment:
        return CommentService.create_comment(
            params=CreateCommentParams(
                account_id=account_id, task_id=task_id, content=content or self.DEFAULT_COMMENT_CONTENT
            )
        )

    def create_multiple_test_comments(self, account_id: str, task_id: str, count: int) -> list[Comment]:
        comments: list[Comment] = []
        for i in range(count):
            comments.append(self.create_test_comment(account_id=account_id, task_id=task_id, content=f"Comment {i+1}"))
        return comments

    def make_authenticated_comment_request(
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
            url = self.get_comments_api_url(account_id, task_id)
        if query_params:
            url += f"?{query_params}"
        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}
        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers={"Authorization": f"Bearer {token}"})
            if method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data is not None else None)
            if method.upper() == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data is not None else None)
            if method.upper() == "DELETE":
                return client.delete(url, headers={"Authorization": f"Bearer {token}"})

    def make_unauthenticated_comment_request(
        self, method: str, account_id: str, task_id: str, comment_id: str = None, data: dict = None
    ):
        if comment_id:
            url = self.get_comment_by_id_api_url(account_id, task_id, comment_id)
        else:
            url = self.get_comments_api_url(account_id, task_id)
        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url)
            if method.upper() == "POST":
                return client.post(url, headers=self.HEADERS, data=json.dumps(data) if data is not None else None)
            if method.upper() == "PATCH":
                return client.patch(url, headers=self.HEADERS, data=json.dumps(data) if data is not None else None)
            if method.upper() == "DELETE":
                return client.delete(url)

    def make_cross_account_comment_request(
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
            url = self.get_comments_api_url(target_account_id, task_id)
        headers = {**self.HEADERS, "Authorization": f"Bearer {auth_token}"}
        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers={"Authorization": f"Bearer {auth_token}"})
            if method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data is not None else None)
            if method.upper() == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data) if data is not None else None)
            if method.upper() == "DELETE":
                return client.delete(url, headers={"Authorization": f"Bearer {auth_token}"})

    def assert_comment_response(self, response_json: dict, expected_comment: Comment = None, **expected_fields):
        assert response_json.get("id") is not None
        assert response_json.get("account_id") is not None
        assert response_json.get("task_id") is not None
        if expected_comment:
            assert response_json.get("id") == expected_comment.id
            assert response_json.get("account_id") == expected_comment.account_id
            assert response_json.get("task_id") == expected_comment.task_id
            assert response_json.get("content") == expected_comment.content
        for field, value in expected_fields.items():
            assert response_json.get(field) == value
