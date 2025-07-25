from pymongo import ReturnDocument

from modules.notification.internals.device_token_util import DeviceTokenUtil
from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.types import DeviceToken, RegisterDeviceTokenParams


class DeviceTokenWriter:

    @staticmethod
    def _create_account_fcm_token(params: RegisterDeviceTokenParams) -> DeviceToken:
        device_token_model = DeviceTokenModel(
            token=params.token, account_id=params.account_id, device_type=params.device_type, id=None
        )
        result = DeviceTokenRepository.collection().insert_one(device_token_model.to_bson())
        inserted_token = DeviceTokenRepository.collection().find_one({"_id": result.inserted_id})
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(inserted_token)

    @staticmethod
    def _update_account_fcm_token(params: RegisterDeviceTokenParams) -> DeviceToken:
        updated_token = DeviceTokenRepository.collection().find_one_and_update(
            {"token": params.token},
            {
                "$set": {"account_id": params.account_id, "device_type": params.device_type.value},
                "$currentDate": {"updated_at": True},
            },
            return_document=ReturnDocument.AFTER,
        )
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(updated_token)

    @staticmethod
    def delete_account_fcm_tokens_by_account_id(account_id: str) -> int:
        result = DeviceTokenRepository.collection().delete_many({"account_id": account_id})
        return int(result.deleted_count)

    @staticmethod
    def upsert_account_fcm_token(*, params: RegisterDeviceTokenParams) -> DeviceToken:
        existing_token = DeviceTokenRepository.collection().find_one({"token": params.token})

        if existing_token:
            return DeviceTokenWriter._update_account_fcm_token(params)
        else:
            return DeviceTokenWriter._create_account_fcm_token(params)
