from pymongo.collection import Collection
from pymongo.errors import OperationFailure
from bson import ObjectId
from typing import Optional, List

from modules.application.repository import ApplicationRepository
from modules.comment.internal.store.comment_model import CommentModel
from modules.logger.logger import Logger
from pymongo import ReturnDocument

COMMENT_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["task_id", "account_id", "content", "created_at", "updated_at"],
        "properties": {
            "task_id": {"bsonType": "string"},
            "account_id": {"bsonType": "string"},
            "content": {"bsonType": "string"},
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
            [("task_id", 1), ("account_id", 1)],
            name="task_account_index"
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
                collection.database.create_collection(
                    cls.collection_name,
                    validator=COMMENT_VALIDATION_SCHEMA
                )
            else:
                Logger.error(
                    message=f"OperationFailure occurred for collection comments: {e.details}"
                )
        return True