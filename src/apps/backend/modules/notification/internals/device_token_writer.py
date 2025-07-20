from pymongo import ReturnDocument

from modules.notification.internals.device_token_util import DeviceTokenUtil
from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.types import DeviceToken, RegisterDeviceTokenParams


class DeviceTokenWriter:

    @staticmethod
    def _update_existing_token(params: RegisterDeviceTokenParams, now: datetime) -> DeviceToken:
        updated_token = DeviceTokenRepository.collection().find_one_and_update(
            {"token": params.token},
            {
                "$set": {
                    "user_id": params.user_id,
                    "device_type": params.device_type,
                    "app_version": params.app_version,
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(updated_token)

    @staticmethod
    def _create_new_token(params: RegisterDeviceTokenParams) -> DeviceToken:
        device_token_model = DeviceTokenModel(
            token=params.token,
            user_id=params.user_id,
            device_type=params.device_type,
            app_version=params.app_version,
            id=None,
        )
        result = DeviceTokenRepository.collection().insert_one(device_token_model.to_bson())
        inserted_token = DeviceTokenRepository.collection().find_one({"_id": result.inserted_id})
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(inserted_token)

    @staticmethod
    def remove_device_token(token: str) -> bool:
        result = DeviceTokenRepository.collection().delete_one({"token": token})
        return int(result.deleted_count) > 0

    @staticmethod
    def upsert_device_token(*, params: RegisterDeviceTokenParams) -> DeviceToken:
        now = DeviceTokenUtil.get_current_timestamp()

        existing_token = DeviceTokenRepository.collection().find_one({"token": params.token})

        if existing_token:
            return DeviceTokenWriter._update_existing_token(params, now)
        else:
            return DeviceTokenWriter._create_new_token(params)
