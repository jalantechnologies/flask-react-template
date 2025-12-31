from typing import Optional, Any

from bson.objectid import ObjectId

from modules.device_token.errors import DeviceTokenNotFoundError
from modules.device_token.internal.store.device_token_repository import DeviceTokenRepository
from modules.device_token.internal.device_token_util import DeviceTokenUtil
from modules.device_token.types import DeviceToken, GetDeviceTokenParams, GetDeviceTokensParams


class DeviceTokenReader:
    @staticmethod
    def get_device_token_by_id(*, params: GetDeviceTokenParams) -> DeviceToken:
        device_token_bson = DeviceTokenRepository.collection().find_one(
            {"_id": ObjectId(params.device_token_id), "active": True}
        )

        if device_token_bson is None:
            raise DeviceTokenNotFoundError(device_token_id=params.device_token_id)
        
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(device_token_bson)

    @staticmethod
    def get_device_tokens_by_account_id(*, params: GetDeviceTokensParams) -> list[DeviceToken]:
        filter_query: dict[str, Any] = {"account_id": params.account_id}
        if params.active_only:
            filter_query["active"] = True

        device_tokens_bson = list(
            DeviceTokenRepository.collection().find(filter_query).sort([("created_at", -1)])
        )

        return [
            DeviceTokenUtil.convert_device_token_bson_to_device_token(device_token_bson)
            for device_token_bson in device_tokens_bson
        ]

    @staticmethod
    def get_device_token_by_token(*, token: str) -> Optional[DeviceToken]:
        device_token_bson = DeviceTokenRepository.collection().find_one(
            {"device_token": token, "active": True}
        )

        if device_token_bson is None:
            return None
        
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(device_token_bson)
