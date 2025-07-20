from typing import List, Optional

from modules.notification.internals.device_token_util import DeviceTokenUtil
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.types import DeviceToken


class DeviceTokenReader:
    @staticmethod
    def get_all_active_tokens(days: int = 30) -> List[str]:
        cutoff_date = DeviceTokenUtil.calculate_activity_cutoff_date(days)
        cursor = DeviceTokenRepository.collection().find({"last_active": {"$gt": cutoff_date}})
        return DeviceTokenUtil.extract_tokens_from_cursor(cursor)

    @staticmethod
    def get_token_by_value(token: str) -> Optional[DeviceToken]:
        token_doc = DeviceTokenRepository.collection().find_one({"token": token})
        if not token_doc:
            return None

        return DeviceTokenUtil.convert_device_token_bson_to_device_token(token_doc)

    @staticmethod
    def get_tokens_by_user_id(user_id: str) -> List[str]:
        cursor = DeviceTokenRepository.collection().find({"user_id": user_id})
        return DeviceTokenUtil.extract_tokens_from_cursor(cursor)

    @staticmethod
    def get_device_tokens_by_user_id(user_id: str) -> List[DeviceToken]:
        cursor = DeviceTokenRepository.collection().find({"user_id": user_id})
        device_tokens: List[DeviceToken] = []
        for doc in cursor:
            device_token = DeviceTokenUtil.convert_device_token_bson_to_device_token(doc)
            device_tokens.append(device_token)
        return device_tokens

    @staticmethod
    def get_all_active_device_tokens(days: int = 30) -> List[DeviceToken]:
        cutoff_date = DeviceTokenUtil.calculate_activity_cutoff_date(days)
        cursor = DeviceTokenRepository.collection().find({"last_active": {"$gt": cutoff_date}})
        device_tokens: List[DeviceToken] = []
        for doc in cursor:
            device_token = DeviceTokenUtil.convert_device_token_bson_to_device_token(doc)
            device_tokens.append(device_token)
        return device_tokens
