import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from modules.account.types import PhoneNumber
from modules.core.common.types import QueryParams


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


class NotificationPriority(str, enum.Enum):
    IMMEDIATE = "immediate"
    NORMAL = "normal"


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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class AccountNotificationPreferencesQuery(QueryParams):
    account_id: Optional[str] = None
    # Preferences are soft-deleted via `active`; reads default to active records only.
    active: Optional[bool] = True


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
class EmailNotificationPayload:
    recipient_email: str
    sender_email: str
    sender_name: str
    template_id: str
    template_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_send_email_params(cls, params: "SendEmailParams") -> "EmailNotificationPayload":
        return cls(
            recipient_email=params.recipient.email,
            sender_email=params.sender.email,
            sender_name=params.sender.name,
            template_id=params.template_id,
            template_data=params.template_data,
        )

    def to_send_email_params(self) -> "SendEmailParams":
        return SendEmailParams(
            recipient=EmailRecipient(email=self.recipient_email),
            sender=EmailSender(email=self.sender_email, name=self.sender_name),
            template_id=self.template_id,
            template_data=self.template_data,
        )


@dataclass(frozen=True)
class QueuedNotification:
    account_id: str
    channel: NotificationChannel
    payload: EmailNotificationPayload
    priority: NotificationPriority
    status: NotificationStatus
    expires_at: datetime
    id: Optional[str] = None
    max_retries: int = 5
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class QueuedNotificationQuery(QueryParams):
    id: Optional[str] = None
    account_id: Optional[str] = None
    statuses: Optional[List[NotificationStatus]] = None
    due_before: Optional[datetime] = None


@dataclass(frozen=True)
class NotificationErrorCode:
    PREFERENCES_NOT_FOUND = "NOTIFICATION_ERR_01"
    VALIDATION_ERROR = "NOTIFICATION_ERR_02"
    SERVICE_ERROR = "NOTIFICATION_ERR_03"


@dataclass(frozen=True)
class ValidationFailure:
    field: str
    message: str
