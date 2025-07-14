from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class AccountNotificationPreferencesModel(BaseModel):
    account_id: str
    id: Optional[ObjectId | str] = None
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = True
    active: bool = True
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "AccountNotificationPreferencesModel":
        return cls(
            account_id=str(bson_data.get("account_id")),
            id=bson_data.get("_id"),
            email_enabled=bson_data.get("email_enabled", True),
            push_enabled=bson_data.get("push_enabled", True),
            sms_enabled=bson_data.get("sms_enabled", True),
            active=bson_data.get("active", True),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "account_notification_preferences"
