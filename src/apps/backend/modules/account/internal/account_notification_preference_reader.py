from typing import Any, cast
from modules.account.internal.store.account_notification_preferences_model import AccountNotificationPreferencesModel
from modules.account.internal.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.types import NotificationPreferences


class AccountNotificationPreferenceReader:
    @staticmethod
    def get_notification_preferences_by_account_id(account_id: str) -> NotificationPreferences:
        notification_preferences = AccountNotificationPreferencesRepository.collection().find_one(
            {"account_id": account_id}
        )

        if notification_preferences is None:
            default_preferences = AccountNotificationPreferencesModel(account_id=account_id, id=None).to_bson()
            AccountNotificationPreferencesRepository.collection().insert_one(default_preferences)
            return NotificationPreferences()

        preferences_model = AccountNotificationPreferencesModel.from_bson(notification_preferences)
        return NotificationPreferences(
            email_enabled=preferences_model.email_enabled,
            push_enabled=preferences_model.push_enabled,
            sms_enabled=preferences_model.sms_enabled,
        )

    @staticmethod
    def get_existing_notification_preferences_by_account_id(account_id: str) -> dict[str, Any] | None:
        result = AccountNotificationPreferencesRepository.collection().find_one({"account_id": account_id})
        return cast(dict[str, Any] | None, result)
