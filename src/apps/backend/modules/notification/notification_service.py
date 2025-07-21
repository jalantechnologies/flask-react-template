from typing import List

from modules.notification.email_service import EmailService
from modules.notification.internals.device_token_reader import DeviceTokenReader
from modules.notification.internals.device_token_writer import DeviceTokenWriter
from modules.notification.sms_service import SMSService
from modules.notification.internals.account_notification_preferences_writer import AccountNotificationPreferenceWriter
from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.types import (
    DeviceToken,
    RegisterDeviceTokenParams,
    SendEmailParams,
    SendSMSParams,
    CreateOrUpdateAccountNotificationPreferencesParams,
    AccountNotificationPreferences,
)


class NotificationService:
    @staticmethod
    def upsert_user_fcm_token(*, params: RegisterDeviceTokenParams) -> DeviceToken:
        return DeviceTokenWriter.upsert_user_fcm_token(params=params)

    @staticmethod
    def delete_user_fcm_tokens_by_user_id(user_id: str) -> int:
        return DeviceTokenWriter.delete_user_fcm_tokens_by_user_id(user_id)

    @staticmethod
    def get_user_fcm_tokens(user_id: str) -> List[str]:
        return DeviceTokenReader.get_user_fcm_tokens(user_id)

    @staticmethod
    def send_email_for_account(*, account_id: str, bypass_preferences: bool = False, params: SendEmailParams) -> None:
        return EmailService.send_email_for_account(
            account_id=account_id, bypass_preferences=bypass_preferences, params=params
        )

    @staticmethod
    def send_sms_for_account(*, account_id: str, bypass_preferences: bool = False, params: SendSMSParams) -> None:
        return SMSService.send_sms_for_account(
            account_id=account_id, bypass_preferences=bypass_preferences, params=params
        )

    @staticmethod
    def create_or_update_account_notification_preferences(
        *, account_id: str, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        return AccountNotificationPreferenceWriter.create_or_update_account_notification_preferences(
            account_id, preferences
        )

    @staticmethod
    def get_account_notification_preferences_by_account_id(*, account_id: str) -> AccountNotificationPreferences:
        return AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(account_id)
