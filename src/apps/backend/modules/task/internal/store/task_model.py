from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class TaskModel(BaseModel):
    account_id: str
    description: str
    title: str
    id: Optional[ObjectId | str] = None
    active: bool = True
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "TaskModel":
        return cls(
            account_id=str(bson_data.get("account_id", "")),
            description=bson_data.get("description", ""),
            title=bson_data.get("title", ""),
            id=bson_data.get("_id"),
            active=bson_data.get("active", True),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "tasks"
