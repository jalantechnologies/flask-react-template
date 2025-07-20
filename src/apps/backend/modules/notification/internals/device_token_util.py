from datetime import datetime, timedelta
from typing import Any, List

from pymongo.cursor import Cursor

from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.types import DeviceToken, DeviceTokenInfo


class DeviceTokenUtil:
    @staticmethod
    def convert_device_token_model_to_device_token_info(device_token_model: DeviceTokenModel) -> DeviceTokenInfo:
        return DeviceTokenInfo(
            token=device_token_model.token,
            device_type=device_token_model.device_type,
            app_version=device_token_model.app_version,
        )

    @staticmethod
    def convert_device_token_model_to_device_token(device_token_model: DeviceTokenModel) -> DeviceToken:
        return DeviceToken(
            id=str(device_token_model.id),
            token=device_token_model.token,
            user_id=device_token_model.user_id,
            device_type=device_token_model.device_type,
            last_active=device_token_model.last_active,
            app_version=device_token_model.app_version,
            created_at=device_token_model.created_at,
            updated_at=device_token_model.updated_at,
        )

    @staticmethod
    def convert_device_token_bson_to_device_token(device_token_bson: dict[str, Any]) -> DeviceToken:
        validated_device_token_data = DeviceTokenModel.from_bson(device_token_bson)
        return DeviceTokenUtil.convert_device_token_model_to_device_token(validated_device_token_data)

    @staticmethod
    def extract_tokens_from_cursor(cursor: Cursor) -> List[str]:
        tokens: List[str] = []
        for doc in cursor:
            if doc.get("token"):
                tokens.append(doc["token"])
        return tokens

    @staticmethod
    def calculate_cutoff_date(days: int) -> datetime:
        return datetime.now() - timedelta(days=days)

    @staticmethod
    def calculate_activity_cutoff_date(days: int) -> datetime:
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date - timedelta(days=days)
        return cutoff_date

    @staticmethod
    def get_current_timestamp() -> datetime:
        return datetime.now()
