from typing import Optional
from modules.account.internal.store.account_notification_preferences_model import AccountNotificationPreferencesModel
from modules.account.internal.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.account.internal.account_notification_preference_util import AccountNotificationPreferenceUtil
from modules.notification.types import NotificationPreferencesParams


class AccountNotificationPreferenceReader:
    @staticmethod
    def get_notification_preferences_by_account_id(account_id: str) -> NotificationPreferencesParams:
        notification_preferences = AccountNotificationPreferencesRepository.collection().find_one(
            {"account_id": account_id}
        )

        if notification_preferences is None:
            default_preferences = AccountNotificationPreferencesModel(account_id=account_id, id=None).to_bson()
            query = AccountNotificationPreferencesRepository.collection().insert_one(default_preferences)
            notification_preferences = AccountNotificationPreferencesRepository.collection().find_one(
                {"_id": query.inserted_id}
            )

        return AccountNotificationPreferenceUtil.convert_notification_preferences_bson_to_params(
            notification_preferences
        )

    @staticmethod
    def get_existing_notification_preferences_by_account_id(account_id: str) -> Optional[NotificationPreferencesParams]:
        notification_preferences = AccountNotificationPreferencesRepository.collection().find_one(
            {"account_id": account_id}
        )

        if notification_preferences is None:
            return None

        return AccountNotificationPreferenceUtil.convert_notification_preferences_bson_to_params(
            notification_preferences
        )
