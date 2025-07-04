from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.logger.logger import Logger
from modules.notification.internals.store.device_token_model import DeviceTokenModel

STRING_REQUIRED = "must be a string and is required"
STRING_OPTIONAL = "must be a string if present"
DATE_REQUIRED = "must be a date and is required"
DATE_OPTIONAL = "must be a date"

DEVICE_TOKEN_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["token", "user_id", "device_type", "last_active"],
        "properties": {
            "token": {"bsonType": "string", "description": STRING_REQUIRED},
            "user_id": {"bsonType": "string", "description": STRING_REQUIRED},
            "device_type": {"bsonType": "string", "description": STRING_REQUIRED},
            "app_version": {"bsonType": "string", "description": STRING_OPTIONAL},
            "last_active": {"bsonType": "date", "description": DATE_REQUIRED},
            "created_at": {"bsonType": "date", "description": DATE_OPTIONAL},
            "updated_at": {"bsonType": "date", "description": DATE_OPTIONAL},
        },
    }
}


class DeviceTokenRepository(ApplicationRepository):
    collection_name = DeviceTokenModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index("token", unique=True)
        collection.create_index("user_id")
        collection.create_index("last_active")

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": DEVICE_TOKEN_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(cls.collection_name, validator=DEVICE_TOKEN_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection device_tokens: {e.details}")
        return True
