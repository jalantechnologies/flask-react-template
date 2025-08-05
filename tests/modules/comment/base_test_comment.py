from datetime import datetime
from typing import List

from bson import ObjectId

from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.task.internal.store.task_model import TaskModel
from modules.task.internal.store.task_repository import TaskRepository
from tests.modules.account.base_test_account import BaseTestAccount


class BaseTestComment(BaseTestAccount):
    DEFAULT_COMMENT_CONTENT = "This is a test comment"
    DEFAULT_COMMENT_CONTENT_2 = "This is another test comment"

    def create_test_task(self, *, account_id: str, title: str = "Test Task", description: str = "Test Description") -> TaskModel:
        task_model = TaskModel(
            account_id=account_id,
            title=title,
            description=description,
        )
        return TaskRepository.create_task(task_model=task_model)

    def create_test_comment(
        self, *, task_id: str, account_id: str, content: str = DEFAULT_COMMENT_CONTENT
    ) -> CommentModel:
        comment_model = CommentModel(
            task_id=task_id,
            account_id=account_id,
            content=content,
        )
        return CommentRepository.create_comment(comment_model=comment_model)

    def create_multiple_test_comments(
        self, *, task_id: str, account_id: str, count: int
    ) -> List[CommentModel]:
        comments = []
        for i in range(1, count + 1):
            comment = self.create_test_comment(
                task_id=task_id,
                account_id=account_id,
                content=f"Comment {i}",
            )
            comments.append(comment)
        return comments

    def assert_comment_response(
        self,
        response_data: dict,
        *,
        content: str,
        task_id: str,
        account_id: str,
        comment_id: str = None,
    ) -> None:
        assert "id" in response_data
        assert "task_id" in response_data
        assert "account_id" in response_data
        assert "content" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data

        if comment_id:
            assert response_data["id"] == comment_id
        else:
            assert response_data["id"] is not None

        assert response_data["task_id"] == task_id
        assert response_data["account_id"] == account_id
        assert response_data["content"] == content

        # Verify datetime fields are valid
        datetime.fromisoformat(response_data["created_at"].replace("Z", "+00:00"))
        datetime.fromisoformat(response_data["updated_at"].replace("Z", "+00:00"))

    def make_comment_request(
        self, method: str, account_id: str, task_id: str, token: str = None, comment_id: str = None, data: dict = None, query_params: str = None
    ):
        url = f"/api/accounts/{account_id}/tasks/{task_id}/comments"
        if comment_id:
            url += f"/{comment_id}"

        if query_params:
            url += f"?{query_params}"

        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return self.client.open(
            url,
            method=method,
            json=data,
            headers=headers,
        )

    def make_authenticated_comment_request(
        self, method: str, account_id: str, task_id: str, token: str, comment_id: str = None, data: dict = None, query_params: str = None
    ):
        return self.make_comment_request(method, account_id, task_id, token, comment_id, data, query_params)

    def make_unauthenticated_comment_request(
        self, method: str, account_id: str, task_id: str, comment_id: str = None, data: dict = None, query_params: str = None
    ):
        return self.make_comment_request(method, account_id, task_id, None, comment_id, data, query_params) 