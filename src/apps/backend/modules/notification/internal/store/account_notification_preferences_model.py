from dataclasses import dataclass
from typing import NotRequired, Optional

from bson import ObjectId

from modules.core.base_model import BaseModel, StoredDocument, StoredDocumentBase


class AccountNotificationPreferencesDocument(StoredDocumentBase):
    account_id: NotRequired[str]
    email_enabled: NotRequired[bool]
    push_enabled: NotRequired[bool]
    sms_enabled: NotRequired[bool]
    active: NotRequired[bool]


@dataclass
class AccountNotificationPreferencesModel(BaseModel):
    account_id: str
    id: Optional[ObjectId | str] = None
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = True
    active: bool = True

    def to_bson(self) -> AccountNotificationPreferencesDocument:
        doc: AccountNotificationPreferencesDocument = {
            "account_id": self.account_id,
            "email_enabled": self.email_enabled,
            "push_enabled": self.push_enabled,
            "sms_enabled": self.sms_enabled,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id if isinstance(self.id, ObjectId) else ObjectId(self.id)
        return doc

    @classmethod
    def from_bson(cls, bson_data: StoredDocument) -> "AccountNotificationPreferencesModel":
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
