from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from modules.account.types import PhoneNumber


@dataclass(frozen=True)
class EmailSender:
    email: str
    name: str


@dataclass(frozen=True)
class EmailRecipient:
    email: str


@dataclass(frozen=True)
class SendEmailParams:
    recipient: EmailRecipient
    sender: EmailSender
    template_id: str
    template_data: Dict[str, Any] | None = None


@dataclass(frozen=True)
class SendSMSParams:
    message_body: str
    recipient_phone: PhoneNumber


@dataclass(frozen=True)
class CommunicationErrorCode:
    VALIDATION_ERROR = "COMMUNICATION_ERR_01"
    SERVICE_ERROR = "COMMUNICATION_ERR_02"
    INVALID_FCM_TOKEN = "COMMUNICATION_ERR_03"
    FCM_SERVICE_ERROR = "COMMUNICATION_ERR_04"


@dataclass(frozen=True)
class ValidationFailure:
    field: str
    message: str


class DeviceType(str, Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


@dataclass(frozen=True)
class DeviceTokenInfo:
    token: str
    device_type: str
    app_version: Optional[str] = None


@dataclass(frozen=True)
class RegisterDeviceTokenParams:
    user_id: str
    token: str
    device_type: str
    app_version: Optional[str] = None


@dataclass(frozen=True)
class FCMNotificationData:
    title: str
    body: str
    data: Dict[str, str] = field(default_factory=dict)
    image_url: Optional[str] = None


@dataclass(frozen=True)
class SendFCMParams:
    notification: FCMNotificationData
    user_ids: Optional[List[str]] = None
    tokens: Optional[List[str]] = None
    topic: Optional[str] = None
