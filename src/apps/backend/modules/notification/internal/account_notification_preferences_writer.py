from typing import Any

from modules.application.common.types import AuditActor
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
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams, actor: AuditActor
    ) -> AccountNotificationPreferences:
        new_preferences = AccountNotificationPreferences(
            account_id=account_id,
            email_enabled=preferences.email_enabled if preferences.email_enabled is not None else True,
            push_enabled=preferences.push_enabled if preferences.push_enabled is not None else True,
            sms_enabled=preferences.sms_enabled if preferences.sms_enabled is not None else True,
        )
        return AccountNotificationPreferencesRepository.create(new_preferences, actor=actor)

    @staticmethod
    def _update_account_notification_preferences(
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams, actor: AuditActor
    ) -> AccountNotificationPreferences:
        update_data: dict[str, Any] = {}

        if preferences.email_enabled is not None:
            update_data["email_enabled"] = preferences.email_enabled

        if preferences.push_enabled is not None:
            update_data["push_enabled"] = preferences.push_enabled

        if preferences.sms_enabled is not None:
            update_data["sms_enabled"] = preferences.sms_enabled

        return AccountNotificationPreferencesRepository.update_by_account_id(account_id, update_data, actor=actor)

    @staticmethod
    def create_or_update_account_notification_preferences(
        account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams, actor: AuditActor
    ) -> AccountNotificationPreferences:
        try:
            AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(account_id)
            return AccountNotificationPreferenceWriter._update_account_notification_preferences(
                account_id, preferences, actor
            )
        except AccountNotificationPreferencesNotFoundError:
            return AccountNotificationPreferenceWriter._create_account_notification_preferences(
                account_id, preferences, actor
            )
