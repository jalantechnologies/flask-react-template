from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel
from modules.device_token.types import Platform


@dataclass
class DeviceTokenModel(BaseModel):
    account_id: str
    device_token: str
    platform: Platform
    device_info: Optional[dict] = None
    active: bool = True
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = datetime.now()
    id: Optional[ObjectId | str] = None
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "DeviceTokenModel":

        return cls(
            account_id=bson_data.get("account_id", ""),
            device_token=bson_data.get("device_token", ""),
            platform=bson_data.get("platform", ""),
            active=bson_data.get("active", True),
            device_info=bson_data.get("device_info"),
            last_used_at=bson_data.get("last_used_at"),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
            id=bson_data.get("_id"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "device_tokens"
