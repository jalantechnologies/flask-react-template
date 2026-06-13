from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from modules.application.repository import ApplicationRepository, StoredDocument, StoreFilter
from modules.authentication.internals.otp.store.otp_model import OTPModel
from modules.authentication.types import OTP, OTPQuery
from modules.logger.logger import Logger

OTP_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["otp_code", "phone_number", "status", "active"],
        "properties": {
            "active": {"bsonType": "bool", "description": "must be a boolean and is required"},
            "otp_code": {"bsonType": "string", "description": "must be a string and is required"},
            "phone_number": {
                "bsonType": "object",
                "required": ["country_code", "phone_number"],
                "properties": {
                    "country_code": {"bsonType": "string", "description": "must be a string"},
                    "phone_number": {"bsonType": "string", "description": "must be a string"},
                },
                "description": "must be an object with country_code and phone_number",
            },
            "status": {"bsonType": "string", "description": "must be a string and is required"},
            "created_at": {"bsonType": "date", "description": "must be a valid date"},
            "updated_at": {"bsonType": "date", "description": "must be a valid date"},
            "_id": {"bsonType": "objectId", "description": "must be an ObjectId"},
        },
    }
}


class OTPRepository(ApplicationRepository[OTP, OTPQuery]):
    collection_name = OTPModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:

        collection.create_index("phone_number")
        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": OTP_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }
        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:  # NamespaceNotFound MongoDB error code
                collection.database.create_collection(cls.collection_name, validator=OTP_VALIDATION_SCHEMA)
            else:
                Logger.error(message=f"OperationFailure occurred for collection otp: {e.details}")
        return True

    @classmethod
    def from_doc(cls, doc: StoredDocument) -> OTP:
        model = OTPModel.from_bson(doc)
        return OTP(
            id=str(model.id),
            otp_code=model.otp_code,
            phone_number=model.phone_number,
            status=model.status,
            active=model.active,
        )

    @classmethod
    def to_doc(cls, entity: OTP) -> StoredDocument:
        # OTPModel adds the stored timestamps the domain OTP omits. create() strips id/_id so MongoDB
        # assigns a fresh ObjectId.
        return OTPModel(
            active=entity.active,
            id=None,
            otp_code=entity.otp_code,
            phone_number=entity.phone_number,
            status=entity.status,
        ).to_bson()

    @classmethod
    def _to_filter(cls, params: OTPQuery) -> StoreFilter:
        store_filter: StoreFilter = {}
        if params.otp_code is not None:
            store_filter["otp_code"] = params.otp_code
        if params.phone_number is not None:
            store_filter["phone_number"] = {
                "country_code": params.phone_number.country_code,
                "phone_number": params.phone_number.phone_number,
            }
        if params.active is not None:
            store_filter["active"] = params.active
        return store_filter
