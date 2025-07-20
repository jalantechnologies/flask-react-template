from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class DeviceTokenModel(BaseModel):
    app_version: Optional[str]
    device_type: str
    id: Optional[ObjectId | str]
    token: str
    user_id: str
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "DeviceTokenModel":
        return cls(
            app_version=bson_data.get("app_version"),
            device_type=bson_data.get("device_type", ""),
            id=bson_data.get("_id"),
            token=bson_data.get("token", ""),
            user_id=bson_data.get("user_id", ""),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "device_tokens"
