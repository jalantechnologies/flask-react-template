from modules.application.common.types import AuditActor
from modules.notification.email_service import EmailService
from modules.notification.internal.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.internal.account_notification_preferences_writer import AccountNotificationPreferenceWriter
from modules.notification.sms_service import SMSService
from modules.notification.types import (
    AccountNotificationPreferences,
    CreateOrUpdateAccountNotificationPreferencesParams,
    SendEmailParams,
    SendSMSParams,
)


class NotificationService:

    @staticmethod
    def send_email_for_account(
        *, account_id: str, bypass_preferences: bool = False, params: SendEmailParams, actor: AuditActor
    ) -> None:
        return EmailService.send_email_for_account(
            account_id=account_id, bypass_preferences=bypass_preferences, params=params, actor=actor
        )

    @staticmethod
    def send_sms_for_account(
        *, account_id: str, bypass_preferences: bool = False, params: SendSMSParams, actor: AuditActor
    ) -> None:
        return SMSService.send_sms_for_account(
            account_id=account_id, bypass_preferences=bypass_preferences, params=params, actor=actor
        )

    @staticmethod
    def create_or_update_account_notification_preferences(
        *, account_id: str, actor: AuditActor, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        return AccountNotificationPreferenceWriter.create_or_update_account_notification_preferences(
            account_id, preferences, actor
        )

    @staticmethod
    def get_account_notification_preferences_by_account_id(
        *, account_id: str, actor: AuditActor
    ) -> AccountNotificationPreferences:
        return AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(
            account_id, actor=actor
        )
