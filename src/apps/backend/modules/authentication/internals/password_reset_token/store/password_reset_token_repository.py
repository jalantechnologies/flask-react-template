from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository
from modules.authentication.internals.password_reset_token.store.password_reset_token_model import (
    PasswordResetTokenModel,
)
from modules.logger.logger import Logger

PASSWORD_RESET_TOKEN_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account", "expires_at", "token", "is_used"],
        "properties": {
            "account": {"bsonType": "objectId", "description": "must be an ObjectId and is required"},
            "expires_at": {"bsonType": "date", "description": "must be a valid date and is required"},
            "is_used": {"bsonType": "bool", "description": "must be a boolean and is required"},
            "token": {"bsonType": "string", "description": "must be a string and is required"},
            "_id": {"bsonType": "objectId", "description": "must be an ObjectId"},
        },
    }
}


class PasswordResetTokenRepository(ApplicationRepository):
    collection_name = PasswordResetTokenModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index("token")
        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": PASSWORD_RESET_TOKEN_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }
        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:  # NamespaceNotFound MongoDB error code
                collection.database.create_collection(
                    cls.collection_name, validator=PASSWORD_RESET_TOKEN_VALIDATION_SCHEMA
                )
            else:
                Logger.error(message=f"OperationFailure occurred for collection PasswordResetToken: {e.details}")
        return True
