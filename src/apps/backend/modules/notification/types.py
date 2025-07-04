from dataclasses import dataclass
from typing import Any, Dict, Optional

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


@dataclass(frozen=True)
class ValidationFailure:
    field: str
    message: str


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
