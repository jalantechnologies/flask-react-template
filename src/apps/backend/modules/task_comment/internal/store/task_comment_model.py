from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class TaskCommentModel(BaseModel):
    """MongoDB model for task comments"""
    
    task_id: str
    account_id: str
    content: str
    created_at: Optional[datetime] = datetime.now()
    id: Optional[ObjectId | str] = None
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def from_bson(cls, bson_data: dict) -> "TaskCommentModel":
        """Convert MongoDB BSON document to TaskCommentModel"""
        return cls(
            task_id=bson_data.get("task_id", ""),
            account_id=bson_data.get("account_id", ""),
            content=bson_data.get("content", ""),
            created_at=bson_data.get("created_at"),
            id=bson_data.get("_id"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        """Get the MongoDB collection name"""
        return "task_comments"
    
    def to_domain_model(self) -> dict:
        """Convert to domain model (for use with Pydantic types)"""
        return {
            "id": str(self.id) if self.id else None,
            "task_id": self.task_id,
            "account_id": self.account_id,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }