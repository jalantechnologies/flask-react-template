from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.task.internal.store.task_model import TaskModel
from modules.logger.logger import Logger

TASK_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account_id", "description", "title", "active", "created_at", "updated_at"],
        "properties": {
            "account_id": {"bsonType": "string"},
            "description": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "active": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class TaskRepository(ApplicationRepository):
    collection_name = TaskModel.get_collection_name()

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
