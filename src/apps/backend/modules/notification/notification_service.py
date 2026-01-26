from typing import Optional

from modules.logger.logger import Logger
from modules.notification.email_service import EmailService
from modules.notification.sms_service import SMSService
from modules.notification.internals.account_notification_preferences_writer import AccountNotificationPreferenceWriter
from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.types import (
    SendEmailParams,
    SendSMSParams,
    CreateOrUpdateAccountNotificationPreferencesParams,
    AccountNotificationPreferences,
)

from modules.push_notification.push_notification_service import PushNotificationService
from modules.push_notification.types import PushNotification, SendPushNotificationParams


class NotificationService:

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

    @staticmethod
    def send_push_for_account(*, account_id: str, params: SendPushNotificationParams, bypass_preferences: bool = False) -> Optional[PushNotification]:
        try:
            if not bypass_preferences:
                preferences = NotificationService.get_account_notification_preferences_by_account_id(account_id=account_id)
                
                if not preferences.push_enabled:
                    Logger.info(
                        message=f"Push notifications disabled for account | account_id={account_id}"
                    )
                    return None
            
            return PushNotificationService.send_notification(
                account_id=account_id,
                title=params.title,
                body=params.body,
                data=params.data,
                priority=params.priority,
                max_retries=params.max_retries,
            )
        
        except Exception as e:
            Logger.error(
                message=(
                    f"Failed to send push notification for account | "
                    f"account_id={account_id} | "
                    f"error={str(e)}"
                )
            )
            raise
