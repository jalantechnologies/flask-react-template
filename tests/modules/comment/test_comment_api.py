from modules.comment.types import CommentErrorCode
from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):

    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        
        url = self.get_comment_list_url(account.id, task.id)
        data = {"content": "New Comment"}
        
        response = self.make_authenticated_request("POST", account.id, token, url, data=data)
        
        assert response.status_code == 201
        self.assert_comment_response(
            response.json,
            account_id=account.id,
            task_id=task.id,
            content="New Comment"
        )

    def test_get_comments_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        self.create_test_comment(account.id, task.id, "Comment 1")
        self.create_test_comment(account.id, task.id, "Comment 2")
        
        url = self.get_comment_list_url(account.id, task.id)
        response = self.make_authenticated_request("GET", account.id, token, url)
        
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]["content"] == "Comment 1"
        assert response.json[1]["content"] == "Comment 2"

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(account.id, task.id, "Original")
        
        url = self.get_comment_detail_url(account.id, comment.id)
        data = {"content": "Updated"}
        
        response = self.make_authenticated_request("PATCH", account.id, token, url, data=data)
        
        assert response.status_code == 200
        self.assert_comment_response(response.json, expected_comment=comment, content="Updated")

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account.id)
        comment = self.create_test_comment(account.id, task.id)
        
        url = self.get_comment_detail_url(account.id, comment.id)
        
        response = self.make_authenticated_request("DELETE", account.id, token, url)
        
        assert response.status_code == 204
