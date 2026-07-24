from datetime import UTC, datetime
from typing import Optional

from modules.core.common.types import AuditActor
from modules.logger.logger import Logger
from modules.notification.internal.queued_notification_writer import QueuedNotificationWriter
from modules.notification.internal.sendgrid_service import SendGridService
from modules.notification.types import EmailNotificationPayload, NotificationChannel, QueuedNotification


class QueuedNotificationDeliveryService:
    @staticmethod
    def deliver(
        *, notification: QueuedNotification, actor: AuditActor, payload: Optional[EmailNotificationPayload] = None
    ) -> None:
        if notification.expires_at <= datetime.now(UTC):
            QueuedNotificationWriter.mark_expired(notification_id=str(notification.id), actor=actor)
            return

        if not QueuedNotificationWriter.claim_for_processing(notification=notification, actor=actor):
            return

        send_payload = payload if payload is not None else notification.payload
        try:
            QueuedNotificationDeliveryService._send(notification.channel, send_payload)
        except Exception as error:
            Logger.error(message=f"Failed to send {notification.channel.value} notification {notification.id}: {error}")
            QueuedNotificationWriter.record_send_failure(
                notification=notification, error_message=str(error), actor=actor
            )
            return

        QueuedNotificationWriter.mark_sent(notification_id=str(notification.id), actor=actor)

    @staticmethod
    def _send(channel: NotificationChannel, payload: EmailNotificationPayload) -> None:
        if channel is NotificationChannel.EMAIL:
            SendGridService.send_email(payload.to_send_email_params())
            return
        raise ValueError(f"Unsupported notification channel: {channel.value}")
