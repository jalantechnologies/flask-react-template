from dataclasses import dataclass
from datetime import datetime
from typing import NotRequired, Optional

from bson import ObjectId

from modules.core.base_model import BaseModel, StoredDocument, StoredDocumentBase


class PasswordResetTokenDocument(StoredDocumentBase):
    account: ObjectId
    expires_at: datetime
    is_used: NotRequired[bool]
    token: NotRequired[str]


@dataclass
class PasswordResetTokenModel(BaseModel):

    account: ObjectId | str
    expires_at: datetime
    id: Optional[ObjectId | str]
    token: str

    is_used: bool = False

    def to_bson(self) -> PasswordResetTokenDocument:
        doc: PasswordResetTokenDocument = {
            "account": self.account if isinstance(self.account, ObjectId) else ObjectId(self.account),
            "expires_at": self.expires_at,
            "is_used": self.is_used,
            "token": self.token,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id if isinstance(self.id, ObjectId) else ObjectId(self.id)
        return doc

    @classmethod
    def from_bson(cls, bson_data: StoredDocument) -> "PasswordResetTokenModel":
        return cls(
            account=bson_data["account"],
            created_at=bson_data.get("created_at"),
            expires_at=bson_data["expires_at"],
            id=bson_data.get("_id"),
            is_used=bson_data.get("is_used", False),
            token=bson_data.get("token", ""),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "password_reset_tokens"
