from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.core.common.types import JobRun, JobRunQuery
from modules.core.internal.job_run.store.job_run_model import JobRunDocument, JobRunModel
from modules.core.repository import ApplicationRepository, StoredDocument, StoreFilter
from modules.logger.logger import Logger

JOB_RUN_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["job_name", "status", "retry_count", "created_at", "updated_at"],
        "properties": {
            "job_name": {"bsonType": "string"},
            "status": {"bsonType": "string"},
            "arguments": {"bsonType": "object"},
            "retry_count": {"bsonType": "int"},
            "started_at": {"bsonType": ["date", "null"]},
            "ended_at": {"bsonType": ["date", "null"]},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class JobRunRepository(ApplicationRepository[JobRun, JobRunQuery]):
    collection_name = JobRunModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index([("job_name", ASCENDING), ("started_at", DESCENDING)], name="job_name_started_at_index")
        collection.create_index([("status", ASCENDING)], name="status_index")

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": JOB_RUN_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }
        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(cls.collection_name, validator=JOB_RUN_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection job_run: {e.details}")
        return True

    @classmethod
    def from_doc(cls, doc: StoredDocument) -> JobRun:
        model = JobRunModel.from_bson(doc)
        return JobRun(
            id=str(model.id),
            job_name=model.job_name,
            status=model.status,
            arguments=model.arguments,
            retry_count=model.retry_count,
            started_at=model.started_at,
            ended_at=model.ended_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_doc(cls, entity: JobRun) -> JobRunDocument:
        return JobRunModel(
            job_name=entity.job_name,
            status=entity.status,
            id=None,
            arguments=entity.arguments,
            retry_count=entity.retry_count,
            started_at=entity.started_at,
            ended_at=entity.ended_at,
        ).to_bson()

    @classmethod
    def _to_filter(cls, params: JobRunQuery) -> StoreFilter:
        store_filter: StoreFilter = {}
        if params.id is not None:
            object_id = cls._to_object_id(params.id)
            store_filter["_id"] = object_id if object_id is not None else {"$in": []}
        if params.job_name is not None:
            store_filter["job_name"] = params.job_name
        if params.status is not None:
            store_filter["status"] = params.status.value
        return store_filter
