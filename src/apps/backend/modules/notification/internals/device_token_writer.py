from pymongo import ReturnDocument

from modules.notification.errors import InvalidDeviceTypeError
from modules.notification.internals.device_token_util import DeviceTokenUtil
from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.types import DeviceToken, DeviceType, RegisterDeviceTokenParams


class DeviceTokenWriter:

    @staticmethod
    def _validate_device_type(device_type_str: str) -> DeviceType:
        try:
            return DeviceType(device_type_str)
        except ValueError:
            raise InvalidDeviceTypeError(device_type_str, list(DeviceType))

    @staticmethod
    def _create_user_fcm_token(params: RegisterDeviceTokenParams) -> DeviceToken:
        DeviceTokenWriter._validate_device_type(params.device_type)

        device_token_model = DeviceTokenModel(
            token=params.token, user_id=params.user_id, device_type=params.device_type, id=None
        )
        result = DeviceTokenRepository.collection().insert_one(device_token_model.to_bson())
        inserted_token = DeviceTokenRepository.collection().find_one({"_id": result.inserted_id})
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(inserted_token)

    @staticmethod
    def _update_user_fcm_token(params: RegisterDeviceTokenParams) -> DeviceToken:
        DeviceTokenWriter._validate_device_type(params.device_type)

        updated_token = DeviceTokenRepository.collection().find_one_and_update(
            {"token": params.token},
            {
                "$set": {"user_id": params.user_id, "device_type": params.device_type.value},
                "$currentDate": {"updated_at": True},
            },
            return_document=ReturnDocument.AFTER,
        )
        return DeviceTokenUtil.convert_device_token_bson_to_device_token(updated_token)

    @staticmethod
    def delete_user_fcm_tokens_by_user_id(user_id: str) -> int:
        result = DeviceTokenRepository.collection().delete_many({"user_id": user_id})
        return int(result.deleted_count)

    @staticmethod
    def upsert_user_fcm_token(*, params: RegisterDeviceTokenParams) -> DeviceToken:
        existing_token = DeviceTokenRepository.collection().find_one({"token": params.token})

        if existing_token:
            return DeviceTokenWriter._update_user_fcm_token(params)
        else:
            return DeviceTokenWriter._create_user_fcm_token(params)
