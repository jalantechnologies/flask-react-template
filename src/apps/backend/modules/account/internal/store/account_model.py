from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.account.types import NotificationPreferences, PhoneNumber
from modules.application.base_model import BaseModel


@dataclass
class AccountModel(BaseModel):

    first_name: str
    hashed_password: str
    id: Optional[ObjectId | str]
    last_name: str
    phone_number: Optional[PhoneNumber]
    username: str
    notification_preferences: Optional[NotificationPreferences] = None

    active: bool = True
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "AccountModel":
        phone_number_data = bson_data.get("phone_number")
        phone_number = PhoneNumber(**phone_number_data) if phone_number_data else None

        notification_prefs_data = bson_data.get("notification_preferences")
        notification_preferences = (
            NotificationPreferences(**notification_prefs_data) if notification_prefs_data else None
        )

        return cls(
            active=bson_data.get("active", True),
            first_name=bson_data.get("first_name", ""),
            hashed_password=bson_data.get("hashed_password", ""),
            id=bson_data.get("_id"),
            last_name=bson_data.get("last_name", ""),
            phone_number=phone_number,
            username=bson_data.get("username", ""),
            notification_preferences=notification_preferences,
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "accounts"
