from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.notification.internals.store.account_notification_preferences_model import (
    AccountNotificationPreferencesModel,
)
from modules.application.repository import ApplicationRepository
from modules.logger.logger import Logger

ACCOUNT_NOTIFICATION_PREFERENCES_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "account_id",
            "email_enabled",
            "push_enabled",
            "sms_enabled",
            "active",
            "created_at",
            "updated_at",
        ],
        "properties": {
            "account_id": {"bsonType": "string"},
            "email_enabled": {"bsonType": "bool"},
            "push_enabled": {"bsonType": "bool"},
            "sms_enabled": {"bsonType": "bool"},
            "active": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class AccountNotificationPreferencesRepository(ApplicationRepository):
    collection_name = AccountNotificationPreferencesModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index(
            [("active", 1), ("account_id", 1)],
            unique=True,
            partialFilterExpression={"active": True},
            name="active_account_id_unique",
        )

        collection.create_index("account_id", name="account_id_index")

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
