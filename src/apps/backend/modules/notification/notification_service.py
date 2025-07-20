from typing import List

from modules.notification.email_service import EmailService
from modules.notification.internals.device_token_reader import DeviceTokenReader
from modules.notification.internals.device_token_writer import DeviceTokenWriter
from modules.notification.sms_service import SMSService
from modules.notification.types import (
    DeviceToken,
    DeviceTokenInfo,
    RegisterDeviceTokenParams,
    SendEmailParams,
    SendSMSParams,
)


class NotificationService:

    @staticmethod
    def cleanup_inactive_tokens(days: int = 60) -> int:
        return DeviceTokenWriter.cleanup_inactive_tokens(days)

    @staticmethod
    def get_device_tokens_by_user_id(user_id: str) -> List[str]:
        return DeviceTokenReader.get_tokens_by_user_id(user_id)

    @staticmethod
    def get_device_tokens_entities_by_user_id(user_id: str) -> List[DeviceToken]:
        return DeviceTokenReader.get_device_tokens_by_user_id(user_id)

    @staticmethod
    def get_active_tokens(days: int = 30) -> List[str]:
        return DeviceTokenReader.get_all_active_tokens(days)

    @staticmethod
    def get_active_device_tokens(days: int = 30) -> List[DeviceToken]:
        return DeviceTokenReader.get_all_active_device_tokens(days)

    @staticmethod
    def register_device_token(*, params: RegisterDeviceTokenParams) -> DeviceToken:
        return DeviceTokenWriter.register_device_token(params=params)

    @staticmethod
    def register_device_token_info(*, params: RegisterDeviceTokenParams) -> DeviceTokenInfo:
        device_token = DeviceTokenWriter.register_device_token(params=params)
        return DeviceTokenInfo(
            token=device_token.token, device_type=device_token.device_type, app_version=device_token.app_version
        )

    @staticmethod
    def remove_device_token(token: str) -> bool:
        return DeviceTokenWriter.remove_device_token(token)

    @staticmethod
    def update_token_activity(token: str) -> None:
        DeviceTokenWriter.update_token_activity(token)

    @staticmethod
    def send_email(*, params: SendEmailParams) -> None:
        return EmailService.send_email(params=params)

    @staticmethod
    def send_sms(*, params: SendSMSParams) -> None:
        return SMSService.send_sms(params=params)
