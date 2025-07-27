from modules.logger.logger import Logger
from modules.notification.internals.sendgrid_service import SendGridService
from modules.notification.internals.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.types import SendEmailParams


class EmailService:
    @staticmethod
    def send_email_for_account(*, account_id: str, bypass_preferences: bool = False, params: SendEmailParams) -> None:
        if not bypass_preferences:
            preferences = AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(
                account_id
            )
            if not preferences.email_enabled:
                Logger.info(
                    message=f"Email notification skipped for {params.recipient.email} "
                    f"(account {account_id}) using template {params.template_id}: "
                    f"disabled by user preferences"
                )
                return

        return SendGridService.send_email(params)
