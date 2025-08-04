# Defines MongoDB document model for comments

# Desgin decisions:
# 1. Database schema
#   - task_id: Reference to parent task (Required)
#   - account_id: Denormalised account refrence (for performance and validation)
#   - content: comment text content (required, non-empty)
#   - active: Soft delete flag (follows task pattern for consistency)
#   - created_at: Comment creation tracking
#   - updated_at: comment upate timestamp
#
# 2. Field validation
#   - required fields enforeced at database level
#   - default values for active and timestamps
#   - BSON validation for data integrity
#
# Assumptions:
# - comments is stored as plain text only for now
# - Cross account collaboration is not required


from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from bson import ObjectId
from modules.application.base_model import BaseModel

@dataclass 
class CommentModel(BaseModel):
    task_id: str # parent task reference (required)
    account_id: str # comment owner (denormalised from task)
    content: str # comment text content (required)
    active: bool = True # soft delete flag
    created_at : Optional[datetime] = None # creation timestamp
    updated_at : Optional[datetime] = None # update timestamp
    id : Optional[ObjectId | str] = None # MongoDB primary key
    
    def __post_init__(self):
        if self.created_at is None:
            now = datetime.now()
            object.__setattr__(self, 'created_at', now)
            object.__setattr__(self, 'updated_at', now)
        elif self.updated_at is None:
            # if created_at is set, updated_at defaults to created_at
            object.__setattr__(self, 'updated_at', self.created_at)


    @classmethod
    def from_bson(cls, bson_data: dict) -> "CommentModel":
        return cls(
            task_id=bson_data.get("task_id", ""),
            account_id=bson_data.get("account_id", ""),
            content=bson_data.get("content", ""),
            active=bson_data.get("active", True),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
            id=bson_data.get("_id"),
        )


    @staticmethod
    def get_collection_name() -> str:
        return "comments"
# aashi.j@safe.security