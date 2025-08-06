from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class CommentModel(BaseModel):
    task_id: str
    account_id: str
    content: str
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    id: Optional[ObjectId | str] = None

    @classmethod
    def from_bson(cls, bson_data: dict) -> "CommentModel":
        return cls(
            task_id=bson_data.get("task_id", ""),
            account_id=bson_data.get("account_id", ""),
            content=bson_data.get("content", ""),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
            id=bson_data.get("_id"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "comments"
