from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict


class NotificationStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


class Priority(Enum):
    IMMEDIATE = "immediate"
    NORMAL = "normal"

@dataclass(frozen=True)
class PushNotification:
    id: str
    account_id: str
    title: str
    body: str
    device_token_ids: list[str]
    data: Optional[dict]
    status: NotificationStatus
    priority: Priority
    retry_count: int
    max_retries: int
    next_retry_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

@dataclass(frozen=True)
class CreatePushNotificationParams:
    account_id: str
    title: str
    body: str
    device_token_ids: list[str]
    priority: Priority
    data: Optional[Dict] = None
    max_retries: Optional[int] = None
    expires_at: Optional[datetime] = None

@dataclass(frozen=True)
class SendPushNotificationParams:
    title: str
    body: str
    data: Optional[Dict] = None
    priority: str = "normal"
    max_retries: Optional[int] = None

@dataclass(frozen=True)
class GetPendingNotificationsParams:
    limit: int = 100
    skip: int = 0

@dataclass(frozen=True)
class GetRetryNotificationsParams:
    limit: int = 100
    skip: int = 0

@dataclass(frozen=True)
class GetNotificationsByAccountIdParams:
    account_id: str
    limit: int = 100
    skip: int = 0

@dataclass(frozen=True)
class PushNotificationErrorCode:
    NOT_FOUND: str = "PUSH_NOTIFICATION_ERR_01"
    BAD_REQUEST: str = "PUSH_NOTIFICATION_ERR_02"
    INVALID_STATUS: str = "PUSH_NOTIFICATION_ERR_03"
    INVALID_PRIORITY: str = "PUSH_NOTIFICATION_ERR_04"
    MAX_RETRIES_EXCEEDED: str = "PUSH_NOTIFICATION_ERR_05"

@dataclass(frozen=True)
class FCMResponse:
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

@dataclass(frozen=True)
class FCMBatchResponse:
    success_count: int
    failure_count: int
    responses: list[FCMResponse] = field(default_factory=list)

@dataclass(frozen=True)
class NotificationResult:
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    invalid_tokens: list[str] = field(default_factory=list)
