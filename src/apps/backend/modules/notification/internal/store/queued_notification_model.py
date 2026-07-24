from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Dict, NotRequired, Optional

from bson import ObjectId

from modules.core.base_model import BaseModel, StoredDocument, StoredDocumentBase
from modules.notification.types import (
    EmailNotificationPayload,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
)


class EmailNotificationPayloadDocument(StoredDocumentBase):
    recipient_email: str
    sender_email: str
    sender_name: str
    template_id: str
    template_data: NotRequired[Optional[Dict[str, Any]]]


class QueuedNotificationDocument(StoredDocumentBase):
    account_id: NotRequired[str]
    channel: NotRequired[str]
    payload: NotRequired[EmailNotificationPayloadDocument]
    priority: NotRequired[str]
    status: NotRequired[str]
    max_retries: NotRequired[int]
    retry_count: NotRequired[int]
    next_retry_at: NotRequired[Optional[datetime]]
    sent_at: NotRequired[Optional[datetime]]
    delivered_at: NotRequired[Optional[datetime]]
    error_message: NotRequired[Optional[str]]
    expires_at: NotRequired[datetime]


@dataclass
class QueuedNotificationModel(BaseModel):
    account_id: str
    channel: NotificationChannel
    payload: EmailNotificationPayload
    priority: NotificationPriority
    status: NotificationStatus
    expires_at: datetime
    id: Optional[ObjectId | str] = None
    max_retries: int = 5
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def to_bson(self) -> QueuedNotificationDocument:
        stored_payload = self.payload.redacted_for_storage()
        payload: EmailNotificationPayloadDocument = {
            "recipient_email": stored_payload.recipient_email,
            "sender_email": stored_payload.sender_email,
            "sender_name": stored_payload.sender_name,
            "template_id": stored_payload.template_id,
            "template_data": stored_payload.template_data,
        }
        doc: QueuedNotificationDocument = {
            "account_id": self.account_id,
            "channel": self.channel.value,
            "payload": payload,
            "priority": self.priority.value,
            "status": self.status.value,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "next_retry_at": self.next_retry_at,
            "sent_at": self.sent_at,
            "delivered_at": self.delivered_at,
            "error_message": self.error_message,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id if isinstance(self.id, ObjectId) else ObjectId(self.id)
        return doc

    @classmethod
    def from_bson(cls, bson_data: StoredDocument) -> "QueuedNotificationModel":
        expires_at = bson_data["expires_at"]
        payload_data = bson_data.get("payload") or {}
        payload = EmailNotificationPayload(
            recipient_email=payload_data.get("recipient_email", ""),
            sender_email=payload_data.get("sender_email", ""),
            sender_name=payload_data.get("sender_name", ""),
            template_id=payload_data.get("template_id", ""),
            template_data=payload_data.get("template_data"),
        )
        return cls(
            account_id=str(bson_data.get("account_id")),
            channel=NotificationChannel(bson_data.get("channel", NotificationChannel.EMAIL.value)),
            payload=payload,
            priority=NotificationPriority(bson_data.get("priority", NotificationPriority.NORMAL.value)),
            status=NotificationStatus(bson_data.get("status", NotificationStatus.PENDING.value)),
            expires_at=expires_at if expires_at.tzinfo is not None else expires_at.replace(tzinfo=UTC),
            id=bson_data.get("_id"),
            max_retries=bson_data.get("max_retries", 5),
            retry_count=bson_data.get("retry_count", 0),
            next_retry_at=cls._as_utc(bson_data.get("next_retry_at")),
            sent_at=cls._as_utc(bson_data.get("sent_at")),
            delivered_at=cls._as_utc(bson_data.get("delivered_at")),
            error_message=bson_data.get("error_message"),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)

    @staticmethod
    def get_collection_name() -> str:
        return "queued_notifications"
