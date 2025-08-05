from dataclasses import dataclass
from datetime import datetime

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class CommentModel(BaseModel):
    account_id: str
    task_id: str
    content: str
    active: bool = True
    id: ObjectId | str | None = None
    created_at: datetime | None = datetime.now()
    updated_at: datetime | None = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "CommentModel":
        return cls(
            id=bson_data.get("_id"),
            account_id=bson_data.get("account_id", ""),
            task_id=bson_data.get("task_id", ""),
            content=bson_data.get("content", ""),
            active=bson_data.get("active", True),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "comments"
