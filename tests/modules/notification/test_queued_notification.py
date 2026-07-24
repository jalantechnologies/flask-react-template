import unittest
from datetime import UTC, datetime, timedelta
from typing import Callable, Iterator, Optional
from unittest import mock
from unittest.mock import MagicMock

import pytest

from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.internal.otp.store.otp_repository import OTPRepository
from modules.core.celery_app import app as celery_app
from modules.core.common.types import ActorType
from modules.core.internal.audit.store.audit_log_repository import AuditLogRepository
from modules.notification.internal.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.internal.store.queued_notification_repository import QueuedNotificationRepository
from modules.notification.jobs.notification_drain_job import NotificationDrainJob
from modules.notification.notification_service import NotificationService
from modules.notification.queued_notification_service import QueuedNotificationService
from modules.notification.types import (
    CreateOrUpdateAccountNotificationPreferencesParams,
    EmailNotificationPayload,
    EmailRecipient,
    EmailSender,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    QueuedNotification,
    QueuedNotificationQuery,
    SendEmailParams,
)
from tests.conftest import TEST_ACTOR

SENDGRID_SEND = "modules.notification.internal.queued_notification_delivery_service.SendGridService.send_email"


@pytest.fixture(autouse=True)
def eager_celery() -> Iterator[None]:
    previous_eager = celery_app.conf.task_always_eager
    previous_propagate = celery_app.conf.task_eager_propagates
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = previous_eager
    celery_app.conf.task_eager_propagates = previous_propagate


class BaseTestQueuedNotification(unittest.TestCase):
    def setup_method(self, method: Callable[..., object]) -> None:
        self._clear()
        self.account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="queued@example.com"
            ),
            actor=TEST_ACTOR,
        )

    def teardown_method(self, method: Callable[..., object]) -> None:
        self._clear()

    @staticmethod
    def _clear() -> None:
        QueuedNotificationRepository.collection().delete_many({})
        AccountNotificationPreferencesRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})
        OTPRepository.collection().delete_many({})
        AuditLogRepository.collection().delete_many({})

    def _email_params(self) -> SendEmailParams:
        return SendEmailParams(
            recipient=EmailRecipient(email="queued@example.com"),
            sender=EmailSender(email="sender@example.com", name="Sender"),
            template_id="template-123",
            template_data={"first_name": "first_name"},
        )

    def _stored(self, notification_id: str) -> Optional[QueuedNotification]:
        return QueuedNotificationRepository.find(notification_id, actor=TEST_ACTOR)

    def _seed(
        self,
        *,
        status: NotificationStatus,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        retry_count: int = 0,
        max_retries: int = 5,
        next_retry_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ) -> QueuedNotification:
        now = datetime.now(UTC)
        notification = QueuedNotification(
            account_id=self.account.id,
            channel=NotificationChannel.EMAIL,
            payload=EmailNotificationPayload.from_send_email_params(self._email_params()),
            priority=priority,
            status=status,
            expires_at=expires_at if expires_at is not None else now + timedelta(hours=1),
            max_retries=max_retries,
            retry_count=retry_count,
            next_retry_at=next_retry_at if next_retry_at is not None else now,
        )
        return QueuedNotificationRepository.create(notification, actor=TEST_ACTOR)


class TestGivenAnEmailQueuedAsNormal(BaseTestQueuedNotification):
    @mock.patch(SENDGRID_SEND)
    def test_then_it_is_persisted_pending_and_not_sent_inline(self, mock_send: MagicMock) -> None:
        notification = NotificationService.send_email_for_account(
            account_id=self.account.id,
            params=self._email_params(),
            priority=NotificationPriority.NORMAL,
            actor=TEST_ACTOR,
        )

        assert notification is not None
        stored = self._stored(notification.id or "")
        assert stored is not None
        assert stored.status == NotificationStatus.PENDING
        assert stored.channel == NotificationChannel.EMAIL
        mock_send.assert_not_called()

    @mock.patch(SENDGRID_SEND)
    def test_then_the_drain_job_sends_it_and_marks_sent(self, mock_send: MagicMock) -> None:
        notification = NotificationService.send_email_for_account(
            account_id=self.account.id,
            params=self._email_params(),
            priority=NotificationPriority.NORMAL,
            actor=TEST_ACTOR,
        )
        assert notification is not None

        NotificationDrainJob.perform_async()

        mock_send.assert_called_once()
        stored = self._stored(notification.id or "")
        assert stored is not None
        assert stored.status == NotificationStatus.SENT
        assert stored.sent_at is not None


class TestGivenAnImmediateEmail(BaseTestQueuedNotification):
    @mock.patch(SENDGRID_SEND)
    def test_then_it_sends_synchronously_and_is_marked_sent(self, mock_send: MagicMock) -> None:
        notification = NotificationService.send_email_for_account(
            account_id=self.account.id,
            params=self._email_params(),
            priority=NotificationPriority.IMMEDIATE,
            actor=TEST_ACTOR,
        )

        assert notification is not None
        mock_send.assert_called_once()
        stored = self._stored(notification.id or "")
        assert stored is not None
        assert stored.status == NotificationStatus.SENT


