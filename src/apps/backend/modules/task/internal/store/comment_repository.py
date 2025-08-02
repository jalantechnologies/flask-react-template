from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.logger.logger import Logger
from modules.task.internal.store.comment_model import CommentModel

COMMENT_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["task_id", "account_id", "content", "active", "created_at", "updated_at"],
        "properties": {
            "task_id": {"bsonType": "string"},
            "account_id": {"bsonType": "string"},
            "content": {"bsonType": "string"},
            "active": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class CommentRepository(ApplicationRepository):
    collection_name = CommentModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index(
            [("active", 1), ("task_id", 1)], name="active_task_id_index", partialFilterExpression={"active": True}
        )

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": COMMENT_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(cls.collection_name, validator=COMMENT_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection comments: {e.details}")
        return True

    def create_comment(self, comment_model: CommentModel) -> CommentModel:
        comment_data = comment_model.__dict__.copy()
        comment_data.pop("id", None)
        comment_data["created_at"] = datetime.now()
        comment_data["updated_at"] = datetime.now()

        result = self.collection.insert_one(comment_data)
        comment_data["_id"] = result.inserted_id

        return CommentModel.from_bson(comment_data)

    def get_comment_by_id(self, comment_id: str) -> Optional[CommentModel]:
        try:
            object_id = ObjectId(comment_id)
        except Exception:
            return None

        comment_data = self.collection.find_one({"_id": object_id, "active": True})
        if not comment_data:
            return None

        return CommentModel.from_bson(comment_data)

    def get_comments_by_task_id(self, task_id: str, skip: int = 0, limit: int = 10) -> List[CommentModel]:
        cursor = self.collection.find(
            {"task_id": task_id, "active": True}, sort=[("created_at", -1)], skip=skip, limit=limit
        )

        return [CommentModel.from_bson(comment_data) for comment_data in cursor]

    def update_comment(self, comment_id: str, update_data: dict) -> Optional[CommentModel]:
        try:
            object_id = ObjectId(comment_id)
        except Exception:
            return None

        update_data["updated_at"] = datetime.now()
        result = self.collection.update_one({"_id": object_id, "active": True}, {"$set": update_data})

        if result.modified_count == 0:
            return None

        return self.get_comment_by_id(comment_id)

    def delete_comment(self, comment_id: str) -> bool:
        try:
            object_id = ObjectId(comment_id)
        except Exception:
            return False

        result = self.collection.update_one(
            {"_id": object_id, "active": True}, {"$set": {"active": False, "updated_at": datetime.now()}}
        )

        return result.modified_count > 0

    def count_comments_by_task_id(self, task_id: str) -> int:
        return self.collection.count_documents({"task_id": task_id, "active": True})
