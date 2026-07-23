import unittest
from datetime import UTC, datetime

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams
from tests.conftest import TEST_ACTOR


class TestRepositoryTimestamps(unittest.TestCase):
    def setUp(self) -> None:
        self.account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="timestamps@example.com",
                password="testpassword",
                first_name="Time",
                last_name="Stamps",
            )
        )

    def tearDown(self) -> None:
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def test_update_stamps_updated_at_without_caller_supplying_it(self) -> None:
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"),
            actor=TEST_ACTOR,
        )

        before = datetime.now(UTC)
        updated = TaskRepository.update(task.id, {"title": "New title"}, actor=TEST_ACTOR)
        after = datetime.now(UTC)

        assert updated is not None
        assert updated.title == "New title"
        assert updated.updated_at is not None
        assert updated.updated_at.tzinfo is not None
        before_ms = before.replace(microsecond=(before.microsecond // 1000) * 1000)
        assert before_ms <= updated.updated_at <= after

    def test_caller_supplied_updated_at_wins(self) -> None:
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"),
            actor=TEST_ACTOR,
        )
        pinned = datetime(2020, 1, 1, tzinfo=UTC)

        updated = TaskRepository.update(task.id, {"active": False, "updated_at": pinned}, actor=TEST_ACTOR)

        assert updated is not None
        assert updated.updated_at == pinned

    def test_empty_update_leaves_updated_at_untouched(self) -> None:
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"),
            actor=TEST_ACTOR,
        )
        stored = TaskRepository.find(task.id)
        assert stored is not None

        unchanged = TaskRepository.update(task.id, {}, actor=TEST_ACTOR)

        assert unchanged is not None
        assert unchanged.updated_at == stored.updated_at

    def test_empty_update_on_missing_entity_returns_none(self) -> None:
        missing = TaskRepository.update("507f1f77bcf86cd799439011", {}, actor=TEST_ACTOR)

        assert missing is None
