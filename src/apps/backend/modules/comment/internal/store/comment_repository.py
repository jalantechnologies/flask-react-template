from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.comment.internal.store.comment_model import CommentModel
from modules.logger.logger import Logger

TASK_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account_id", "text", "created_at", "updated_at"],
        "properties": {
            "account_id": {"bsonType": "string"},
            "text": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
            "task_id": {"bsonType": "string"},
        },
    }
}


class CommentRepository(ApplicationRepository):
    collection_name = CommentModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index(
            [("active", 1), ("account_id", 1)], name="active_account_id_index", partialFilterExpression={"active": True}
        )

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": TASK_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(cls.collection_name, validator=TASK_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection tasks: {e.details}")
        return True
