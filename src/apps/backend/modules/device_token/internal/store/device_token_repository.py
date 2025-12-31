from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.device_token.internal.store.device_token_model import DeviceTokenModel
from modules.logger.logger import Logger

DEVICE_TOKEN_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account_id", "device_token", "platform", "active", "created_at", "updated_at"],
        "properties": {
            "account_id": {"bsonType": "string"},
            "device_token": {"bsonType": "string"},
            "platform": {
                "bsonType": "string",
                "enum": ["android", "ios", "web"]
            },
            "device_info": {"bsonType": ["object", "null"]},
            "active": {"bsonType": "bool"},
            "last_used_at": {"bsonType": ["date", "null"]},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class DeviceTokenRepository(ApplicationRepository):
    collection_name = DeviceTokenModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index([("device_token", 1)],  unique=True, name="device_token_unique_index")

        collection.create_index(
            [("account_id", 1), ("active", 1)], name="account_id_active_index", partialFilterExpression={"active": True}
        )

        collection.create_index("last_used_at", expireAfterSeconds=30 * 24 * 60 * 60, name="last_used_at_ttl_index", sparse=True)

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
