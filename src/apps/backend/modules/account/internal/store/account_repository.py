from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.account.internal.store.account_model import AccountDocument, AccountModel
from modules.account.types import Account, AccountQuery
from modules.core.repository import ApplicationRepository, StoredDocument, StoreFilter
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


class AccountRepository(ApplicationRepository[Account, AccountQuery]):
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

    @classmethod
    def from_doc(cls, doc: StoredDocument) -> Account:
        model = AccountModel.from_bson(doc)
        return Account(
            created_at=model.created_at,
            first_name=model.first_name,
            hashed_password=model.hashed_password,
            id=str(model.id),
            last_name=model.last_name,
            phone_number=model.phone_number,
            updated_at=model.updated_at,
            username=model.username,
        )

    @classmethod
    def to_doc(cls, entity: Account) -> AccountDocument:
        # The stored document carries fields the domain Account does not (active, timestamps); AccountModel
        # supplies their defaults. create() strips id/_id so MongoDB assigns a fresh ObjectId.
        return AccountModel(
            first_name=entity.first_name,
            hashed_password=entity.hashed_password,
            id=None,
            last_name=entity.last_name,
            phone_number=entity.phone_number,
            username=entity.username,
        ).to_bson()

    @classmethod
    def _to_filter(cls, params: AccountQuery) -> StoreFilter:
        store_filter: StoreFilter = {}
        if params.id is not None:
            object_id = cls._to_object_id(params.id)
            # A malformed id matches nothing; force an empty result rather than raising.
            store_filter["_id"] = object_id if object_id is not None else {"$in": []}
        if params.username is not None:
            store_filter["username"] = params.username
        if params.phone_number is not None:
            store_filter["phone_number"] = {
                "country_code": params.phone_number.country_code,
                "phone_number": params.phone_number.phone_number,
            }
        if params.active is not None:
            store_filter["active"] = params.active
        return store_filter
