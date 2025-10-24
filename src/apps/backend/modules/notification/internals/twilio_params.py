from typing import List

from phonenumbers import NumberParseException, is_valid_number, parse

from modules.notification.errors import ValidationError
from modules.notification.types import SendSMSParams, ValidationFailure


class SMSParams:
    @staticmethod
    def validate(params: SendSMSParams) -> None:
        failures: List[ValidationFailure] = []

        # Parse and validate recipient phone number
        try:
            parsed_number = parse(str(params.recipient_phone))
            is_recipient_phone_valid = is_valid_number(parsed_number)
        except NumberParseException:
            is_recipient_phone_valid = False

        if not is_recipient_phone_valid:
            failures.append(
                ValidationFailure(
                    field="recipient_phone",
                    message="Please specify a valid recipient phone number in format +12124567890.",
                )
            )

        # Check for a non-empty message body
        if not params.message_body:
            failures.append(ValidationFailure(field="message_body", message="Please specify a non-empty message body."))

        if failures:
            raise ValidationError("SMS cannot be sent, please check the params validity.", failures)
