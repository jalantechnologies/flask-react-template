from typing import Optional

from modules.logger.logger import Logger
from modules.notification.internals.sendgrid_service import SendGridService
from modules.notification.types import NotificationPreferences, SendEmailParams


class EmailService:
    @staticmethod
    def send_email(
        *,
        params: SendEmailParams,
        preferences: Optional[NotificationPreferences] = None,
        bypass_preferences: bool = False,
    ) -> None:
        if not bypass_preferences and preferences and not preferences.email_enabled:
            Logger.info(message="Email notification skipped: disabled by user preferences")
            return

        return SendGridService.send_email(params)
