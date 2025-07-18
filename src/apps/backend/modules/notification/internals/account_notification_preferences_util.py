from typing import Any
from modules.notification.internals.store.account_notification_preferences_model import (
    AccountNotificationPreferencesModel,
)
from modules.notification.types import AccountNotificationPreferences


class AccountNotificationPreferenceUtil:
    @staticmethod
    def convert_account_notification_preferences_bson_to_account_notification_preferences(
        notification_preferences_bson: dict[str, Any],
    ) -> AccountNotificationPreferences:
        validated_preferences_data = AccountNotificationPreferencesModel.from_bson(notification_preferences_bson)
        return AccountNotificationPreferences(
            account_id=validated_preferences_data.account_id,
            email_enabled=validated_preferences_data.email_enabled,
            push_enabled=validated_preferences_data.push_enabled,
            sms_enabled=validated_preferences_data.sms_enabled,
        )
