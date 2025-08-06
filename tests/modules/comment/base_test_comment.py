import unittest

from server import app

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams


class BaseTestComment(unittest.TestCase):
    HEADERS = {"Content-Type": "application/json"}
    DEFAULT_USERNAME = "testuser@example.com"
    DEFAULT_PASSWORD = "testpassword"
    DEFAULT_FIRST_NAME = "Test"
    DEFAULT_LAST_NAME = "User"
    DEFAULT_TASK_TITLE = "Test Task"
    DEFAULT_TASK_DESCRIPTION = "Test Description"

    def setUp(self) -> None:
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def tearDown(self) -> None:
        CommentRepository.collection().delete_many({})
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def create_test_account(self):
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username=self.DEFAULT_USERNAME,
                password=self.DEFAULT_PASSWORD,
                first_name=self.DEFAULT_FIRST_NAME,
                last_name=self.DEFAULT_LAST_NAME,
            )
        )

    def create_test_task(self, account_id: str):
        return TaskService.create_task(
            params=CreateTaskParams(
                account_id=account_id, title=self.DEFAULT_TASK_TITLE, description=self.DEFAULT_TASK_DESCRIPTION
            )
        )

    def get_access_token(self):
        with app.test_client() as client:
            response = client.post(
                "/api/access-tokens",
                headers=self.HEADERS,
                json={"username": self.DEFAULT_USERNAME, "password": self.DEFAULT_PASSWORD},
            )
            return response.json.get("token")
