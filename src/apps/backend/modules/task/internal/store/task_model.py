from dataclasses import dataclass
from typing import NotRequired, Optional

from bson import ObjectId

from modules.core.base_model import BaseModel, StoredDocument, StoredDocumentBase


class TaskDocument(StoredDocumentBase):
    account_id: NotRequired[str]
    description: NotRequired[str]
    title: NotRequired[str]
    active: NotRequired[bool]


@dataclass
class TaskModel(BaseModel):
    account_id: str
    description: str
    title: str
    active: bool = True
    id: Optional[ObjectId | str] = None

    def to_bson(self) -> TaskDocument:
        doc: TaskDocument = {
            "account_id": self.account_id,
            "description": self.description,
            "title": self.title,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id if isinstance(self.id, ObjectId) else ObjectId(self.id)
        return doc

    @classmethod
    def from_bson(cls, bson_data: StoredDocument) -> "TaskModel":
        return cls(
            account_id=bson_data.get("account_id", ""),
            active=bson_data.get("active", True),
            created_at=bson_data.get("created_at"),
            description=bson_data.get("description", ""),
            id=bson_data.get("_id"),
            title=bson_data.get("title", ""),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "tasks"
