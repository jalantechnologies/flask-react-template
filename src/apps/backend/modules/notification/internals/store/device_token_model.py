from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel
from modules.notification.types import DeviceType


@dataclass
class DeviceTokenModel(BaseModel):
    device_type: DeviceType
    id: Optional[ObjectId | str]
    token: str
    account_id: str
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "DeviceTokenModel":
        device_type_str = bson_data.get("device_type", "")
        try:
            device_type = DeviceType(device_type_str)
        except ValueError:
            device_type = DeviceType.ANDROID

        return cls(
            device_type=device_type,
            id=bson_data.get("_id"),
            token=bson_data.get("token", ""),
            account_id=bson_data.get("account_id", ""),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    def to_bson(self) -> dict:
        data = super().to_bson()
        if isinstance(data["device_type"], DeviceType):
            data["device_type"] = data["device_type"].value
        return data

    @staticmethod
    def get_collection_name() -> str:
        return "device_tokens"
