from typing import Optional

from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.notification.internals.twilio_service import TwilioService
from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.types import SendSMSParams


class SMSService:
    @staticmethod
    def send_sms(*, account_id: Optional[str] = None, bypass_preferences: bool = False, params: SendSMSParams) -> None:
        is_sms_enabled = ConfigService[bool].get_value(key="sms.enabled")
        if not is_sms_enabled:
            Logger.warn(
                message=f"SMS is disabled. Could not send message to {params.recipient_phone}"
                + (f" for account {account_id}" if account_id else "")
                + f" - message: {params.message_body}"
            )
            return

        preferences = None
        if account_id:
            try:
                preferences = AccountNotificationPreferenceReader.get_notification_preferences_by_account_id(account_id)
            except Exception as e:
                Logger.warn(message=f"Could not retrieve notification preferences for account {account_id}: {e}")
                preferences = None

        if not bypass_preferences and preferences and not preferences.sms_enabled:
            Logger.info(
                message=f"SMS notification skipped for {params.recipient_phone}"
                + (f" (account {account_id})" if account_id else "")
                + ": disabled by user preferences"
            )
            return

        TwilioService.send_sms(params=params)
