from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.logger.logger import Logger
from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.types import DeviceType

DEVICE_TOKEN_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["token", "account_id", "device_type"],
        "properties": {
            "device_type": {
                "bsonType": "string",
                "enum": [DeviceType.ANDROID.value, DeviceType.IOS.value],
                "description": "must be either 'android' or 'ios'",
            },
            "token": {"bsonType": "string"},
            "account_id": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class DeviceTokenRepository(ApplicationRepository):
    collection_name = DeviceTokenModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index("token", unique=True)
        collection.create_index("account_id")

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
