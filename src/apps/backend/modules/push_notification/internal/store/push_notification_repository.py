from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.logger.logger import Logger
from modules.application.repository import ApplicationRepository
from modules.push_notification.internal.store.push_notification_model import PushNotificationModel


PUSH_NOTIFICATION_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account_id", "title", "body", "device_token_ids", "status", "priority", "retry_count", "max_retries", "created_at", "updated_at"],
        "properties": {
            "account_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "body": {"bsonType": "string"},
            "device_token_ids": {"bsonType": "array"},
            "data": {"bsonType": ["object", "null"]},
            "status": {
                "bsonType": "string",
                "enum": ["pending", "processing", "sent", "delivered", "failed", "expired"]
            },
            "priority": {
                "bsonType": "string",
                "enum": ["immediate", "normal"]
            },
            "retry_count": {"bsonType": "int"},
            "max_retries": {"bsonType": "int"},
            "next_retry_at": {"bsonType": ["date", "null"]},
            "sent_at": {"bsonType": ["date", "null"]},
            "delivered_at": {"bsonType": ["date", "null"]},
            "error_message": {"bsonType": ["string", "null"]},
            "expires_at": {"bsonType": ["date", "null"]},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class PushNotificationRepository(ApplicationRepository):
    collection_name = PushNotificationModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index([("status", 1), ("priority", 1), ("next_retry_at", 1)], name="status_priority_next_retry_index")

        collection.create_index([
            ("account_id", 1),
            ("created_at", -1),],
            name="push_notification_created_at_index",
        )

        collection.create_index("expires_at", expireAfterSeconds=0, name="expires_at_ttl_index", sparse=True)

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": PUSH_NOTIFICATION_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(cls.collection_name, validator=PUSH_NOTIFICATION_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection push_notifications: {e.details}")

        return True
