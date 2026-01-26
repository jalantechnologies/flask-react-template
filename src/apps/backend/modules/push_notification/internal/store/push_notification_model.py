from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel
from modules.push_notification.types import NotificationStatus, Priority


@dataclass
class PushNotificationModel(BaseModel):
    account_id: str
    title: str
    body: str
    device_token_ids: list[ObjectId]
    data: Optional[dict]
    status: NotificationStatus = NotificationStatus.PENDING
    priority: Priority = Priority.NORMAL
    retry_count: int = 0
    max_retries: int = 4
    next_retry_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = datetime.now()
    id: Optional[ObjectId | str] = None
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "PushNotificationModel":

        return cls(
            account_id=bson_data.get("account_id", ""),
            title=bson_data.get("title", ""),
            body=bson_data.get("body", ""),
            data=bson_data.get("data"),
            device_token_ids=bson_data.get("device_token_ids", []),
            status=NotificationStatus(bson_data.get("status", "pending")),
            priority=Priority(bson_data.get("priority", "normal")),
            retry_count=bson_data.get("retry_count", 0),
            max_retries=bson_data.get("max_retries", 4),
            next_retry_at=bson_data.get("next_retry_at"),
            sent_at=bson_data.get("sent_at"),
            delivered_at=bson_data.get("delivered_at"),
            error_message=bson_data.get("error_message"),
            expires_at=bson_data.get("expires_at"),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
            id=bson_data.get("_id"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "push_notifications"
