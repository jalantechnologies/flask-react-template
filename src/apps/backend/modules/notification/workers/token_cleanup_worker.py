from typing import Any

from modules.application.types import BaseWorker, WorkerPriority
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.notification.notification_service import NotificationService


class TokenCleanupWorker(BaseWorker):

    priority: WorkerPriority = WorkerPriority.DEFAULT
    max_execution_time_in_seconds: int = 300
    max_retries: int = 3

    @staticmethod
    async def execute(*args: Any) -> None:
        try:
            cleanup_days = ConfigService[int].get_value(key="notification.token_cleanup_days", default=60)

            Logger.info(message=f"Starting token cleanup for tokens inactive for {cleanup_days} days")

            deleted_count = NotificationService.cleanup_inactive_tokens(days=cleanup_days)

            Logger.info(message=f"Token cleanup completed successfully. Removed {deleted_count} inactive tokens")

        except Exception as e:
            Logger.error(message=f"Token cleanup failed: {str(e)}")
            raise

    async def run(self, *args: Any) -> None:
        await super().run(*args)
