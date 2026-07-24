from datetime import UTC, datetime

from modules.core.common.types import AuditActor
from modules.logger.logger import Logger
from modules.notification.internal.queued_notification_writer import QueuedNotificationWriter
from modules.notification.internal.sendgrid_service import SendGridService
from modules.notification.types import NotificationChannel, QueuedNotification


class QueuedNotificationDeliveryService:
    @staticmethod
    def deliver(*, notification: QueuedNotification, actor: AuditActor) -> None:
        if notification.expires_at <= datetime.now(UTC):
            QueuedNotificationWriter.mark_expired(notification_id=str(notification.id), actor=actor)
            return

        QueuedNotificationWriter.mark_processing(notification_id=str(notification.id), actor=actor)

        try:
            QueuedNotificationDeliveryService._send(notification)
        except Exception as error:
            Logger.error(message=f"Failed to send {notification.channel.value} notification {notification.id}: {error}")
            QueuedNotificationWriter.record_send_failure(
                notification=notification, error_message=str(error), actor=actor
            )
            return

        QueuedNotificationWriter.mark_sent(notification_id=str(notification.id), actor=actor)

    @staticmethod
    def _send(notification: QueuedNotification) -> None:
        if notification.channel is NotificationChannel.EMAIL:
            SendGridService.send_email(notification.payload.to_send_email_params())
            return
        raise ValueError(f"Unsupported notification channel: {notification.channel.value}")
