from typing import Optional

from modules.logger.logger import Logger
from modules.notification.internals.sendgrid_service import SendGridService
from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.types import SendEmailParams


class EmailService:
    @staticmethod
    def send_email_for_account(
        *, account_id: Optional[str] = None, bypass_preferences: bool = False, params: SendEmailParams
    ) -> None:
        preferences = None
        if account_id:
            try:
                preferences = AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(account_id)
            except Exception as e:
                Logger.warn(message=f"Could not retrieve notification preferences for account {account_id}: {e}")
                preferences = None

        if not bypass_preferences and preferences and not preferences.email_enabled:
            Logger.info(
                message=f"Email notification skipped for {params.recipient.email}"
                + (f" (account {account_id})" if account_id else "")
                + f" using template {params.template_id}: disabled by user preferences"
            )
            return

        return SendGridService.send_email(params)
