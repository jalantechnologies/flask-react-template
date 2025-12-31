from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class RegisterDeviceTokenResponse:
    id: str
    device_token: str
    platform: str
    device_info: Optional[dict]
    active: bool
    created_at: Optional[str]

@dataclass(frozen=True)
class DeviceTokenListItemResponse:
    id: str
    platform: str
    device_info: Optional[dict]
    active: bool
    last_used_at: Optional[str]