class TestGivenSendGridFails(BaseTestQueuedNotification):
    @mock.patch(SENDGRID_SEND, side_effect=RuntimeError("transient sendgrid error"))
    def test_then_a_transient_failure_increments_retry_and_stays_retryable(self, mock_send: MagicMock) -> None:
        seeded = self._seed(status=NotificationStatus.PENDING)

        drained = QueuedNotificationService.drain_pending_notifications(actor=TEST_ACTOR)
        assert drained == 1

        stored = self._stored(seeded.id or "")
        assert stored is not None
        assert stored.status == NotificationStatus.PENDING
        assert stored.retry_count == 1
        assert stored.next_retry_at is not None
        assert stored.next_retry_at > datetime.now(UTC)
        assert stored.error_message == "transient sendgrid error"

    @mock.patch(SENDGRID_SEND, side_effect=RuntimeError("permanent sendgrid error"))
    def test_then_exceeding_max_retries_marks_failed(self, mock_send: MagicMock) -> None:
        seeded = self._seed(status=NotificationStatus.PENDING, retry_count=5, max_retries=5)

        QueuedNotificationService.drain_pending_notifications(actor=TEST_ACTOR)

        stored = self._stored(seeded.id or "")
        assert stored is not None
        assert stored.status == NotificationStatus.FAILED
        assert stored.retry_count == 6


class TestGivenAnExpiredNotification(BaseTestQueuedNotification):
    @mock.patch(SENDGRID_SEND)
    def test_then_it_is_marked_expired_and_not_sent(self, mock_send: MagicMock) -> None:
        seeded = self._seed(
            status=NotificationStatus.PENDING,
            next_retry_at=datetime.now(UTC) - timedelta(minutes=5),
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )

        QueuedNotificationService.drain_pending_notifications(actor=TEST_ACTOR)

        stored = self._stored(seeded.id or "")
        assert stored is not None
        assert stored.status == NotificationStatus.EXPIRED
        mock_send.assert_not_called()


class TestGivenEmailPreferenceDisabled(BaseTestQueuedNotification):
    @mock.patch(SENDGRID_SEND)
    def test_then_it_is_not_queued_unless_bypassed(self, mock_send: MagicMock) -> None:
        NotificationService.create_or_update_account_notification_preferences(
            account_id=self.account.id,
            actor=TEST_ACTOR,
            preferences=CreateOrUpdateAccountNotificationPreferencesParams(email_enabled=False),
        )

        result = NotificationService.send_email_for_account(
            account_id=self.account.id,
            params=self._email_params(),
            priority=NotificationPriority.IMMEDIATE,
            actor=TEST_ACTOR,
        )

        assert result is None
        mock_send.assert_not_called()
        assert QueuedNotificationRepository.count(QueuedNotificationQuery(account_id=self.account.id)) == 0

    @mock.patch(SENDGRID_SEND)
    def test_then_bypass_preferences_still_sends(self, mock_send: MagicMock) -> None:
        NotificationService.create_or_update_account_notification_preferences(
            account_id=self.account.id,
            actor=TEST_ACTOR,
            preferences=CreateOrUpdateAccountNotificationPreferencesParams(email_enabled=False),
        )

        result = NotificationService.send_email_for_account(
            account_id=self.account.id,
            bypass_preferences=True,
            params=self._email_params(),
            priority=NotificationPriority.IMMEDIATE,
            actor=TEST_ACTOR,
        )

        assert result is not None
        mock_send.assert_called_once()


class TestGivenTheDrainJobSendsAnEmail(BaseTestQueuedNotification):
    @mock.patch(SENDGRID_SEND)
    def test_then_the_send_is_attributed_to_the_job_run_actor(self, mock_send: MagicMock) -> None:
        seeded = self._seed(status=NotificationStatus.PENDING)

        NotificationDrainJob.perform_async()

        mock_send.assert_called_once()
        updates = [
            doc
            for doc in AuditLogRepository.collection().find({})
            if doc["resource_type"] == QueuedNotificationRepository.collection_name
            and doc["resource_id"] == seeded.id
            and doc["action"] == "update"
        ]
        assert updates
        assert all(doc["actor_type"] == ActorType.JOB.value for doc in updates)
        assert all(doc["actor_id"] for doc in updates)


class TestGivenMixedPriorities(BaseTestQueuedNotification):
    @mock.patch(SENDGRID_SEND)
    def test_then_the_drain_orders_immediate_before_normal(self, mock_send: MagicMock) -> None:
        normal = self._seed(status=NotificationStatus.PENDING, priority=NotificationPriority.NORMAL)
        immediate = self._seed(status=NotificationStatus.PENDING, priority=NotificationPriority.IMMEDIATE)

        from modules.notification.internal.queued_notification_reader import QueuedNotificationReader

        drainable = QueuedNotificationReader.get_drainable_notifications(actor=TEST_ACTOR)

        ids = [item.id for item in drainable]
        assert ids.index(immediate.id) < ids.index(normal.id)
