import re
from typing import List

from modules.notification.errors import ValidationError
from modules.notification.types import SendEmailParams, ValidationFailure


class EmailParams:
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    @staticmethod
    def validate(params: SendEmailParams) -> None:
        failures: List[ValidationFailure] = []

        if not EmailParams.is_email_valid(params.recipient.email):
            failures.append(
                ValidationFailure(
                    field="recipient.email", message="Please specify valid recipient email in format you@example.com."
                )
            )

        if not EmailParams.is_email_valid(params.sender.email):
            failures.append(
                ValidationFailure(
                    field="sender.email", message="Please specify valid sender email in format you@example.com."
                )
            )

        if not params.sender.name:
            failures.append(ValidationFailure(field="sender.name", message="Please specify a non-empty sender name."))

        if failures:
            raise ValidationError("Email cannot be sent, please check the params validity.", failures)

    @staticmethod
    def is_email_valid(email: str) -> bool:
        return bool(re.match(EmailParams.email_regex, email.lower()))  # Use your email_regex
