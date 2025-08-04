import json
from typing import Optional
from server import app
from modules.task.comments.internal.store.comment_repository import CommentRepository
from modules.task.comments.comment_service import CommentService
from modules.task.comments.types import Comment, CreateCommentParams
from tests.modules.task.base_test_task import BaseTestTask


class BaseTestComment(BaseTestTask):
    """
    Base test class for comment operations with helper methods and setup

    Responsibility:
    - extends BaseTestTask
    - Addd comment-specific helper methods and utilities
    - database cleanup in teardown

    """
    
    DEFAULT_COMMENT_CONTENT = "[TEST] Hey, this is a test comment"
    UPDATED_COMMENT_CONTENT = "[TEST] This is an updated comment"
    LONG_COMMENT_CONTENT = "[TEST] " * 500

    def tearDown(self) -> None:
       CommentRepository.collection().delete_many({})
       super().tearDown()

   # helper methods
    def get_comment_api_url(self, account_id: str, task_id: str) -> str:
        """
        Generate URL for comment collection operations
        """
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments"

    def get_comment_by_id_api_url(self, account_id: str, task_id: str, comment_id: str) -> str:
        """
        Generate URL for comment retrieval by id
        """
        return f"http://127.0.0.1:8080/api/accounts/{account_id}/tasks/{task_id}/comments/{comment_id}"

    def create_test_comment(
        self,
        account_id: str,
        task_id: str,
        content: str = None
    ) -> Comment:
        """
        Create a test comment with default content
        """
        if content is None:
            content = self.DEFAULT_COMMENT_CONTENT

        return CommentService.create_comment(
            params=CreateCommentParams(
                account_id=account_id,
                task_id=task_id,
                content=content or self.DEFAULT_COMMENT_CONTENT
            )
        )
    
    def create_multiple_test_comments(
        self,
        account_id: str,
        task_id: str,
        count: int
    ) -> list[Comment]:
        """
        Create multiple test comments with default content
        """
        comments = []
        for i in range(count):
            comment = self.create_test_comment(
                account_id=account_id,
                task_id=task_id,
                content=f"Test comment {i+1} content"
            )
            comments.append(comment)
        return comments

    def create_comment_with_task_and_account(
        self, 
        content: str = None
    ) -> tuple[Comment, str, str]:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment = self.create_test_comment(
            account_id=account.id,
            task_id=task.id,
            content=content
        )
        return comment, task.id, account.id


    # REST API helper methods
    def make_authenticated_request(
        self, method: str, account_id: str, token: str, task_id: str, data: dict = None, comment_id: str = None
    ):
        """
        Make authenticated HTTP request to comment endpoints
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            account_id: Account ID for the request
            token: Authentication token
            task_id: Task ID that the comment belongs to
            data: Request payload for POST/PUT requests
            comment_id: Comment ID for specific comment operations
        """
        if comment_id:
            url = self.get_comment_by_id_api_url(account_id, task_id, comment_id)
        else:
            url = self.get_comment_api_url(account_id, task_id)

        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers={"Authorization": f"Bearer {token}"})
            elif method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "PUT":
                return client.put(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers={"Authorization": f"Bearer {token}"})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

    def assert_comment_response(
        self, 
        response_json: dict, 
        account_id: str, 
        task_id: str, 
        content: str,
        comment_id: str = None
    ) -> None:
        """
        Assert that the comment response contains expected fields and values
        
        Args:
            response_json: The JSON response from the API
            account_id: Expected account ID
            task_id: Expected task ID  
            content: Expected comment content
            comment_id: Expected comment ID (optional for creation responses)
        """
        assert "id" in response_json, "Comment response should contain 'id' field"
        assert "account_id" in response_json, "Comment response should contain 'account_id' field"
        assert "task_id" in response_json, "Comment response should contain 'task_id' field"
        assert "content" in response_json, "Comment response should contain 'content' field"
        assert "created_at" in response_json, "Comment response should contain 'created_at' field"
        assert "updated_at" in response_json, "Comment response should contain 'updated_at' field"
        
        assert response_json["account_id"] == account_id, f"Expected account_id {account_id}, got {response_json['account_id']}"
        assert response_json["task_id"] == task_id, f"Expected task_id {task_id}, got {response_json['task_id']}"
        assert response_json["content"] == content, f"Expected content '{content}', got '{response_json['content']}'"
        
        if comment_id:
            assert response_json["id"] == comment_id, f"Expected comment_id {comment_id}, got {response_json['id']}"
