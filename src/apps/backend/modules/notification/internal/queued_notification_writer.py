from datetime import UTC, datetime, timedelta

from modules.core.common.types import AuditActor
from modules.notification.internal.store.queued_notification_repository import QueuedNotificationRepository
from modules.notification.types import (
    EmailNotificationPayload,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    QueuedNotification,
    QueuedNotificationQuery,
)

DEFAULT_MAX_RETRIES = 5
RETRY_BACKOFF_BASE_SECONDS = 30
DEFAULT_EXPIRY = timedelta(hours=24)
PROCESSING_LEASE = timedelta(minutes=10)


class QueuedNotificationWriter:
    @staticmethod
    def enqueue_email(
        *, account_id: str, payload: EmailNotificationPayload, priority: NotificationPriority, actor: AuditActor
    ) -> QueuedNotification:
        now = datetime.now(UTC)
        notification = QueuedNotification(
            account_id=account_id,
            channel=NotificationChannel.EMAIL,
            payload=payload,
            priority=priority,
            status=NotificationStatus.PENDING,
            expires_at=now + DEFAULT_EXPIRY,
            max_retries=DEFAULT_MAX_RETRIES,
            retry_count=0,
            next_retry_at=now,
        )
        return QueuedNotificationRepository.create(notification, actor=actor)

    @staticmethod
    def claim_for_processing(*, notification: QueuedNotification, actor: AuditActor) -> bool:
        claimed = QueuedNotificationRepository.update_by_query(
            QueuedNotificationQuery(
                id=str(notification.id),
                statuses=[NotificationStatus.PENDING, NotificationStatus.PROCESSING],
                due_before=datetime.now(UTC),
            ),
            {"status": NotificationStatus.PROCESSING.value, "next_retry_at": datetime.now(UTC) + PROCESSING_LEASE},
            actor=actor,
        )
        return claimed is not None

    @staticmethod
    def mark_sent(*, notification_id: str, actor: AuditActor) -> None:
        QueuedNotificationRepository.update_fields(
            notification_id,
            {"status": NotificationStatus.SENT.value, "sent_at": datetime.now(UTC), "error_message": None},
            actor=actor,
        )

    @staticmethod
    def mark_expired(*, notification_id: str, actor: AuditActor) -> None:
        QueuedNotificationRepository.update_fields(
            notification_id, {"status": NotificationStatus.EXPIRED.value}, actor=actor
        )

    @staticmethod
    def record_send_failure(*, notification: QueuedNotification, error_message: str, actor: AuditActor) -> None:
        next_retry_count = notification.retry_count + 1
        if next_retry_count > notification.max_retries:
            QueuedNotificationRepository.update_fields(
                str(notification.id),
                {
                    "status": NotificationStatus.FAILED.value,
                    "retry_count": next_retry_count,
                    "error_message": error_message,
                },
                actor=actor,
            )
            return
        QueuedNotificationRepository.update_fields(
            str(notification.id),
            {
                "status": NotificationStatus.PENDING.value,
                "retry_count": next_retry_count,
                "next_retry_at": QueuedNotificationWriter._backoff_from(next_retry_count),
                "error_message": error_message,
            },
            actor=actor,
        )

    @staticmethod
    def _backoff_from(retry_count: int) -> datetime:
        delay_seconds = RETRY_BACKOFF_BASE_SECONDS * (2 ** (retry_count - 1))
        return datetime.now(UTC) + timedelta(seconds=delay_seconds)
