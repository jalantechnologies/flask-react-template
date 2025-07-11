from typing import List, Optional

from modules.notification.internals.device_token_util import DeviceTokenUtil
from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository


class DeviceTokenReader:
    @staticmethod
    def get_all_active_tokens(days: int = 30) -> List[str]:
        cutoff_date = DeviceTokenUtil.calculate_activity_cutoff_date(days)
        cursor = DeviceTokenRepository.collection().find({"last_active": {"$gt": cutoff_date}})
        return DeviceTokenUtil.extract_tokens_from_cursor(cursor)

    @staticmethod
    def get_token_by_value(token: str) -> Optional[DeviceTokenModel]:
        token_doc = DeviceTokenRepository.collection().find_one({"token": token})
        if not token_doc:
            return None

        return DeviceTokenModel.from_bson(token_doc)

    @staticmethod
    def get_tokens_by_user_id(user_id: str) -> List[str]:
        cursor = DeviceTokenRepository.collection().find({"user_id": user_id})
        return DeviceTokenUtil.extract_tokens_from_cursor(cursor)
