from datetime import datetime
from typing import List, Optional

from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository


class DeviceTokenReader:
    @staticmethod
    def get_tokens_by_user_id(user_id: str) -> List[str]:
        cursor = DeviceTokenRepository.collection().find({"user_id": user_id})
        enhanced_tokens = []

        for doc in cursor:
            token_model = DeviceTokenModel.from_bson(doc)
            token_info = {
                "token": token_model.token,
                "user_id": token_model.user_id,
                "device_type": token_model.device_type,
                "app_version": token_model.app_version,
                "last_active": token_model.last_active.isoformat() if token_model.last_active else None,
                "created_at": token_model.created_at.isoformat() if token_model.created_at else None,
                "updated_at": token_model.updated_at.isoformat() if token_model.updated_at else None,
                "id": str(token_model.id) if token_model.id else None,
            }
            enhanced_tokens.append(token_info)

        return enhanced_tokens

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
        """Get token document by token value"""
        token_doc = DeviceTokenRepository.collection().find_one({"token": token})
        if not token_doc:
            return None

        return DeviceTokenModel.from_bson(token_doc)

    @staticmethod
    def update_token_activity(token: str) -> None:
        DeviceTokenRepository.collection().update_one(
            {"token": token}, {"$set": {"last_active": datetime.now(), "updated_at": datetime.now()}}
        )
