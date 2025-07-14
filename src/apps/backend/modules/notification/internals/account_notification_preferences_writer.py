from datetime import datetime
from pymongo import ReturnDocument

from modules.notification.internals.store.account_notification_preferences_model import (
    AccountNotificationPreferencesModel,
)
from modules.notification.internals.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.internals.account_notification_preferences_util import AccountNotificationPreferenceUtil
from modules.notification.errors import AccountNotificationPreferencesNotFoundError
from modules.notification.types import NotificationPreferences


class AccountNotificationPreferenceWriter:
    @staticmethod
    def create_account_notification_preferences(
        account_id: str, preferences: NotificationPreferences
    ) -> NotificationPreferences:
        preferences_model = AccountNotificationPreferencesModel(
            account_id=account_id,
            id=None,
            email_enabled=preferences.email_enabled,
            push_enabled=preferences.push_enabled,
            sms_enabled=preferences.sms_enabled,
            active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ).to_bson()

        query = AccountNotificationPreferencesRepository.collection().insert_one(preferences_model)
        created_preferences = AccountNotificationPreferencesRepository.collection().find_one({"_id": query.inserted_id})

        return AccountNotificationPreferenceUtil.convert_account_notification_preferences_bson_to_account_params(
            created_preferences
        )

    @staticmethod
    def create_or_update_account_notification_preferences(
        account_id: str, preferences: NotificationPreferences
    ) -> NotificationPreferences:
        from modules.notification.internals.account_notification_preferences_reader import (
            AccountNotificationPreferenceReader,
        )

        try:
            AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(account_id)
            return AccountNotificationPreferenceWriter.update_account_notification_preferences(account_id, preferences)
        except AccountNotificationPreferencesNotFoundError:
            return AccountNotificationPreferenceWriter.create_account_notification_preferences(account_id, preferences)

    @staticmethod
    def update_account_notification_preferences(
        account_id: str, preferences: NotificationPreferences
    ) -> NotificationPreferences:
        update_data = {
            "email_enabled": preferences.email_enabled,
            "push_enabled": preferences.push_enabled,
            "sms_enabled": preferences.sms_enabled,
            "updated_at": datetime.now(),
        }

        updated_preferences = AccountNotificationPreferencesRepository.collection().find_one_and_update(
            {"account_id": account_id, "active": True}, {"$set": update_data}, return_document=ReturnDocument.AFTER
        )

        return AccountNotificationPreferenceUtil.convert_account_notification_preferences_bson_to_account_params(
            updated_preferences
        )
