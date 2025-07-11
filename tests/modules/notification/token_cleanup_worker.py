from typing import Any

from modules.application.types import BaseWorker, WorkerPriority
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.notification.notification_service import NotificationService


class TokenCleanupWorker(BaseWorker):
    priority = WorkerPriority.DEFAULT
    max_execution_time_in_seconds = 300
    max_retries = 3

    @staticmethod
    async def execute(*args: Any) -> None:
        try:
            cleanup_enabled = ConfigService[bool].get_value(
                key="notification.token_cleanup_enabled", default=True
            )
            if not cleanup_enabled:
                Logger.info(message="Device token cleanup is disabled. Skipping...")
                return

            cleanup_days = ConfigService[int].get_value(
                key="notification.token_cleanup_days", default=60
            )

            deleted_count = NotificationService.cleanup_inactive_tokens(
                days=cleanup_days
            )

            Logger.info(
                message=f"Token cleanup worker completed. Removed {deleted_count} inactive device tokens."
            )

        except Exception as e:
            Logger.error(message=f"Error in token cleanup worker: {e}")
            raise

    async def run(self, *args: Any) -> None:
        await super().run(*args)
