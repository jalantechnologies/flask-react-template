from dataclasses import dataclass
from typing import Optional, Any, Dict
from bson import ObjectId


@dataclass
class CommentModel:
    """
    Represents a Comment document stored in MongoDB.
    """

    id: Optional[ObjectId] = None
    task_id: str = ""
    body: str = ""
    author: Optional[str] = None
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None

    @staticmethod
    def get_collection_name() -> str:
        """Collection name for storing comments."""
        return "comments"

    def to_bson(self) -> Dict[str, Any]:
        """
        Convert model to MongoDB compatible dictionary.
        """
        data = {
            "task_id": self.task_id,
            "body": self.body,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        if self.id:
            data["_id"] = ObjectId(str(self.id))

        return data

    @staticmethod
    def from_bson(document: Dict[str, Any]) -> "CommentModel":
        """
        Convert MongoDB document into CommentModel.
        """
        if not document:
            return None

        return CommentModel(
            id=document.get("_id"),
            task_id=document.get("task_id"),
            body=document.get("body"),
            author=document.get("author"),
            created_at=document.get("created_at"),
            updated_at=document.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model into dictionary for API responses.
        Converts ObjectId to string for serialization.
        """
        return {
            "id": str(self.id) if self.id else None,
            "task_id": self.task_id,
            "body": self.body,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
