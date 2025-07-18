from datetime import datetime, timedelta
from typing import List

from pymongo.cursor import Cursor

from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.types import DeviceTokenInfo


class DeviceTokenUtil:
    @staticmethod
    def convert_device_token_model_to_device_token_info(device_token_model: DeviceTokenModel) -> DeviceTokenInfo:
        return DeviceTokenInfo(
            token=device_token_model.token,
            device_type=device_token_model.device_type,
            app_version=device_token_model.app_version,
        )

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
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        return cutoff_date

    @staticmethod
    def get_current_timestamp() -> datetime:
        return datetime.now()
