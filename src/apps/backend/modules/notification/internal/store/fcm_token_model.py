from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class FCMTokenModel(BaseModel):
    """MongoDB model for FCM tokens"""

    id: Optional[ObjectId | str]
    user_id: str
    fcm_token: str
    device_info: Optional[str]
    active: bool
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "FCMTokenModel":
        return cls(
            id=bson_data.get("_id"),
            user_id=bson_data.get("user_id", ""),
            fcm_token=bson_data.get("fcm_token", ""),
            device_info=bson_data.get("device_info"),
            active=bson_data.get("active", True),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "fcm_tokens"
