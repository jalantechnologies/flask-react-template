from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.notification.internals.twilio_service import TwilioService
from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.types import SendSMSParams


class SMSService:
    @staticmethod
    def send_sms_for_account(*, account_id: str, bypass_preferences: bool = False, params: SendSMSParams) -> None:
        is_sms_enabled = ConfigService[bool].get_value(key="sms.enabled")
        if not is_sms_enabled:
            Logger.warn(message=f"SMS is disabled. Could not send message - {params.message_body}")
            return

        if not bypass_preferences:
            preferences = AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(
                account_id
            )
            if not preferences.sms_enabled:
                Logger.info(
                    message=f"SMS notification skipped for {params.recipient_phone} "
                    f"(account {account_id}): disabled by user preferences"
                )
                return

        TwilioService.send_sms(params=params)
