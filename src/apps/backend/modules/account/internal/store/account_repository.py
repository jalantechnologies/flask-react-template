from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.account.internal.store.account_model import AccountModel
from modules.application.repository import ApplicationRepository
from modules.logger.logger import Logger

ACCOUNT_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["active", "created_at", "updated_at"],
        "properties": {
            "active": {"bsonType": "bool"},
            "first_name": {"bsonType": "string"},
            "hashed_password": {"bsonType": "string", "description": "must be a string"},
            "last_name": {"bsonType": "string"},
            "phone_number": {
                "bsonType": ["object", "null"],
                "properties": {"country_code": {"bsonType": "string"}, "phone_number": {"bsonType": "string"}},
                "description": "must be an object with country_code and phone_number",
            },
            "username": {"bsonType": "string", "description": "must be a string"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
        "anyOf": [{"required": ["username"]}, {"required": ["phone_number"]}],
    }
}


class AccountRepository(ApplicationRepository):
    collection_name = AccountModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index("username")
        collection.create_index([("active", 1), ("username", 1)], name="active_username_index")
        collection.create_index([("active", 1), ("phone_number", 1)], name="active_phone_number_index")

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": ACCOUNT_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:  # NamespaceNotFound MongoDB error code
                collection.database.create_collection(cls.collection_name, validator=ACCOUNT_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection accounts: {e.details}")
        return True
