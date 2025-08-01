import hashlib
import os
import urllib.parse
from datetime import datetime, timedelta
from typing import Any

import bcrypt

from modules.authentication.internals.password_reset_token.store.password_reset_token_model import (
    PasswordResetTokenModel,
)
from modules.authentication.types import PasswordResetToken
from modules.config.config_service import ConfigService
from modules.notification.email_service import EmailService
from modules.notification.types import EmailRecipient, EmailSender, SendEmailParams


class PasswordResetTokenUtil:

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()

    @staticmethod
    def compare_password(*, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def generate_password_reset_token() -> str:
        return hashlib.sha256(os.urandom(60)).hexdigest()

    @staticmethod
    def hash_password_reset_token(reset_token: str) -> str:
        return bcrypt.hashpw(reset_token.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()

    @staticmethod
    def get_token_expires_at() -> datetime:
        default_token_expire_time_in_seconds = ConfigService[int].get_value(key="accounts.token_expires_in_seconds")
        return datetime.now() + timedelta(seconds=default_token_expire_time_in_seconds)

    @staticmethod
    def is_token_expired(expires_at: datetime) -> bool:
        return datetime.now() > expires_at

    @staticmethod
    def convert_password_reset_token_bson_to_password_reset_token(
        password_reset_token_bson: dict[str, Any],
    ) -> PasswordResetToken:
        validated_password_reset_token_data = PasswordResetTokenModel.from_bson(password_reset_token_bson)
        return PasswordResetToken(
            account=str(validated_password_reset_token_data.account),
            id=str(validated_password_reset_token_data.id),
            is_used=validated_password_reset_token_data.is_used,
            is_expired=PasswordResetTokenUtil.is_token_expired(validated_password_reset_token_data.expires_at),
            expires_at=str(validated_password_reset_token_data.expires_at),
            token=validated_password_reset_token_data.token,
        )

    @staticmethod
    def send_password_reset_email(account_id: str, first_name: str, username: str, password_reset_token: str) -> None:
        web_app_host = ConfigService[str].get_value(key="web_app_host")
        default_email = ConfigService[str].get_value(key="mailer.default_email")
        default_email_name = ConfigService[str].get_value(key="mailer.default_email_name")
        forgot_password_mail_template_id = ConfigService[str].get_value(key="mailer.forgot_password_mail_template_id")

        template_data = {
            "first_name": first_name,
            "password_reset_link": f"{web_app_host}/accounts/{account_id}/reset_password?token={urllib.parse.quote(password_reset_token)}",
            "username": username,
        }

        password_reset_email_params = SendEmailParams(
            template_id=forgot_password_mail_template_id,
            recipient=EmailRecipient(email=username),
            sender=EmailSender(email=default_email, name=default_email_name),
            template_data=template_data,
        )

        EmailService.send_email_for_account(
            account_id=account_id, bypass_preferences=True, params=password_reset_email_params
        )
