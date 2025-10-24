from datetime import datetime
from typing import List, Optional

from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.comments.internal.store.comments_model import CommentModel
from modules.comments.types import Comment
from modules.logger.logger import Logger

COMMENT_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account_id", "task_id", "text", "created_at"],
        "properties": {
            "account_id": {"bsonType": "string"},
            "task_id": {"bsonType": "string"},
            "text": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class CommentRepository(ApplicationRepository):
    collection_name = CommentModel.get_collection_name()

    @classmethod
    def get_collection(cls) -> Collection:
        if not hasattr(cls, "db"):
            cls.client = MongoClient("mongodb://localhost:27017")
            cls.db = cls.client["my_database"]
        return cls.db[cls.collection_name]

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index([("account_id", 1), ("task_id", 1)], name="account_task_index")
        collection.create_index(
            [("account_id", 1), ("task_id", 1), ("created_at", -1)], name="account_task_created_at_index"
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

    @classmethod
    def add_comment(cls, comment: Comment) -> Comment:
        collection = cls.get_collection()

        comment_model = CommentModel(
            id=comment.id,
            account_id=comment.account_id,
            task_id=comment.task_id,
            text=comment.text,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

        collection.insert_one(comment_model.to_dict())
        return comment

    @classmethod
    def get_comments_by_task(cls, account_id: str, task_id: str) -> List[Comment]:
        collection = cls.get_collection()

        cursor = collection.find({"account_id": account_id, "task_id": task_id}).sort("created_at", -1)

        comments = []
        for doc in cursor:
            comment_model = CommentModel.from_dict(doc)
            comments.append(
                Comment(
                    id=comment_model.id,
                    account_id=comment_model.account_id,
                    task_id=comment_model.task_id,
                    text=comment_model.text,
                    created_at=comment_model.created_at,
                    updated_at=comment_model.updated_at,
                )
            )

        return comments

    # @classmethod
    # def get_comment_by_id(cls, account_id: str, task_id: str, comment_id: str) -> Optional[Comment]:
    #     collection = cls.get_collection()

    #     doc = collection.find_one({
    #         "_id": comment_id,
    #         "account_id": account_id,
    #         "task_id": task_id
    #     })

    #     if doc:
    #         comment_model = CommentModel.from_dict(doc)
    #         return Comment(
    #             id=comment_model.id,
    #             account_id=comment_model.account_id,
    #             task_id=comment_model.task_id,
    #             text=comment_model.text,
    #             created_at=comment_model.created_at,
    #             updated_at=comment_model.updated_at
    #         )
    #     return None

    @classmethod
    def update_comment(cls, account_id: str, task_id: str, comment_id: str, text: str) -> Optional[Comment]:
        collection = cls.get_collection()

        result = collection.find_one_and_update(
            {"_id": comment_id, "account_id": account_id, "task_id": task_id},
            {"$set": {"text": text, "updated_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )

        if result:
            comment_model = CommentModel.from_dict(result)
            return Comment(
                id=comment_model.id,
                account_id=comment_model.account_id,
                task_id=comment_model.task_id,
                text=comment_model.text,
                created_at=comment_model.created_at,
                updated_at=comment_model.updated_at,
            )
        return None

    @classmethod
    def delete_comment(cls, account_id: str, task_id: str, comment_id: str) -> bool:
        collection = cls.get_collection()

        result = collection.delete_one({"_id": comment_id, "account_id": account_id, "task_id": task_id})

        return result.deleted_count > 0

    # @classmethod
    # def get_comments_count(cls, account_id: str, task_id: str) -> int:
    #     """Get the count of comments for a task"""
    #     collection = cls.get_collection()

    #     return collection.count_documents({
    #         "account_id": account_id,
    #         "task_id": task_id
    #     })
