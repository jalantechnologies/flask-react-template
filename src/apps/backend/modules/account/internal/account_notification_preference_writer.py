from datetime import datetime

from modules.account.internal.store.account_notification_preferences_model import AccountNotificationPreferencesModel
from modules.account.internal.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.types import NotificationPreferences


class AccountNotificationPreferenceWriter:
    @staticmethod
    def create_notification_preferences(account_id: str, params: NotificationPreferences) -> NotificationPreferences:
        preferences_model = AccountNotificationPreferencesModel(
            account_id=account_id,
            id=None,
            email_enabled=params.email_enabled,
            push_enabled=params.push_enabled,
            sms_enabled=params.sms_enabled,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ).to_bson()

        AccountNotificationPreferencesRepository.collection().insert_one(preferences_model)

        return NotificationPreferences(
            email_enabled=params.email_enabled, push_enabled=params.push_enabled, sms_enabled=params.sms_enabled
        )

    @staticmethod
    def update_notification_preferences(account_id: str, params: NotificationPreferences) -> NotificationPreferences:
        update_data = {
            "email_enabled": params.email_enabled,
            "push_enabled": params.push_enabled,
            "sms_enabled": params.sms_enabled,
            "updated_at": datetime.now(),
        }

        AccountNotificationPreferencesRepository.collection().update_one(
            {"account_id": account_id}, {"$set": update_data}
        )

        return NotificationPreferences(
            email_enabled=params.email_enabled, push_enabled=params.push_enabled, sms_enabled=params.sms_enabled
        )
