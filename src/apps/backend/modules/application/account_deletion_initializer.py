from modules.application.internal.account_deletion_registry import AccountDeletionRegistry
from modules.authentication.internal.authentication_cleanup_hook import AuthenticationCleanupHook
from modules.notification.internal.notification_cleanup_hook import NotificationCleanupHook
from modules.logger.logger import Logger


class AccountDeletionInitializer:

    @staticmethod
    def initialize() -> None:
        """Register all available cleanup hooks with the registry"""
        Logger.info(message="Initializing account deletion cleanup hooks")

        try:
            auth_hook = AuthenticationCleanupHook()
            AccountDeletionRegistry.register_hook(auth_hook)

            notification_hook = NotificationCleanupHook()
            AccountDeletionRegistry.register_hook(notification_hook)

            registered_hooks = list(AccountDeletionRegistry.get_all_hooks().keys())
            Logger.info(
                message=f"Successfully initialized {len(registered_hooks)} cleanup hooks: {', '.join(registered_hooks)}"
            )

        except Exception as e:
            Logger.error(message=f"Failed to initialize account deletion hooks: {str(e)}")
            raise
