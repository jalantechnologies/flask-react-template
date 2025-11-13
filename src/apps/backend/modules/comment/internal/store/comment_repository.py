from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.comment.internal.store.comment_model import CommentModel
from modules.logger.logger import Logger


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
        # Create indexes for efficient queries
        collection.create_index(
            [("active", 1), ("task_id", 1), ("account_id", 1)],
            name="active_task_account_index",
            partialFilterExpression={"active": True}
        )
        
        # Create index for task_id queries
        collection.create_index(
            [("task_id", 1), ("created_at", -1)],
            name="task_id_created_at_index"
        )

        # Add validation schema
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

    @classmethod
    def create(cls, comment: CommentModel) -> CommentModel:
        """Create a new comment"""
        collection = cls.get_collection()
        
        comment_dict = {
            "task_id": comment.task_id,
            "account_id": comment.account_id,
            "content": comment.content,
            "active": comment.active,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
        }
        
        result = collection.insert_one(comment_dict)
        comment.id = result.inserted_id
        return comment

    @classmethod
    def find_by_task_id(cls, task_id: str, account_id: str) -> List[CommentModel]:
        """Get all comments for a task"""
        collection = cls.get_collection()
        
        comments = collection.find({
            "task_id": task_id,
            "account_id": account_id,
            "active": True
        }).sort("created_at", -1)  # Most recent first
        
        return [CommentModel.from_bson(comment) for comment in comments]

    @classmethod
    def find_by_id(cls, comment_id: str, account_id: str) -> Optional[CommentModel]:
        """Get a single comment by ID"""
        collection = cls.get_collection()
        
        comment = collection.find_one({
            "_id": ObjectId(comment_id),
            "account_id": account_id,
            "active": True
        })
        
        return CommentModel.from_bson(comment) if comment else None

    @classmethod
    def update(cls, comment_id: str, account_id: str, content: str) -> Optional[CommentModel]:
        """Update a comment"""
        collection = cls.get_collection()
        
        result = collection.find_one_and_update(
            {"_id": ObjectId(comment_id), "account_id": account_id, "active": True},
            {"$set": {"content": content, "updated_at": datetime.now()}},
            return_document=True
        )
        
        return CommentModel.from_bson(result) if result else None

    @classmethod
    def delete(cls, comment_id: str, account_id: str) -> bool:
        """Soft delete a comment"""
        collection = cls.get_collection()
        
        result = collection.update_one(
            {"_id": ObjectId(comment_id), "account_id": account_id},
            {"$set": {"active": False, "updated_at": datetime.now()}}
        )
        
        return result.modified_count > 0