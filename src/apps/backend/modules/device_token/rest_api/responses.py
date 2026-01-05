from dataclasses import dataclass
from typing import Optional

from modules.device_token.types import Platform

@dataclass(frozen=True)
class RegisterDeviceTokenResponse:
    id: str
    device_token: str
    platform: Platform
    device_info: Optional[dict]
    active: bool
    created_at: Optional[str]

@dataclass(frozen=True)
class DeviceTokenListItemResponse:
    id: str
    platform: Platform
    device_info: Optional[dict]
    active: bool
    last_used_at: Optional[str]
