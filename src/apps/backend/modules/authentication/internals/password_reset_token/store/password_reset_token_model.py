from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class PasswordResetTokenModel(BaseModel):

    account: ObjectId | str
    expires_at: datetime
    id: Optional[ObjectId | str]
    token: str

    is_used: bool = False

    @classmethod
    def from_bson(cls, bson_data: dict) -> "PasswordResetTokenModel":
        return cls(
            account=bson_data.get("account"),
            expires_at=bson_data.get("expires_at", ""),
            id=bson_data.get("_id"),
            is_used=bson_data.get("is_used", ""),
            token=bson_data.get("token", ""),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "password_reset_tokens"
