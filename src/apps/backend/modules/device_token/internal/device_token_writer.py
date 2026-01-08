from datetime import datetime

from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from modules.device_token.types import CreateDeviceTokenParams, DeviceToken, DeleteDeviceTokenParams, UpdateDeviceTokenParams
from modules.device_token.internal.store.device_token_repository import DeviceTokenRepository
from modules.device_token.internal.device_token_util import DeviceTokenUtil
from modules.device_token.errors import DeviceTokenNotFoundError, DeviceTokenConflictError


class DeviceTokenWriter:
    @staticmethod
    def create_device_token(*, params: CreateDeviceTokenParams) -> DeviceToken:
        device_token_data = {
            "account_id": params.account_id,
            "device_token": params.device_token,
            "platform": params.platform.value,
            "device_info": params.device_info,
            "active": True,
            "last_used_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        try:
            result = DeviceTokenRepository.collection().insert_one(device_token_data)
        except DuplicateKeyError:
            existing = DeviceTokenRepository.collection().find_one(
                {"device_token": params.device_token, "active": True}
            )

            if existing and str(existing["account_id"]) != str(params.account_id):
                raise DeviceTokenConflictError("Device token already registered to another account.")

            raise DeviceTokenConflictError("Device token already registered.")

        created_bson = DeviceTokenRepository.collection().find_one(
            {"_id": result.inserted_id}
        )

        return DeviceTokenUtil.convert_device_token_bson_to_device_token(created_bson)
    
    @staticmethod
    def update_device_token(*, params: UpdateDeviceTokenParams) -> DeviceToken:
        update_fields: dict = {}

        if params.device_info is not None:
            update_fields["device_info"] = params.device_info

        if params.device_token is not None:
            update_fields["device_token"] = params.device_token

        update_fields["updated_at"] = datetime.now()
        update_fields["last_used_at"] = datetime.now()

        try:
            updated_bson = DeviceTokenRepository.collection().find_one_and_update(
                {
                    "_id": ObjectId(params.device_token_id),
                    "account_id": params.account_id,
                    "active": True
                },
                {
                    "$set": update_fields
                },
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError:
            raise DeviceTokenConflictError( "Device token already registered to another device.")

        if updated_bson is None:
            raise DeviceTokenNotFoundError()

        return DeviceTokenUtil.convert_device_token_bson_to_device_token(updated_bson)

    @staticmethod
    def deactivate_device_token(*, params: DeleteDeviceTokenParams) -> None:
        deletion_time = datetime.now()

        try:
            object_id = ObjectId(params.device_token_id)
        except InvalidId:
            raise DeviceTokenNotFoundError()

        result = DeviceTokenRepository.collection().find_one_and_update(
            {
                "_id": object_id,
                "account_id": params.account_id,
                "active": True,
            },
            {"$set": {"active": False, "updated_at": deletion_time}}
        )

        if result is None:
            raise DeviceTokenNotFoundError()
        
        return None
