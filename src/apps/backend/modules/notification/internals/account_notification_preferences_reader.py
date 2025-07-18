from modules.notification.internals.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.internals.account_notification_preferences_util import AccountNotificationPreferenceUtil
from modules.notification.errors import AccountNotificationPreferencesNotFoundError
from modules.notification.types import AccountNotificationPreferences


class AccountNotificationPreferenceReader:
    @staticmethod
    def get_account_notification_preferences_by_account_id(account_id: str) -> AccountNotificationPreferences:
        notification_preferences = AccountNotificationPreferencesRepository.collection().find_one(
            {"account_id": account_id, "active": True}
        )

        if notification_preferences is None:
            raise AccountNotificationPreferencesNotFoundError(account_id=account_id)

        return AccountNotificationPreferenceUtil.convert_account_notification_preferences_bson_to_account_notification_preferences(
            notification_preferences
        )
