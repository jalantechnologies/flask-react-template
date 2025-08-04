from server import app
from modules.authentication.types import AccessTokenErrorCode
from modules.task.comments.types import CommentErrorCode
from tests.modules.task.comments.base_test_comment import BaseTestComment

class TestCommentsApi(BaseTestComment):
    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_authenticated_request("POST", account.id, token, task.id, data=comment_data)

        assert response.status_code == 200
        assert response.json is not None
        self.assert_comment_response(response.json, account_id=account.id, task_id=task.id, content=self.DEFAULT_COMMENT_CONTENT)