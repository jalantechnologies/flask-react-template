from datetime import UTC, datetime
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.common.types import AuditActor, ResourceAction
from modules.application.repository import ApplicationRepository, SortSpec, StoredDocument, StoreFilter
from modules.authentication.internal.password_reset_token.password_reset_token_util import PasswordResetTokenUtil
from modules.authentication.internal.password_reset_token.store.password_reset_token_model import (
    PasswordResetTokenModel,
)
from modules.authentication.types import PasswordResetToken, PasswordResetTokenQuery
from modules.logger.logger import Logger

PASSWORD_RESET_TOKEN_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account", "expires_at", "is_used", "token"],
        "properties": {
            "account": {"bsonType": "objectId", "description": "must be an ObjectId and is required"},
            "created_at": {"bsonType": "date"},
            "expires_at": {"bsonType": "date", "description": "must be a valid date and is required"},
            "is_used": {"bsonType": "bool", "description": "must be a boolean and is required"},
            "token": {"bsonType": "string", "description": "must be a string and is required"},
            "updated_at": {"bsonType": "date"},
            "_id": {"bsonType": "objectId", "description": "must be an ObjectId"},
        },
    }
}


class PasswordResetTokenRepository(ApplicationRepository[PasswordResetToken, PasswordResetTokenQuery]):
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

    @classmethod
    def from_doc(cls, doc: StoredDocument) -> PasswordResetToken:
        model = PasswordResetTokenModel.from_bson(doc)
        return PasswordResetToken(
            account=str(model.account),
            created_at=model.created_at,
            expires_at=str(model.expires_at),
            id=str(model.id),
            is_expired=PasswordResetTokenUtil.is_token_expired(model.expires_at),
            is_used=model.is_used,
            token=model.token,
            updated_at=model.updated_at,
        )

    @classmethod
    def _to_filter(cls, params: PasswordResetTokenQuery) -> StoreFilter:
        store_filter: StoreFilter = {}
        if params.account_id is not None:
            # The account reference is stored as an ObjectId, so the domain account id is converted here.
            store_filter["account"] = ObjectId(params.account_id)
        return store_filter

    @classmethod
    def _to_sort(cls, params: PasswordResetTokenQuery) -> Optional[SortSpec]:
        # Latest token first: an account can have several, and reads always want the most recent.
        return [("expires_at", -1)]

    @classmethod
    def create_for_account(
        cls, account_id: str, token_hash: str, expires_at: datetime, *, actor: AuditActor
    ) -> PasswordResetToken:
        # The stored document keys `account` as an ObjectId and `expires_at` as a real date — a store-shaped
        # write the generic create()/to_doc() (which round-trips the string-typed domain entity) cannot
        # express, so it stays on the repository (see docs/backend-architecture.md).
        creation_time = datetime.now(UTC)
        doc: StoredDocument = {
            "account": ObjectId(account_id),
            "created_at": creation_time,
            "expires_at": expires_at,
            "is_used": False,
            "token": token_hash,
            "updated_at": creation_time,
        }
        result = cls.collection().insert_one(doc)
        cls._emit_audit(actor, str(result.inserted_id), ResourceAction.CREATE)
        return cls.from_doc({**doc, "_id": result.inserted_id})
