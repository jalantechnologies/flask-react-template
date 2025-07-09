from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class DeviceTokenModel(BaseModel):
    token: str
    user_id: str
    device_type: str
    app_version: Optional[str]
    last_active: datetime
    id: Optional[ObjectId | str]
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "DeviceTokenModel":
        return cls(
            id=bson_data.get("_id"),
            token=bson_data.get("token", ""),
            user_id=bson_data.get("user_id", ""),
            device_type=bson_data.get("device_type", ""),
            app_version=bson_data.get("app_version"),
            last_active=bson_data.get("last_active", datetime.now()),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "device_tokens"
