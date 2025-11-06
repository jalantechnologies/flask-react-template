from datetime import datetime
from typing import Any, Optional
from bson import ObjectId

from modules.application.repository import ApplicationRepository
from .comment_model import CommentModel


class CommentRepository(ApplicationRepository):
    """
    Repository responsible for CRUD operations for comments in MongoDB.
    Interacts directly with the database and returns CommentModel objects.
    """

    @property
    def collection_name(self) -> str:
        """Defines the MongoDB collection for comments."""
        return CommentModel.get_collection_name()

    def create(self, model: CommentModel) -> CommentModel:
        """Insert a new comment into MongoDB."""
        data = model.to_bson()

        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()

        inserted_id = self.collection(self.collection_name).insert_one(data).inserted_id
        model.id = inserted_id
        return model

    def find_by_id(self, _id: str | ObjectId) -> Optional[CommentModel]:
        """Find a comment by ID."""
        document = self.collection(self.collection_name).find_one({"_id": ObjectId(str(_id))})
        return CommentModel.from_bson(document) if document else None

    def list_for_task(self, task_id: str) -> list[CommentModel]:
        """List all comments for a given task."""
        cursor = (
            self.collection(self.collection_name)
            .find({"task_id": task_id})
            .sort("created_at", -1)
        )
        return [CommentModel.from_bson(doc) for doc in cursor]

    def update(self, _id: str | ObjectId, fields: dict[str, Any]) -> Optional[CommentModel]:
        """Update comment fields and return the updated model."""
        fields["updated_at"] = datetime.utcnow()
        self.collection(self.collection_name).update_one(
            {"_id": ObjectId(str(_id))},
            {"$set": fields}
        )
        return self.find_by_id(_id)

    def delete(self, _id: str | ObjectId) -> bool:
        """Delete a comment by ID."""
        result = self.collection(self.collection_name).delete_one({"_id": ObjectId(str(_id))})
        return result.deleted_count == 1