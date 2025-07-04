from typing import List

from modules.notification.email_service import EmailService
from modules.notification.internals.device_token_reader import DeviceTokenReader
from modules.notification.internals.device_token_writer import DeviceTokenWriter
from modules.notification.sms_service import SMSService
from modules.notification.types import DeviceTokenInfo, RegisterDeviceTokenParams, SendEmailParams, SendSMSParams


class NotificationService:

    @staticmethod
    def send_email(*, params: SendEmailParams) -> None:
        return EmailService.send_email(params=params)

    @staticmethod
    def send_sms(*, params: SendSMSParams) -> None:
        return SMSService.send_sms(params=params)

    @staticmethod
    def register_device_token(*, params: RegisterDeviceTokenParams) -> DeviceTokenInfo:
        return DeviceTokenWriter.register_device_token(params=params)

    @staticmethod
    def get_device_tokens_by_user_id(user_id: str) -> List[str]:
        return DeviceTokenReader.get_tokens_by_user_id(user_id)

    @staticmethod
    def remove_device_token(token: str) -> None:
        DeviceTokenWriter.remove_device_token(token)

    @staticmethod
    def cleanup_inactive_tokens(days: int = 60) -> int:
        return DeviceTokenWriter.cleanup_inactive_tokens(days)
