from dataclasses import dataclass
from typing import Any, Dict, Optional

from modules.account.types import PhoneNumber


@dataclass(frozen=True)
class EmailSender:
    email: str
    name: str


@dataclass(frozen=True)
class EmailRecipient:
    email: str


@dataclass(frozen=True)
class CreateOrUpdateAccountNotificationPreferencesParams:
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None


@dataclass(frozen=True)
class AccountNotificationPreferences:
    account_id: str
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = True


@dataclass(frozen=True)
class SendEmailParams:
    recipient: EmailRecipient
    sender: EmailSender
    template_id: str
    template_data: Dict[str, Any] | None = None


@dataclass(frozen=True)
class SendSMSParams:
    message_body: str
    recipient_phone: PhoneNumber


@dataclass(frozen=True)
class NotificationErrorCode:
    PREFERENCES_NOT_FOUND = "NOTIFICATION_ERR_01"
    VALIDATION_ERROR = "NOTIFICATION_ERR_02"
    SERVICE_ERROR = "NOTIFICATION_ERR_03"


@dataclass(frozen=True)
class ValidationFailure:
    field: str
    message: str
