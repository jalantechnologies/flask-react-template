from typing import Optional

from twilio.base.exceptions import TwilioException, TwilioRestException
from twilio.rest import Client

from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.notification.errors import ServiceError
from modules.notification.internals.twilio_params import SMSParams
from modules.notification.types import NotificationErrorCode, SendSMSParams


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
            recipient_phone_number = params.recipient_phone.phone_number
            recipient_country_code = params.recipient_phone.country_code
            twilio_error_code = err.code if isinstance(err, TwilioRestException) else None
            twilio_status = err.status if isinstance(err, TwilioRestException) else None

            Logger.error(
                message=(
                    "[notification.twilio_sms_failure] Twilio SMS delivery failed while sending OTP | "
                    f"notification_error_code={NotificationErrorCode.SERVICE_ERROR} "
                    f"recipient_country_code={recipient_country_code} "
                    f"recipient_phone_number={recipient_phone_number} "
                    f"twilio_error_code={twilio_error_code} "
                    f"twilio_status={twilio_status}"
                )
            )
            raise ServiceError(
                message="Our system is facing challenge to deliver OTP to you at the moment, and the team has been notified. We recommend you to come back and try again later",
                original_error=err,
            ) from err

    @staticmethod
    def get_client() -> Client:
        if not TwilioService.__client:
            account_sid = ConfigService[str].get_value(key="twilio.account_sid")
            auth_token = ConfigService[str].get_value(key="twilio.auth_token")

            # Initialize the Twilio client
            TwilioService.__client = Client(account_sid, auth_token)

        return TwilioService.__client
