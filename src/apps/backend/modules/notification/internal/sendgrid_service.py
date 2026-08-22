from typing import Optional

import sendgrid
from python_http_client.exceptions import HTTPError
from sendgrid.helpers.mail import From, Mail, TemplateId, To

from modules.core.config.config_service import ConfigService
from modules.core.logger.logger import Logger
from modules.notification.errors import EmailRejectedError, EmailServiceUnavailableError
from modules.notification.internal.sendgrid_email_params import EmailParams
from modules.notification.types import NotificationErrorCode, SendEmailParams

LOWEST_SERVER_ERROR_STATUS = 500


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

        except HTTPError as err:
            status_code = SendGridService.__status_code_of(err)

            if status_code is None:
                raise SendGridService.__unavailable(params, "the provider responded without a status", err) from err

            reason = f"the provider responded with status {status_code}"

            if status_code >= LOWEST_SERVER_ERROR_STATUS:
                raise SendGridService.__unavailable(params, reason, err, status_code) from err

            raise SendGridService.__rejected(params, reason, err, status_code) from err

        except OSError as err:
            raise SendGridService.__unavailable(params, "the request never reached the provider", err) from err

        except sendgrid.SendGridException as err:
            raise SendGridService.__rejected(params, "the message failed provider validation", err) from err

    @staticmethod
    def __status_code_of(error: HTTPError) -> Optional[int]:
        try:
            return int(error.status_code)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def __rejected(
        params: SendEmailParams, reason: str, error: Exception, status_code: Optional[int] = None
    ) -> EmailRejectedError:
        SendGridService.__log_failure(params, NotificationErrorCode.EMAIL_REJECTED, reason, error)
        return EmailRejectedError(recipient=params.recipient.email, reason=reason, status_code=status_code)

    @staticmethod
    def __unavailable(
        params: SendEmailParams, reason: str, error: Exception, status_code: Optional[int] = None
    ) -> EmailServiceUnavailableError:
        SendGridService.__log_failure(params, NotificationErrorCode.EMAIL_SERVICE_UNAVAILABLE, reason, error)
        return EmailServiceUnavailableError(recipient=params.recipient.email, reason=reason, status_code=status_code)

    @staticmethod
    def __log_failure(params: SendEmailParams, code: str, reason: str, error: Exception) -> None:
        Logger.error(
            message=(
                "[notification.sendgrid_email_failure] SendGrid email delivery failed | "
                f"notification_error_code={code} "
                f"template_id={params.template_id} "
                f"reason={reason} "
                f"error_type={type(error).__name__}"
            )
        )

    @staticmethod
    def get_client() -> sendgrid.SendGridAPIClient:
        if not SendGridService.__client:
            api_key = ConfigService[str].get_value(key="sendgrid.api_key")
            SendGridService.__client = sendgrid.SendGridAPIClient(api_key=api_key)
        return SendGridService.__client
