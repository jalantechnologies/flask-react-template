from datetime import datetime
from typing import Any
from pymongo import ReturnDocument

from modules.notification.internals.store.account_notification_preferences_model import (
    AccountNotificationPreferencesModel,
)
from modules.notification.internals.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.internals.account_notification_preferences_util import AccountNotificationPreferenceUtil
from modules.notification.errors import AccountNotificationPreferencesNotFoundError
from modules.notification.types import (
    CreateOrUpdateAccountNotificationPreferencesParams,
    AccountNotificationPreferences,
)


class AccountNotificationPreferenceWriter:
    @staticmethod
    def _create_account_notification_preferences(
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        preferences_model = AccountNotificationPreferencesModel(
            account_id=account_id,
            id=None,
            email_enabled=preferences.email_enabled if preferences.email_enabled is not None else True,
            push_enabled=preferences.push_enabled if preferences.push_enabled is not None else True,
            sms_enabled=preferences.sms_enabled if preferences.sms_enabled is not None else True,
        ).to_bson()

        query = AccountNotificationPreferencesRepository.collection().insert_one(preferences_model)
        created_preferences = AccountNotificationPreferencesRepository.collection().find_one({"_id": query.inserted_id})

        return AccountNotificationPreferenceUtil.convert_account_notification_preferences_bson_to_account_notification_preferences(
            created_preferences
        )

    @staticmethod
    def _update_account_notification_preferences(
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        update_data: dict[str, Any] = {"updated_at": datetime.now()}

        if preferences.email_enabled is not None:
            update_data["email_enabled"] = preferences.email_enabled

        if preferences.push_enabled is not None:
            update_data["push_enabled"] = preferences.push_enabled

        if preferences.sms_enabled is not None:
            update_data["sms_enabled"] = preferences.sms_enabled

        updated_preferences = AccountNotificationPreferencesRepository.collection().find_one_and_update(
            {"account_id": account_id, "active": True}, {"$set": update_data}, return_document=ReturnDocument.AFTER
        )

        return AccountNotificationPreferenceUtil.convert_account_notification_preferences_bson_to_account_notification_preferences(
            updated_preferences
        )

    @staticmethod
    def create_or_update_account_notification_preferences(
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        try:
            AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(account_id)
            return AccountNotificationPreferenceWriter._update_account_notification_preferences(account_id, preferences)
        except AccountNotificationPreferencesNotFoundError:
            return AccountNotificationPreferenceWriter._create_account_notification_preferences(account_id, preferences)
