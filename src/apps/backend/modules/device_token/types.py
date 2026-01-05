from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict


class Platform(Enum):
    ANDROID = "android"
    IOS = "ios"


@dataclass(frozen=True)
class DeviceToken:
    id: str
    account_id: str
    device_token: str
    platform: str
    device_info: Optional[dict]
    active: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateDeviceTokenParams:
    account_id: str
    device_token: str
    platform: Platform
    device_info: Optional[Dict] = None

@dataclass(frozen=True)
class GetDeviceTokenParams:
    device_token_id: str

@dataclass(frozen=True)
class GetDeviceTokensParams:
    account_id: str
    active_only: bool = True

@dataclass(frozen=True)
class DeleteDeviceTokenParams:
    account_id: str
    device_token_id: str

@dataclass(frozen=True)
class DeviceTokenErrorCode:
    NOT_FOUND: str = "DEVICE_TOKEN_ERR_01"
    INVALID_PLATFORM: str = "DEVICE_TOKEN_ERR_02"
    BAD_REQUEST: str = "DEVICE_TOKEN_ERR_03"

@dataclass(frozen=True)
class DeviceTokenDeletionResult:
    device_token_id: str
    deleted_at: datetime
    success: bool

@dataclass(frozen=True)
class ValidationFailure:
    field: str
    message: str
