from typing import Optional

from modules.logger.logger import Logger
from modules.notification.internals.sendgrid_service import SendGridService
from modules.notification.types import NotificationPreferences, SendEmailParams


class EmailService:
    @staticmethod
    def send_email(*, params: SendEmailParams) -> None:
        return SendGridService.send_email(params)

    @staticmethod
    def send_email_with_preferences(
        *, params: SendEmailParams, preferences: Optional[NotificationPreferences] = None
    ) -> None:
        if preferences and not preferences.email_enabled:
            Logger.info(message="Email notification skipped: disabled by user preferences")
            return

        EmailService.send_email(params=params)
