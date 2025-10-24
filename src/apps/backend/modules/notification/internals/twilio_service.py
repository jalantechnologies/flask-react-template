from typing import Optional

from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from modules.config.config_service import ConfigService
from modules.notification.errors import ServiceError
from modules.notification.internals.twilio_params import SMSParams
from modules.notification.types import SendSMSParams


class TwilioService:
    __client: Optional[Client] = None

    @staticmethod
    def send_sms(params: SendSMSParams) -> None:
        SMSParams.validate(params)

        try:
            client = TwilioService.get_client()

            # Send SMS
            client.messages.create(
                to=params.recipient_phone,
                messaging_service_sid=ConfigService[str].get_value(key="twilio.messaging_service_sid"),
                body=params.message_body,
            )

        except TwilioException as err:
            raise ServiceError(err)

    @staticmethod
    def get_client() -> Client:
        if not TwilioService.__client:
            account_sid = ConfigService[str].get_value(key="twilio.account_sid")
            auth_token = ConfigService[str].get_value(key="twilio.auth_token")

            # Initialize the Twilio client
            TwilioService.__client = Client(account_sid, auth_token)

        return TwilioService.__client
