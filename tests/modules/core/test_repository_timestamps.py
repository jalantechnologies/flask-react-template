import unittest
from datetime import UTC, datetime, timedelta

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams, UpdateAccountProfileParams
from modules.notification.internal.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.notification_service import NotificationService
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.task_service import TaskService
from modules.task.types import CreateTaskParams, DeleteTaskParams, UpdateTaskParams
from tests.conftest import TEST_ACTOR


class TestRepositoryTimestamps(unittest.TestCase):
    def setUp(self) -> None:
        self.account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username="timestamps@example.com", password="testpassword", first_name="Time", last_name="Stamps"
            ),
            actor=TEST_ACTOR,
        )

    def tearDown(self) -> None:
        TaskRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})
        AccountNotificationPreferencesRepository.collection().delete_many({})

    def test_update_stamps_updated_at_without_caller_supplying_it(self) -> None:
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"), actor=TEST_ACTOR
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
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"), actor=TEST_ACTOR
        )
        pinned = datetime(2020, 1, 1, tzinfo=UTC)

        updated = TaskRepository.update(task.id, {"active": False, "updated_at": pinned}, actor=TEST_ACTOR)

        assert updated is not None
        assert updated.updated_at == pinned

    def test_empty_update_leaves_updated_at_untouched(self) -> None:
        task = TaskService.create_task(
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"), actor=TEST_ACTOR
        )
        stored = TaskRepository.find(task.id, actor=TEST_ACTOR)
        assert stored is not None

        unchanged = TaskRepository.update(task.id, {}, actor=TEST_ACTOR)

        assert unchanged is not None
        assert unchanged.updated_at == stored.updated_at

    def test_empty_update_on_missing_entity_returns_none(self) -> None:
        missing = TaskRepository.update("507f1f77bcf86cd799439011", {}, actor=TEST_ACTOR)

        assert missing is None

    def test_given_task_details_when_creating_task_then_created_at_and_updated_at_reflect_creation_time(self) -> None:
        before = datetime.now(UTC)
        created_task = TaskService.create_task(
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"), actor=TEST_ACTOR
        )
        after = datetime.now(UTC)

        assert created_task.created_at is not None
        assert created_task.updated_at is not None
        assert created_task.created_at.tzinfo is not None
        assert created_task.updated_at.tzinfo is not None
        assert created_task.created_at.utcoffset() == timedelta(0)
        assert created_task.updated_at.utcoffset() == timedelta(0)
        assert created_task.created_at == created_task.updated_at
        assert before <= created_task.created_at <= after
        assert before <= created_task.updated_at <= after

    def test_given_existing_task_when_updating_task_then_updated_at_reflects_update_time(self) -> None:
        created_task = TaskService.create_task(
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"), actor=TEST_ACTOR
        )
        update_params = UpdateTaskParams(
            account_id=self.account.id,
            task_id=created_task.id,
            title="Updated Title",
            description="Updated Description",
        )

        before = datetime.now(UTC)
        updated_task = TaskService.update_task(params=update_params, actor=TEST_ACTOR)
        after = datetime.now(UTC)

        assert updated_task.updated_at is not None
        assert updated_task.created_at is not None
        assert before - timedelta(milliseconds=1) <= updated_task.updated_at <= after
        assert updated_task.updated_at > updated_task.created_at

    def test_given_existing_task_when_deleting_task_then_deleted_at_reflects_deletion_time_in_utc(self) -> None:
        created_task = TaskService.create_task(
            params=CreateTaskParams(account_id=self.account.id, title="Title", description="Body"), actor=TEST_ACTOR
        )
        delete_params = DeleteTaskParams(account_id=self.account.id, task_id=created_task.id)

        before = datetime.now(UTC)
        deletion_result = TaskService.delete_task(params=delete_params, actor=TEST_ACTOR)
        after = datetime.now(UTC)

        assert deletion_result.deleted_at is not None
        assert deletion_result.deleted_at.tzinfo is not None
        assert deletion_result.deleted_at.utcoffset() == timedelta(0)
        assert before <= deletion_result.deleted_at <= after

    def test_given_account_details_when_creating_account_then_created_at_and_updated_at_reflect_creation_time(
        self,
    ) -> None:
        before = datetime.now(UTC)
        created_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="timestamp_username"
            ),
            actor=TEST_ACTOR,
        )
        after = datetime.now(UTC)

        assert created_account.created_at is not None
        assert created_account.updated_at is not None
        assert created_account.created_at.tzinfo is not None
        assert created_account.updated_at.tzinfo is not None
        assert created_account.created_at.utcoffset() == timedelta(0)
        assert created_account.updated_at.utcoffset() == timedelta(0)
        assert created_account.created_at == created_account.updated_at
        assert before <= created_account.created_at <= after
        assert before <= created_account.updated_at <= after

    def test_given_existing_account_when_updating_profile_then_updated_at_reflects_update_time(self) -> None:
        before = datetime.now(UTC)
        updated_account = AccountService.update_account_profile(
            account_id=self.account.id,
            actor=TEST_ACTOR,
            params=UpdateAccountProfileParams(first_name="updated_first_name"),
        )
        after = datetime.now(UTC)

        assert updated_account.updated_at is not None
        assert updated_account.created_at is not None
        assert before - timedelta(milliseconds=1) <= updated_account.updated_at <= after
        assert updated_account.updated_at > updated_account.created_at

    def test_given_existing_account_when_deleting_account_then_deleted_at_reflects_deletion_time_in_utc(self) -> None:
        before = datetime.now(UTC)
        deletion_result = AccountService.delete_account(account_id=self.account.id, actor=TEST_ACTOR)
        after = datetime.now(UTC)

        assert deletion_result.deleted_at is not None
        assert deletion_result.deleted_at.tzinfo is not None
        assert deletion_result.deleted_at.utcoffset() == timedelta(0)
        assert before <= deletion_result.deleted_at <= after

    def test_given_account_details_when_creating_account_then_notification_preferences_timestamps_reflect_creation_time(
        self,
    ) -> None:
        before = datetime.now(UTC)
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="prefs_timestamp_username"
            ),
            actor=TEST_ACTOR,
        )
        after = datetime.now(UTC)

        preferences = NotificationService.get_account_notification_preferences_by_account_id(
            account_id=account.id, actor=TEST_ACTOR
        )

        assert preferences.created_at is not None
        assert preferences.updated_at is not None
        assert preferences.created_at.utcoffset() == timedelta(0)
        assert preferences.updated_at.utcoffset() == timedelta(0)
        assert preferences.created_at == preferences.updated_at
        assert before - timedelta(milliseconds=1) <= preferences.created_at <= after
        assert before - timedelta(milliseconds=1) <= preferences.updated_at <= after

    def test_given_existing_notification_preferences_when_updating_then_updated_at_reflects_update_time(self) -> None:
        update_preferences = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=False, push_enabled=True, sms_enabled=False
        )

        before = datetime.now(UTC)
        preferences = NotificationService.create_or_update_account_notification_preferences(
            account_id=self.account.id, actor=TEST_ACTOR, preferences=update_preferences
        )
        after = datetime.now(UTC)

        assert preferences.created_at is not None
        assert preferences.updated_at is not None
        assert before - timedelta(milliseconds=1) <= preferences.updated_at <= after
        assert preferences.updated_at > preferences.created_at
