from modules.core.common.types import AuditActor
from modules.notification.internal.queued_notification_delivery_service import QueuedNotificationDeliveryService
from modules.notification.internal.queued_notification_reader import QueuedNotificationReader
from modules.notification.internal.queued_notification_writer import QueuedNotificationWriter
from modules.notification.types import (
    EmailNotificationPayload,
    NotificationPriority,
    QueuedNotification,
    SendEmailParams,
)


class QueuedNotificationService:
    @staticmethod
    def queue_email(
        *, account_id: str, params: SendEmailParams, priority: NotificationPriority, actor: AuditActor
    ) -> QueuedNotification:
        notification = QueuedNotificationWriter.enqueue_email(
            account_id=account_id,
            payload=EmailNotificationPayload.from_send_email_params(params),
            priority=priority,
            actor=actor,
        )
        if priority is NotificationPriority.IMMEDIATE:
            QueuedNotificationDeliveryService.deliver(notification=notification, actor=actor)
        return notification

    @staticmethod
    def drain_pending_notifications(*, actor: AuditActor) -> int:
        notifications = QueuedNotificationReader.get_drainable_notifications(actor=actor)
        for notification in notifications:
            QueuedNotificationDeliveryService.deliver(notification=notification, actor=actor)
        return len(notifications)
