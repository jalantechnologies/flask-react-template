from datetime import UTC, datetime
from typing import Optional

from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.api_key.internal.store.api_key_model import ApiKeyModel
from modules.api_key.types import ApiKey, ApiKeyQuery
from modules.application.repository import ApplicationRepository, SortSpec, StoredDocument, StoreFilter
from modules.logger.logger import Logger

API_KEY_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["account_id", "name", "key_hash", "status", "kind", "created_at", "updated_at"],
        "properties": {
            "account_id": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "key_hash": {"bsonType": "string"},
            "status": {"bsonType": "string"},
            "kind": {"bsonType": "string"},
            "expires_at": {"bsonType": ["date", "null"]},
            "last_used_at": {"bsonType": ["date", "null"]},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}


class ApiKeyRepository(ApplicationRepository[ApiKey, ApiKeyQuery]):
    collection_name = ApiKeyModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        collection.create_index("key_hash", unique=True)
        collection.create_index([("account_id", 1), ("kind", 1), ("status", 1)], name="account_kind_status_index")

        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": API_KEY_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }
        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:
                collection.database.create_collection(cls.collection_name, validator=API_KEY_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection api_keys: {e.details}")
        return True

    @classmethod
    def to_doc(cls, entity: ApiKey) -> StoredDocument:
        # ApiKeyModel supplies the stored timestamps the domain ApiKey omits; enum values are stored as
        # their string form. create() strips id/_id so MongoDB assigns a fresh ObjectId.
        doc = ApiKeyModel(
            account_id=entity.account_id,
            name=entity.name,
            key_hash=entity.key_hash,
            status=entity.status,
            kind=entity.kind,
            expires_at=entity.expires_at,
            last_used_at=entity.last_used_at,
            id=None,
        ).to_bson()
        # Strict collection validation expects string BSON, so store the enum members' string values.
        doc["status"] = entity.status.value
        doc["kind"] = entity.kind.value
        return doc

    @classmethod
    def from_doc(cls, doc: StoredDocument) -> ApiKey:
        model = ApiKeyModel.from_bson(doc)
        return ApiKey(
            id=str(model.id),
            account_id=model.account_id,
            name=model.name,
            key_hash=model.key_hash,
            status=model.status,
            kind=model.kind,
            expires_at=cls._as_utc(model.expires_at),
            last_used_at=cls._as_utc(model.last_used_at),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def _to_filter(cls, params: ApiKeyQuery) -> StoreFilter:
        store_filter: StoreFilter = {}
        if params.id is not None:
            object_id = cls._to_object_id(params.id)
            # A malformed id matches nothing; force an empty result rather than raising.
            store_filter["_id"] = object_id if object_id is not None else {"$in": []}
        if params.account_id is not None:
            store_filter["account_id"] = params.account_id
        if params.key_hash is not None:
            store_filter["key_hash"] = params.key_hash
        if params.name is not None:
            store_filter["name"] = params.name
        if params.status is not None:
            store_filter["status"] = params.status.value
        if params.kind is not None:
            store_filter["kind"] = params.kind.value
        if params.expires_before is not None:
            # BSON orders null below any date, so an explicit $ne None keeps never-expiring keys out of
            # the "already expired" window.
            store_filter["expires_at"] = {"$lt": params.expires_before, "$ne": None}
        return store_filter

    @classmethod
    def _to_sort(cls, params: ApiKeyQuery) -> Optional[SortSpec]:
        return [("created_at", -1), ("_id", -1)]

    @staticmethod
    def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
