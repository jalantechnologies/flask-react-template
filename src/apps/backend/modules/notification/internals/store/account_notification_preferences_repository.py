from datetime import UTC, datetime

from pymongo import ReturnDocument
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository, FieldUpdates, StoredDocument, StoreFilter
from modules.logger.logger import Logger
from modules.notification.internals.store.account_notification_preferences_model import (
    AccountNotificationPreferencesModel,
)
from modules.notification.types import AccountNotificationPreferences, AccountNotificationPreferencesQuery

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


class AccountNotificationPreferencesRepository(
    ApplicationRepository[AccountNotificationPreferences, AccountNotificationPreferencesQuery]
):
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

    @classmethod
    def from_doc(cls, doc: StoredDocument) -> AccountNotificationPreferences:
        model = AccountNotificationPreferencesModel.from_bson(doc)
        return AccountNotificationPreferences(
            account_id=model.account_id,
            created_at=model.created_at,
            email_enabled=model.email_enabled,
            push_enabled=model.push_enabled,
            sms_enabled=model.sms_enabled,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_doc(cls, entity: AccountNotificationPreferences) -> StoredDocument:
        # The stored document carries fields the domain entity does not (active, timestamps); the model
        # supplies their defaults. create() strips id/_id so MongoDB assigns a fresh ObjectId.
        return AccountNotificationPreferencesModel(
            account_id=entity.account_id,
            id=None,
            email_enabled=entity.email_enabled,
            push_enabled=entity.push_enabled,
            sms_enabled=entity.sms_enabled,
        ).to_bson()

    @classmethod
    def _to_filter(cls, params: AccountNotificationPreferencesQuery) -> StoreFilter:
        store_filter: StoreFilter = {}
        if params.account_id is not None:
            store_filter["account_id"] = params.account_id
        if params.active is not None:
            store_filter["active"] = params.active
        return store_filter

    @classmethod
    def update_by_account_id(cls, account_id: str, fields: FieldUpdates) -> AccountNotificationPreferences:
        # The active preferences row is identified by its natural key (account_id), not its ObjectId, so
        # this $set has no generic-verb equivalent and stays on the repository (see backend-architecture.md).
        updated = cls.collection().find_one_and_update(
            {"account_id": account_id, "active": True},
            {"$set": {**fields, "updated_at": datetime.now(UTC)}},
            return_document=ReturnDocument.AFTER,
        )
        return cls.from_doc(updated)
