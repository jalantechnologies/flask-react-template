from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId

from modules.api_key.types import ApiKeyKind, ApiKeyStatus
from modules.application.base_model import BaseModel


@dataclass
class ApiKeyModel(BaseModel):
    account_id: str
    name: str
    key_hash: str
    status: ApiKeyStatus
    kind: ApiKeyKind = ApiKeyKind.USER
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    id: Optional[ObjectId | str] = None

    @classmethod
    def from_bson(cls, bson_data: dict[str, Any]) -> "ApiKeyModel":
        return cls(
            account_id=bson_data.get("account_id", ""),
            name=bson_data.get("name", ""),
            key_hash=bson_data.get("key_hash", ""),
            status=ApiKeyStatus(bson_data.get("status", ApiKeyStatus.ACTIVE.value)),
            kind=ApiKeyKind(bson_data.get("kind", ApiKeyKind.USER.value)),
            expires_at=bson_data.get("expires_at"),
            last_used_at=bson_data.get("last_used_at"),
            id=bson_data.get("_id"),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "api_keys"
