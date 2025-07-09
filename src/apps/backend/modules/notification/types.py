from dataclasses import dataclass
from typing import Any, Dict

from modules.account.types import PhoneNumber


@dataclass(frozen=True)
class EmailSender:
    email: str
    name: str


@dataclass(frozen=True)
class EmailRecipient:
    email: str


@dataclass(frozen=True)
class NotificationPreferences:
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
class CommunicationErrorCode:
    VALIDATION_ERROR = "COMMUNICATION_ERR_01"
    SERVICE_ERROR = "COMMUNICATION_ERR_02"


@dataclass(frozen=True)
class UpdateNotificationPreferencesParams:
    account_id: str
    email_enabled: bool
    push_enabled: bool
    sms_enabled: bool


@dataclass(frozen=True)
class ValidationFailure:
    field: str
    message: str
