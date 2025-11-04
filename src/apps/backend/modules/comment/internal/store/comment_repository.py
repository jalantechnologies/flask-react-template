from datetime import datetime
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.application.common.types import PaginationParams
from modules.comment.internal.store.comment_model import CommentModel
from modules.logger.logger import Logger

COMMENT_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["task_id", "account_id", "author_name", "content", "active", "created_at", "updated_at"],
        "properties": {
            "task_id": {"bsonType": "string"},
            "account_id": {"bsonType": "string"},
            "author_name": {"bsonType": "string"},
            "content": {"bsonType": "string", "maxLength": 2000, "minLength": 1},
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
        collection.create_index(
            [("active", 1), ("account_id", 1)], name="active_account_id_index", partialFilterExpression={"active": True}
        )
        collection.create_index(
            [("task_id", 1), ("created_at", -1)], name="task_created_at_index"
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
        comment_dict = comment_model.to_bson()
        result = self.collection().insert_one(comment_dict)
        comment_dict["_id"] = result.inserted_id
        return CommentModel.from_bson(comment_dict)

    def get_comment_by_id(self, comment_id: str, account_id: str) -> CommentModel | None:
        comment_dict = self.collection().find_one({
            "_id": comment_id,
            "account_id": account_id,
            "active": True
        })
        return CommentModel.from_bson(comment_dict) if comment_dict else None

    def get_comments_for_task(self, task_id: str, account_id: str, pagination: PaginationParams) -> list[CommentModel]:
        query = {
            "task_id": task_id,
            "account_id": account_id,
            "active": True
        }
        cursor = self.collection().find(query).sort("created_at", -1).skip(pagination.offset).limit(pagination.size)
        return [CommentModel.from_bson(comment_dict) for comment_dict in cursor]

    def count_comments_for_task(self, task_id: str, account_id: str) -> int:
        return self.collection().count_documents({
            "task_id": task_id,
            "account_id": account_id,
            "active": True
        })

    def update_comment(self, comment_id: str, account_id: str, update_data: dict) -> CommentModel:
        update_data["updated_at"] = datetime.now()
        self.collection().update_one(
            {"_id": comment_id, "account_id": account_id, "active": True},
            {"$set": update_data}
        )
        comment_dict = self.collection().find_one({
            "_id": comment_id,
            "account_id": account_id,
            "active": True
        })
        return CommentModel.from_bson(comment_dict)

    def soft_delete_comment(self, comment_id: str, account_id: str) -> CommentModel:
        self.collection().update_one(
            {"_id": comment_id, "account_id": account_id, "active": True},
            {"$set": {"active": False, "updated_at": datetime.now()}}
        )
        comment_dict = self.collection().find_one({
            "_id": comment_id,
            "account_id": account_id
        })
        return CommentModel.from_bson(comment_dict)

    def get_comments_by_account_id(self, account_id: str, pagination: PaginationParams) -> list[CommentModel]:
        query = {
            "account_id": account_id,
            "active": True
        }
        cursor = self.collection().find(query).sort("created_at", -1).skip(pagination.offset).limit(pagination.size)
        return [CommentModel.from_bson(comment_dict) for comment_dict in cursor]