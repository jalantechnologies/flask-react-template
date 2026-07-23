from typing import Any

from modules.notification.errors import AccountNotificationPreferencesNotFoundError
from modules.notification.internal.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.internal.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.notification.types import (
    AccountNotificationPreferences,
    CreateOrUpdateAccountNotificationPreferencesParams,
)


class AccountNotificationPreferenceWriter:
    @staticmethod
    def _create_account_notification_preferences(
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        new_preferences = AccountNotificationPreferences(
            account_id=account_id,
            email_enabled=preferences.email_enabled if preferences.email_enabled is not None else True,
            push_enabled=preferences.push_enabled if preferences.push_enabled is not None else True,
            sms_enabled=preferences.sms_enabled if preferences.sms_enabled is not None else True,
        )
        return AccountNotificationPreferencesRepository.create(new_preferences)

    @staticmethod
    def _update_account_notification_preferences(
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        update_data: dict[str, Any] = {}

        if preferences.email_enabled is not None:
            update_data["email_enabled"] = preferences.email_enabled

        if preferences.push_enabled is not None:
            update_data["push_enabled"] = preferences.push_enabled

        if preferences.sms_enabled is not None:
            update_data["sms_enabled"] = preferences.sms_enabled

        return AccountNotificationPreferencesRepository.update_by_account_id(account_id, update_data)

    @staticmethod
    def create_or_update_account_notification_preferences(
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        try:
            AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(account_id)
            return AccountNotificationPreferenceWriter._update_account_notification_preferences(account_id, preferences)
        except AccountNotificationPreferencesNotFoundError:
            return AccountNotificationPreferenceWriter._create_account_notification_preferences(account_id, preferences)
