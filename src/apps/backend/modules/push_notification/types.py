from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List


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
class PushNotificationErrorCode:
    NOT_FOUND: str = "PUSH_NOTIFICATION_ERR_01"
    BAD_REQUEST: str = "PUSH_NOTIFICATION_ERR_02"
    INVALID_STATUS: str = "PUSH_NOTIFICATION_ERR_03"
    INVALID_PRIORITY: str = "PUSH_NOTIFICATION_ERR_04"
    MAX_RETRIES_EXCEEDED: str = "PUSH_NOTIFICATION_ERR_05"
