from typing import Optional

from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.notification.internals.twilio_service import TwilioService
from modules.notification.types import NotificationPreferences, SendSMSParams


class SMSService:
    @staticmethod
    def send_sms(*, params: SendSMSParams) -> None:
        is_sms_enabled = ConfigService[bool].get_value(key="sms.enabled")
        if not is_sms_enabled:
            Logger.warn(message=f"SMS is disabled. Could not send message - {params.message_body}")
            return

        TwilioService.send_sms(params=params)

    @staticmethod
    def send_sms_with_preferences(
        *, params: SendSMSParams, preferences: Optional[NotificationPreferences] = None
    ) -> None:
        if preferences and not preferences.sms_enabled:
            Logger.info(message="SMS notification skipped: disabled by user preferences")
            return

        SMSService.send_sms(params=params)
