from typing import Optional

from modules.core.common.types import AuditActor
from modules.logger.logger import Logger
from modules.notification.internal.account_notification_preferences_reader import AccountNotificationPreferenceReader
from modules.notification.internal.account_notification_preferences_writer import AccountNotificationPreferenceWriter
from modules.notification.queued_notification_service import QueuedNotificationService
from modules.notification.sms_service import SMSService
from modules.notification.types import (
    AccountNotificationPreferences,
    CreateOrUpdateAccountNotificationPreferencesParams,
    NotificationPriority,
    QueuedNotification,
    SendEmailParams,
    SendSMSParams,
)


class NotificationService:

    @staticmethod
    def send_email_for_account(
        *,
        account_id: str,
        bypass_preferences: bool = False,
        params: SendEmailParams,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        actor: AuditActor,
    ) -> Optional[QueuedNotification]:
        if not bypass_preferences:
            preferences = AccountNotificationPreferenceReader.get_account_notification_preferences_by_account_id(
                account_id, actor=actor
            )
            if not preferences.email_enabled:
                Logger.info(
                    message=f"Email notification skipped for {params.recipient.email} "
                    f"(account {account_id}) using template {params.template_id}: "
                    f"disabled by user preferences"
                )
                return None

        return QueuedNotificationService.queue_email(
            account_id=account_id, params=params, priority=priority, actor=actor
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
