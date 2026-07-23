from typing import Any, ClassVar, Optional

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.common.types import AuditLogEntry
from modules.application.internal.audit.store.audit_log_model import AuditLogModel
from modules.application.repository_client import ApplicationRepositoryClient
from modules.logger.logger import Logger

AUDIT_LOG_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "resource_type",
            "resource_id",
            "actor_type",
            "actor_id",
            "action",
            "timestamp",
            "created_at",
            "updated_at",
        ],
        "properties": {
            "resource_type": {"bsonType": "string"},
            "resource_id": {"bsonType": "string"},
            "actor_type": {"bsonType": "string"},
            "actor_id": {"bsonType": ["string", "null"]},
            "action": {"bsonType": "string"},
            "timestamp": {"bsonType": "date"},
            "changes": {"bsonType": "object"},
            "outcome": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class AuditLogRepository:
    """Append-only store for the audit trail. Deliberately not an ApplicationRepository: the base
    repository emits an audit entry on every write, so routing the audit write back through it would
    recurse. The trail is write-only here, so it needs only an insert."""

    collection_name = AuditLogModel.get_collection_name()

    _collection: ClassVar[Optional[Collection]] = None

    @classmethod
    def collection(cls) -> Collection:
        if cls._collection is None:
            database = ApplicationRepositoryClient.get_client().get_database()
            collection = database[cls.collection_name]
            cls._init_collection(collection)
            cls._collection = collection
        return cls._collection

    @classmethod
    def _init_collection(cls, collection: Collection) -> None:
        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": AUDIT_LOG_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }
        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(cls.collection_name, validator=AUDIT_LOG_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection audit_log: {e.details}")

        collection.create_index([("resource_type", ASCENDING), ("resource_id", ASCENDING), ("timestamp", ASCENDING)])
        collection.create_index([("actor_type", ASCENDING), ("actor_id", ASCENDING), ("timestamp", ASCENDING)])

    @classmethod
    def create(cls, entity: AuditLogEntry) -> AuditLogEntry:
        doc = cls._to_doc(entity)
        result = cls.collection().insert_one(doc)
        return cls._from_doc({**doc, "_id": result.inserted_id})

    @classmethod
    def create_many(cls, entities: list[AuditLogEntry]) -> list[AuditLogEntry]:
        # One round trip for a batch of entries so a multi-document read audits in a single insert
        # rather than one per document (see AGENTS.md §13 on N+1 access).
        docs = [cls._to_doc(entity) for entity in entities]
        result = cls.collection().insert_many(docs)
        return [cls._from_doc({**doc, "_id": inserted_id}) for doc, inserted_id in zip(docs, result.inserted_ids)]

    @classmethod
    def _to_doc(cls, entity: AuditLogEntry) -> dict[str, Any]:
        doc = AuditLogModel(
            resource_type=entity.resource_type,
            resource_id=entity.resource_id,
            actor_type=entity.actor_type,
            actor_id=entity.actor_id,
            action=entity.action,
            timestamp=entity.timestamp,
            changes=entity.changes,
            outcome=entity.outcome,
        ).to_bson()
        doc.pop("id", None)
        doc.pop("_id", None)
        doc["action"] = entity.action.value
        doc["actor_type"] = entity.actor_type.value
        doc["outcome"] = entity.outcome.value
        doc["changes"] = {name: {"old": change.old, "new": change.new} for name, change in entity.changes.items()}
        return doc

    @classmethod
    def _from_doc(cls, doc: dict[str, Any]) -> AuditLogEntry:
        model = AuditLogModel.from_bson(doc)
        return AuditLogEntry(
            id=str(model.id),
            resource_type=model.resource_type,
            resource_id=model.resource_id,
            actor_type=model.actor_type,
            actor_id=model.actor_id,
            action=model.action,
            timestamp=model.timestamp,
            changes=model.changes,
            outcome=model.outcome,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
