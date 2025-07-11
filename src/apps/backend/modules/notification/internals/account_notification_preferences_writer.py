from datetime import datetime
from pymongo import ReturnDocument

from modules.notification.internals.store.account_notification_preferences_model import AccountNotificationPreferencesModel
from modules.notification.internals.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.internals.account_notification_preferences_util import AccountNotificationPreferenceUtil
from modules.notification.types import NotificationPreferencesParams


class AccountNotificationPreferenceWriter:
    @staticmethod
    def create_notification_preferences(
        account_id: str, preferences: NotificationPreferencesParams
    ) -> NotificationPreferencesParams:
        preferences_model = AccountNotificationPreferencesModel(
            account_id=account_id,
            id=None,
            email_enabled=preferences.email_enabled,
            push_enabled=preferences.push_enabled,
            sms_enabled=preferences.sms_enabled,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ).to_bson()

        query = AccountNotificationPreferencesRepository.collection().insert_one(preferences_model)
        created_preferences = AccountNotificationPreferencesRepository.collection().find_one({"_id": query.inserted_id})

        return AccountNotificationPreferenceUtil.convert_notification_preferences_bson_to_params(created_preferences)

    @staticmethod
    def create_or_update_notification_preferences(
        account_id: str, preferences: NotificationPreferencesParams
    ) -> NotificationPreferencesParams:
        from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader

        existing_preferences = AccountNotificationPreferenceReader.get_existing_notification_preferences_by_account_id(
            account_id
        )

        if existing_preferences is None:
            return AccountNotificationPreferenceWriter.create_notification_preferences(account_id, preferences)
        else:
            return AccountNotificationPreferenceWriter.update_notification_preferences(account_id, preferences)

    @staticmethod
    def update_notification_preferences(
        account_id: str, preferences: NotificationPreferencesParams
    ) -> NotificationPreferencesParams:
        update_data = {
            "email_enabled": preferences.email_enabled,
            "push_enabled": preferences.push_enabled,
            "sms_enabled": preferences.sms_enabled,
            "updated_at": datetime.now(),
        }

        updated_preferences = AccountNotificationPreferencesRepository.collection().find_one_and_update(
            {"account_id": account_id}, {"$set": update_data}, return_document=ReturnDocument.AFTER
        )

        return AccountNotificationPreferenceUtil.convert_notification_preferences_bson_to_params(updated_preferences)
