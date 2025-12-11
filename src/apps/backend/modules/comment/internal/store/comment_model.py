from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from modules.application.common.base_model import BaseModel as AppBaseModel


class CommentModel(AppBaseModel):
    collection_name = "comments"

    account_id: str
    task_id: str
    content: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def get_collection_name(cls) -> str:
        return cls.collection_name
