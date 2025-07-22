from modules.application.internal.account_deletion_registry import BaseAccountDeletionHook
from modules.notification.internals.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.logger.logger import Logger


class NotificationCleanupHook(BaseAccountDeletionHook):
    """Cleanup hook for notification-related data during account deletion"""

    @property
    def hook_name(self) -> str:
        return "notification_cleanup"

    def execute(self, account_id: str) -> None:
        Logger.info(message=f"Starting notification data cleanup for account {account_id}")

        self._cleanup_notification_preferences(account_id)

        Logger.info(message=f"Notification data cleanup completed for account {account_id}")

    def _cleanup_notification_preferences(self, account_id: str) -> None:
        try:
            result = AccountNotificationPreferencesRepository.collection().delete_many({"account_id": account_id})
            Logger.info(
                message=f"Deleted {result.deleted_count} notification preference records for account {account_id}"
            )

        except Exception as e:
            Logger.error(message=f"Failed to cleanup notification preferences for account {account_id}: {str(e)}")
            raise
