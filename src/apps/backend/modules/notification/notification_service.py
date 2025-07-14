from modules.notification.email_service import EmailService
from modules.notification.sms_service import SMSService
from modules.notification.internals.account_notification_preferences_writer import AccountNotificationPreferenceWriter
from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.types import (
    SendEmailParams,
    SendSMSParams,
    NotificationPreferences,
    AccountNotificationPreferences,
)


class NotificationService:

    @staticmethod
    def send_email(*, params: SendEmailParams) -> None:
        return EmailService.send_email_for_account(params=params)

    @staticmethod
    def send_sms(*, params: SendSMSParams) -> None:
        return SMSService.send_sms_for_account(params=params)

    @staticmethod
    def create_or_update_account_notification_preferences(
        *, account_id: str, preferences: NotificationPreferences
    ) -> AccountNotificationPreferences:
        return AccountNotificationPreferenceWriter.create_or_update_account_notification_preferences(
            account_id, preferences
        )

    @staticmethod
    def get_account_notification_preferences_by_account_id(*, account_id: str) -> AccountNotificationPreferences:
        return AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(account_id)
