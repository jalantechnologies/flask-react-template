from datetime import datetime, timedelta

from pymongo import ReturnDocument

from modules.logger.logger import Logger
from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.types import DeviceTokenInfo, RegisterDeviceTokenParams


class DeviceTokenWriter:
    @staticmethod
    def register_device_token(*, params: RegisterDeviceTokenParams) -> DeviceTokenInfo:
        now = datetime.now()

        existing_token = DeviceTokenRepository.collection().find_one({"token": params.token})

        if existing_token:
            updated_token = DeviceTokenRepository.collection().find_one_and_update(
                {"token": params.token},
                {
                    "$set": {
                        "user_id": params.user_id,
                        "device_type": params.device_type,
                        "app_version": params.app_version,
                        "last_active": now,
                        "updated_at": now,
                    }
                },
                return_document=ReturnDocument.AFTER,
            )
            device_token_model = DeviceTokenModel.from_bson(updated_token)
        else:
            device_token_model = DeviceTokenModel(
                token=params.token,
                user_id=params.user_id,
                device_type=params.device_type,
                app_version=params.app_version,
                last_active=now,
                id=None,
            )

            result = DeviceTokenRepository.collection().insert_one(device_token_model.to_bson())
            inserted_token = DeviceTokenRepository.collection().find_one({"_id": result.inserted_id})
            device_token_model = DeviceTokenModel.from_bson(inserted_token)

        return DeviceTokenInfo(
            token=device_token_model.token,
            device_type=device_token_model.device_type,
            app_version=device_token_model.app_version,
        )

    @staticmethod
    def remove_device_token(token: str) -> bool:
        result = DeviceTokenRepository.collection().delete_one({"token": token})
        return result.deleted_count > 0

    @staticmethod
    def cleanup_inactive_tokens(days: int = 60) -> int:
        cutoff_date = datetime.now() - timedelta(days=days)
        result = DeviceTokenRepository.collection().delete_many({"last_active": {"$lt": cutoff_date}})

        deleted_count = int(result.deleted_count)
        Logger.info(message=f"Cleaned up {deleted_count} inactive device tokens older than {days} days")

        return deleted_count
