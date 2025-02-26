from typing import Optional

import sendgrid
from sendgrid.helpers.mail import From, Mail, TemplateId, To

from modules.communication.errors import ServiceError
from modules.communication.internals.sendgrid_email_params import EmailParams
from modules.communication.types import SendEmailParams
from modules.config.config_service import ConfigService


class SendGridService:
    __client: Optional[sendgrid.SendGridAPIClient] = None

    @staticmethod
    def send_email(params: SendEmailParams) -> None:
        EmailParams.validate(params)

        message = Mail(from_email=From(params.sender.email, params.sender.name), to_emails=To(params.recipient.email))
        message.template_id = TemplateId(params.template_id)
        message.dynamic_template_data = params.template_data

        try:
            client = SendGridService.get_client()
            client.send(message)

        except sendgrid.SendGridException as err:
            raise ServiceError(err)

    @staticmethod
    def get_client() -> sendgrid.SendGridAPIClient:
        if not SendGridService.__client:
            api_key = ConfigService.get_value(key="SENDGRID_API_KEY",section="SENDGRID")
            SendGridService.__client = sendgrid.SendGridAPIClient(api_key=api_key)
        return SendGridService.__client
