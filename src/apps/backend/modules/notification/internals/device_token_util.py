from typing import Any, List

from pymongo.cursor import Cursor

from modules.notification.internals.store.device_token_model import DeviceTokenModel
from modules.notification.types import DeviceToken


class DeviceTokenUtil:
    @staticmethod
    def convert_device_token_bson_to_device_token(device_token_bson: dict[str, Any]) -> DeviceToken:
        validated_device_token_data = DeviceTokenModel.from_bson(device_token_bson)
        return DeviceToken(
            id=str(validated_device_token_data.id),
            token=validated_device_token_data.token,
            account_id=validated_device_token_data.account_id,
            device_type=validated_device_token_data.device_type,
            created_at=validated_device_token_data.created_at,
            updated_at=validated_device_token_data.updated_at,
        )

    @staticmethod
    def extract_tokens_from_cursor(cursor: Cursor) -> List[str]:
        tokens: List[str] = []
        for doc in cursor:
            if doc.get("token"):
                tokens.append(doc["token"])
        return tokens
