from datetime import UTC, datetime
from typing import List

from modules.core.common.types import AuditActor
from modules.notification.internal.store.queued_notification_repository import QueuedNotificationRepository
from modules.notification.types import NotificationStatus, QueuedNotification, QueuedNotificationQuery


class QueuedNotificationReader:
    @staticmethod
    def get_drainable_notifications(*, actor: AuditActor) -> List[QueuedNotification]:
        return QueuedNotificationRepository.query(
            QueuedNotificationQuery(statuses=[NotificationStatus.PENDING], due_before=datetime.now(UTC)), actor=actor
        )
