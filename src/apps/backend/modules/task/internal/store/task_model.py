from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

from attrs import field

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class TaskModel(BaseModel):
    account_id: str
    description: str
    title: str
    active: bool = True
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    comments: List[Dict[str, Union[str, datetime]]] = field(default_factory=list)

    @classmethod
    def from_bson(cls, bson_data: dict) -> "TaskModel":
        return cls(
            account_id=bson_data.get("account_id", ""),
            active=bson_data.get("active", True),
            created_at=bson_data.get("created_at"),
            description=bson_data.get("description", ""),
            id=bson_data.get("_id"),
            title=bson_data.get("title", ""),
            updated_at=bson_data.get("updated_at"),
            comments=bson_data.get("comments", []),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "tasks"
