from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.logger.logger import Logger
from modules.notification.internal.store.fcm_token_model import FCMTokenModel

FCM_TOKEN_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["user_id", "fcm_token", "active", "created_at", "updated_at"],
        "properties": {
            "user_id": {"bsonType": "string"},
            "fcm_token": {"bsonType": "string"},
            "device_info": {"bsonType": ["string", "null"]},
            "active": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
            "_id": {"bsonType": "objectId"},
        },
    }
}


class FCMTokenRepository(ApplicationRepository):
    collection_name = FCMTokenModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index("user_id")
        collection.create_index("fcm_token", unique=True)
        collection.create_index([("user_id", 1), ("active", 1)])

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": FCM_TOKEN_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(cls.collection_name, validator=FCM_TOKEN_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection fcm_tokens: {e.details}")
        return True
