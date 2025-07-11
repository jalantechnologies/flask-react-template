from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.notification.internals.store.account_notification_preferences_model import AccountNotificationPreferencesModel
from modules.application.repository import ApplicationRepository
from modules.logger.logger import Logger

BOOLEAN_REQUIRED_DESCRIPTION = "must be a boolean and is required"
DATE_REQUIRED_DESCRIPTION = "must be a valid date"
OBJECT_ID_REQUIRED_DESCRIPTION = "must be an ObjectId and is required"

ACCOUNT_NOTIFICATION_PREFERENCES_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account_id", "email_enabled", "push_enabled", "sms_enabled", "created_at", "updated_at"],
        "properties": {
            "account_id": {"bsonType": "string", "description": OBJECT_ID_REQUIRED_DESCRIPTION},
            "email_enabled": {"bsonType": "bool", "description": BOOLEAN_REQUIRED_DESCRIPTION},
            "push_enabled": {"bsonType": "bool", "description": BOOLEAN_REQUIRED_DESCRIPTION},
            "sms_enabled": {"bsonType": "bool", "description": BOOLEAN_REQUIRED_DESCRIPTION},
            "created_at": {"bsonType": "date", "description": DATE_REQUIRED_DESCRIPTION},
            "updated_at": {"bsonType": "date", "description": DATE_REQUIRED_DESCRIPTION},
        },
    }
}


class AccountNotificationPreferencesRepository(ApplicationRepository):
    collection_name = AccountNotificationPreferencesModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index("account_id", unique=True)

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": ACCOUNT_NOTIFICATION_PREFERENCES_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(
                    cls.collection_name, validator=ACCOUNT_NOTIFICATION_PREFERENCES_VALIDATION_SCHEMA
                )
            else:
                Logger.error(
                    message=f"OperationFailure occurred for collection account_notification_preferences: {e.details}"
                )
        return True
