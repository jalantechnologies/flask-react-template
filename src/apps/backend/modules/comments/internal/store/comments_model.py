from datetime import datetime
from typing import Optional


class CommentModel:
    @staticmethod
    def get_collection_name() -> str:
        return "comments"

    @staticmethod
    def from_dict(data: dict) -> "CommentModel":
        return CommentModel(
            id=str(data["_id"]),
            account_id=data["account_id"],
            task_id=data["task_id"],
            text=data["text"],
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
        )

    def __init__(
        self,
        id: str,
        account_id: str,
        task_id: str,
        text: str,
        created_at: datetime,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.account_id = account_id
        self.task_id = task_id
        self.text = text
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "account_id": self.account_id,
            "task_id": self.task_id,
            "text": self.text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
