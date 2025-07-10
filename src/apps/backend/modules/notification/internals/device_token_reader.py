from datetime import datetime
from typing import List, Optional

from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository


class DeviceTokenReader:
    @staticmethod
    def get_tokens_by_user_id(user_id: str) -> List[str]:
        cursor = DeviceTokenRepository.collection().find({"user_id": user_id})
        tokens: List[str] = []
        for doc in cursor:
            if doc.get("token"):
                tokens.append(doc["token"])
        return tokens

    @staticmethod
    def get_all_active_tokens(days: int = 30) -> List[str]:
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        cursor = DeviceTokenRepository.collection().find({"last_active": {"$gt": cutoff_date}})
        tokens: List[str] = []
        for doc in cursor:
            if doc.get("token"):
                tokens.append(doc["token"])
        return tokens

    @staticmethod
    def get_token_by_value(token: str) -> Optional[DeviceTokenModel]:
        token_doc = DeviceTokenRepository.collection().find_one({"token": token})
        if not token_doc:
            return None

        return DeviceTokenModel.from_bson(token_doc)
