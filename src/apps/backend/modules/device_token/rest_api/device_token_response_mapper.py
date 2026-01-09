from typing import Optional
from datetime import datetime, timezone

from modules.device_token.types import DeviceToken
from modules.device_token.rest_api.responses import RegisterDeviceTokenResponse, DeviceTokenListItemResponse, UpdateDeviceTokenResponse


def to_iso8601(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

class DeviceTokenResponseMapper:
    @staticmethod
    def to_register_response(token: DeviceToken) -> RegisterDeviceTokenResponse:
        return RegisterDeviceTokenResponse(
            id=token.id,
            device_token=token.device_token,
            platform=token.platform.value,
            device_info=token.device_info,
            active=token.active,
            created_at=to_iso8601(token.created_at),
        )

    @staticmethod
    def to_list_item(token: DeviceToken) -> DeviceTokenListItemResponse:
        return DeviceTokenListItemResponse(
            id=token.id,
            platform=token.platform.value,
            device_info=token.device_info,
            active=token.active,
            last_used_at=to_iso8601(token.last_used_at),
        )
    
    @staticmethod
    def to_update_response(token: DeviceToken) -> UpdateDeviceTokenResponse:
        return UpdateDeviceTokenResponse(
            id=token.id,
            platform=token.platform.value,
            device_info=token.device_info,
            active=token.active,
            last_used_at=to_iso8601(token.last_used_at),
        )
    