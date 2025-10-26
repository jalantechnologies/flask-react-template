from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class CommentModel(BaseModel):
    account_id: str
    text: str
    task_id: str
    created_at: Optional[datetime] = datetime.now()
    id: Optional[ObjectId | str] = None
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "TaskModel":
        return cls(
            account_id=bson_data.get("account_id", ""),
            task_id=bson_data.get("task_id", ""),
            created_at=bson_data.get("created_at"),
            text=bson_data.get("text", ""),
            id=bson_data.get("_id"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "comments"
