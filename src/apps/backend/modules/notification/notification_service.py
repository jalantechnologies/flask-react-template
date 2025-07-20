from typing import List

from modules.notification.email_service import EmailService
from modules.notification.internals.device_token_reader import DeviceTokenReader
from modules.notification.internals.device_token_writer import DeviceTokenWriter
from modules.notification.sms_service import SMSService
from modules.notification.types import DeviceToken, RegisterDeviceTokenParams, SendEmailParams, SendSMSParams


class NotificationService:
    @staticmethod
    def register_device_token(*, params: RegisterDeviceTokenParams) -> DeviceToken:
        return DeviceTokenWriter.register_device_token(params=params)

    @staticmethod
    def remove_device_token(token: str) -> bool:
        return DeviceTokenWriter.remove_device_token(token)

    @staticmethod
    def get_user_fcm_tokens(user_id: str) -> List[str]:
        return DeviceTokenReader.get_user_fcm_tokens(user_id)

    @staticmethod
    def send_email(*, params: SendEmailParams) -> None:
        return EmailService.send_email(params=params)

    @staticmethod
    def send_sms(*, params: SendSMSParams) -> None:
        return SMSService.send_sms(params=params)
