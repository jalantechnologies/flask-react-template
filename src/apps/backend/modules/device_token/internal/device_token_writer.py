from datetime import datetime

from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument

from modules.device_token.types import CreateDeviceTokenParams, DeviceToken, DeviceTokenDeletionResult, DeleteDeviceTokenParams
from modules.device_token.internal.store.device_token_repository import DeviceTokenRepository
from modules.device_token.internal.device_token_util import DeviceTokenUtil
from modules.device_token.errors import DeviceTokenNotFoundError


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
            "updated_at": datetime.now()
        }
        
        updated_device_token_bson = DeviceTokenRepository.collection().find_one_and_update(
            {"device_token": params.device_token},
            {
                "$set": device_token_data,
                "$setOnInsert": {"created_at": datetime.now()}
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(updated_device_token_bson)
    
    @staticmethod
    def update_device_token_last_used(*, device_token_id: str) -> DeviceToken:
        updated_device_token_bson = DeviceTokenRepository.collection().find_one_and_update(
            {"_id": ObjectId(device_token_id), "active": True},
            {"$set": {"last_used_at": datetime.now(), "updated_at": datetime.now()}},
            return_document=ReturnDocument.AFTER
        )

        if updated_device_token_bson is None:
            raise DeviceTokenNotFoundError(device_token_id=device_token_id)
        
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(updated_device_token_bson)

    @staticmethod
    def deactivate_device_token(*, params: DeleteDeviceTokenParams) -> DeviceTokenDeletionResult:
        deletion_time = datetime.now()
        try:
            oid = ObjectId(params.device_token_id)
        except InvalidId:
            raise DeviceTokenNotFoundError(device_token_id=params.device_token_id)

        updated_token_bson = DeviceTokenRepository.collection().find_one_and_update(
            {
                "_id": ObjectId(params.device_token_id),
                "account_id": params.account_id,
                "active": True,
            },
            {"$set": {"active": False, "updated_at": deletion_time}},
            return_document=ReturnDocument.AFTER,
        )
        
        return DeviceTokenDeletionResult(
            device_token_id=params.device_token_id,
            deleted_at=deletion_time,
            success=True,
        )
    
    @staticmethod
    def deactivate_device_tokens_by_token(*, token: str) -> int:
        result = DeviceTokenRepository.collection().update_many(
            {"device_token": token, "active": True},
            {"$set": {"active": False, "updated_at": datetime.now()}}
        )

        return int(result.modified_count)