from typing import Optional

from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.core.repository import ApplicationRepository, SortSpec, StoredDocument, StoreFilter
from modules.logger.logger import Logger
from modules.task.internal.store.task_model import TaskModel
from modules.task.types import Task, TaskQuery

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


class TaskRepository(ApplicationRepository[Task, TaskQuery]):
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

    @classmethod
    def from_doc(cls, doc: StoredDocument) -> Task:
        model = TaskModel.from_bson(doc)
        return Task(
            account_id=model.account_id,
            created_at=model.created_at,
            description=model.description,
            id=str(model.id),
            title=model.title,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_doc(cls, entity: Task) -> StoredDocument:
        # The stored document carries fields the domain Task does not (active, timestamps); TaskModel
        # supplies their defaults. create() strips id/_id so MongoDB assigns a fresh ObjectId.
        return TaskModel(account_id=entity.account_id, description=entity.description, title=entity.title).to_bson()

    @classmethod
    def _to_filter(cls, params: TaskQuery) -> StoreFilter:
        store_filter: StoreFilter = {}
        if params.id is not None:
            object_id = cls._to_object_id(params.id)
            # A malformed id matches nothing; force an empty result rather than raising.
            store_filter["_id"] = object_id if object_id is not None else {"$in": []}
        if params.account_id is not None:
            store_filter["account_id"] = params.account_id
        if params.active is not None:
            store_filter["active"] = params.active
        return store_filter

    @classmethod
    def _to_sort(cls, params: TaskQuery) -> Optional[SortSpec]:
        # Default ordering for task listings: newest first, with _id as a stable tiebreaker.
        return [("created_at", -1), ("_id", -1)]
