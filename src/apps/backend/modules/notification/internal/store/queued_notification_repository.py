from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.core.repository import ApplicationRepository, SortSpec, StoredDocument, StoreFilter
from modules.logger.logger import Logger
from modules.notification.internal.store.queued_notification_model import (
    QueuedNotificationDocument,
    QueuedNotificationModel,
)
from modules.notification.types import QueuedNotification, QueuedNotificationQuery

QUEUED_NOTIFICATION_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "account_id",
            "channel",
            "payload",
            "priority",
            "status",
            "max_retries",
            "retry_count",
            "expires_at",
            "created_at",
            "updated_at",
        ],
        "properties": {
            "account_id": {"bsonType": "string"},
            "channel": {"bsonType": "string"},
            "payload": {"bsonType": "object"},
            "priority": {"bsonType": "string"},
            "status": {"bsonType": "string"},
            "max_retries": {"bsonType": "int"},
            "retry_count": {"bsonType": "int"},
            "next_retry_at": {"bsonType": ["date", "null"]},
            "sent_at": {"bsonType": ["date", "null"]},
            "delivered_at": {"bsonType": ["date", "null"]},
            "error_message": {"bsonType": ["string", "null"]},
            "expires_at": {"bsonType": "date"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class QueuedNotificationRepository(ApplicationRepository[QueuedNotification, QueuedNotificationQuery]):
    collection_name = QueuedNotificationModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index(
            [("status", ASCENDING), ("priority", ASCENDING), ("next_retry_at", ASCENDING)],
            name="status_priority_next_retry_at_index",
        )
        collection.create_index(
            [("account_id", ASCENDING), ("created_at", ASCENDING)], name="account_id_created_at_index"
        )
        collection.create_index("expires_at", expireAfterSeconds=0, name="expires_at_ttl_index")

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": QUEUED_NOTIFICATION_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }
        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(
                    cls.collection_name, validator=QUEUED_NOTIFICATION_VALIDATION_SCHEMA
                )
            else:
                Logger.error(message=f"OperationFailure occurred for collection queued_notifications: {e.details}")
        return True

    @classmethod
    def from_doc(cls, doc: StoredDocument) -> QueuedNotification:
        model = QueuedNotificationModel.from_bson(doc)
        return QueuedNotification(
            account_id=model.account_id,
            channel=model.channel,
            payload=model.payload,
            priority=model.priority,
            status=model.status,
            expires_at=model.expires_at,
            id=str(model.id),
            max_retries=model.max_retries,
            retry_count=model.retry_count,
            next_retry_at=model.next_retry_at,
            sent_at=model.sent_at,
            delivered_at=model.delivered_at,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_doc(cls, entity: QueuedNotification) -> QueuedNotificationDocument:
        return QueuedNotificationModel(
            account_id=entity.account_id,
            channel=entity.channel,
            payload=entity.payload,
            priority=entity.priority,
            status=entity.status,
            expires_at=entity.expires_at,
            id=None,
            max_retries=entity.max_retries,
            retry_count=entity.retry_count,
            next_retry_at=entity.next_retry_at,
            sent_at=entity.sent_at,
            delivered_at=entity.delivered_at,
            error_message=entity.error_message,
        ).to_bson()

    @classmethod
    def _to_filter(cls, params: QueuedNotificationQuery) -> StoreFilter:
        store_filter: StoreFilter = {}
        if params.id is not None:
            object_id = cls._to_object_id(params.id)
            store_filter["_id"] = object_id if object_id is not None else {"$in": []}
        if params.account_id is not None:
            store_filter["account_id"] = params.account_id
        if params.statuses is not None:
            store_filter["status"] = {"$in": [status.value for status in params.statuses]}
        if params.due_before is not None:
            store_filter["next_retry_at"] = {"$lte": params.due_before}
        return store_filter

    @classmethod
    def _to_sort(cls, params: QueuedNotificationQuery) -> SortSpec:
        return [("priority", ASCENDING), ("next_retry_at", ASCENDING)]
