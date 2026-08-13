from typing import Any, ClassVar, Optional

from modules.core.common.types import AuditActor
from modules.core.job import Job
from modules.logger.logger import Logger
from modules.notification.queued_notification_service import QueuedNotificationService


class NotificationDrainJob(Job):
    queue = "default"
    cron_schedule: ClassVar[Optional[str]] = "*/5 * * * *"

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> None:
        drained = QueuedNotificationService.drain_pending_notifications(actor=actor)
        Logger.info(message=f"NotificationDrainJob processed {drained} queued notifications")
