from typing import Any
from datetime import datetime

from modules.device_token.internal.store.device_token_model import DeviceTokenModel
from modules.device_token.types import DeviceToken, Platform


class DeviceTokenUtil:
    @staticmethod
    def convert_device_token_bson_to_device_token(device_token_bson: dict[str, Any]) -> DeviceToken:
        validated_device_token_data = DeviceTokenModel.from_bson(device_token_bson)
        return DeviceToken(
            id=str(validated_device_token_data.id),
            account_id=validated_device_token_data.account_id,
            device_token=validated_device_token_data.device_token,
            platform=Platform(validated_device_token_data.platform),
            device_info=validated_device_token_data.device_info,
            last_used_at=validated_device_token_data.last_used_at,
            active=validated_device_token_data.active,
            created_at=validated_device_token_data.created_at or datetime.now(),
            updated_at=validated_device_token_data.updated_at or datetime.now()
        )
