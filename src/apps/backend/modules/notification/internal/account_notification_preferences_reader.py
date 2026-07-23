from modules.core.common.types import AuditActor
from modules.notification.errors import AccountNotificationPreferencesNotFoundError
from modules.notification.internal.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.types import AccountNotificationPreferences, AccountNotificationPreferencesQuery


class AccountNotificationPreferenceReader:
    @staticmethod
    def get_account_notification_preferences_by_account_id(
        account_id: str, *, actor: AuditActor
    ) -> AccountNotificationPreferences:
        preferences = AccountNotificationPreferencesRepository.query_one(
            AccountNotificationPreferencesQuery(account_id=account_id), actor=actor
        )

        if preferences is None:
            raise AccountNotificationPreferencesNotFoundError(account_id=account_id)

        return preferences
