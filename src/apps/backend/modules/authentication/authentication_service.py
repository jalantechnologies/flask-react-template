import urllib.parse
from dataclasses import asdict
from datetime import datetime, timedelta

import jwt

from modules.account.errors import AccountBadRequestError
from modules.account.types import Account, PhoneNumber
from modules.authentication.errors import AccessTokenExpiredError, AccessTokenInvalidError, OTPIncorrectError
from modules.authentication.internals.otp.otp_util import OTPUtil
from modules.authentication.internals.otp.otp_writer import OTPWriter
from modules.authentication.internals.password_reset_token.password_reset_token_reader import PasswordResetTokenReader
from modules.authentication.internals.password_reset_token.password_reset_token_util import PasswordResetTokenUtil
from modules.authentication.internals.password_reset_token.password_reset_token_writer import PasswordResetTokenWriter
from modules.authentication.types import (
    OTP,
    AccessToken,
    AccessTokenPayload,
    CreateOTPParams,
    OTPBasedAuthAccessTokenRequestParams,
    OTPStatus,
    PasswordResetToken,
    VerifyOTPParams,
)
from modules.config.config_service import ConfigService
from modules.notification.email_service import EmailService
from modules.notification.sms_service import SMSService
from modules.notification.types import EmailRecipient, EmailSender, SendEmailParams, SendSMSParams


class AuthenticationService:
    @staticmethod
    def create_access_token_by_username_and_password(*, account: Account) -> AccessToken:
        return AuthenticationService.__generate_access_token(account=account)

    @staticmethod
    def create_access_token_by_phone_number(
        *, params: OTPBasedAuthAccessTokenRequestParams, account: Account
    ) -> AccessToken:
        otp = AuthenticationService.verify_otp(
            params=VerifyOTPParams(phone_number=params.phone_number, otp_code=params.otp_code)
        )

        if otp.status != OTPStatus.SUCCESS:
            raise OTPIncorrectError()

        return AuthenticationService.__generate_access_token(account=account)

    @staticmethod
    def __generate_access_token(*, account: Account) -> AccessToken:
        jwt_signing_key = ConfigService[str].get_value(key="accounts.token_signing_key")
        jwt_expiry = timedelta(days=ConfigService[int].get_value(key="accounts.token_expiry_days"))
        expiry_time = datetime.now() + jwt_expiry
        payload = {"account_id": account.id, "exp": (expiry_time).timestamp()}
        jwt_token = jwt.encode(payload, jwt_signing_key, algorithm="HS256")
        access_token = AccessToken(token=jwt_token, account_id=account.id, expires_at=expiry_time.isoformat())

        return access_token

    @staticmethod
    def verify_access_token(*, token: str) -> AccessTokenPayload:

        jwt_signing_key = ConfigService[str].get_value(key="accounts.token_signing_key")

        try:
            verified_token = jwt.decode(token, jwt_signing_key, algorithms=["HS256"])
        except jwt.exceptions.DecodeError:
            raise AccessTokenInvalidError("Invalid access token")
        except jwt.ExpiredSignatureError:
            raise AccessTokenExpiredError(message="Access token has expired. Please login again.")

        return AccessTokenPayload(account_id=verified_token.get("account_id"))

    @staticmethod
    def create_password_reset_token(params: Account) -> PasswordResetToken:
        token = PasswordResetTokenUtil.generate_password_reset_token()
        password_reset_token = PasswordResetTokenWriter.create_password_reset_token(params.id, token)
        AuthenticationService.send_password_reset_email(params.id, params.first_name, params.username, token)

        return password_reset_token

    @staticmethod
    def get_password_reset_token_by_account_id(account_id: str) -> PasswordResetToken:
        return PasswordResetTokenReader.get_password_reset_token_by_account_id(account_id)

    @staticmethod
    def set_password_reset_token_as_used_by_id(password_reset_token_id: str) -> PasswordResetToken:
        return PasswordResetTokenWriter.set_password_reset_token_as_used(password_reset_token_id)

    @staticmethod
    def verify_password_reset_token(account_id: str, token: str) -> PasswordResetToken:
        password_reset_token = AuthenticationService.get_password_reset_token_by_account_id(account_id)

        if password_reset_token.is_expired:
            raise AccountBadRequestError(
                f"Password reset link is expired for accountId {account_id}. Please retry with new link"
            )
        if password_reset_token.is_used:
            raise AccountBadRequestError(
                f"Password reset is already used for accountId {account_id}. Please retry with new link"
            )

        is_token_valid = PasswordResetTokenUtil.compare_password(
            password=token, hashed_password=password_reset_token.token
        )
        if not is_token_valid:
            raise AccountBadRequestError(
                f"Password reset link is invalid for accountId {account_id}. Please retry with new link."
            )

        return password_reset_token

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

        EmailService.send_email_for_account(params=password_reset_email_params)

    @staticmethod
    def create_otp(*, params: CreateOTPParams) -> OTP:
        recipient_phone_number = PhoneNumber(**asdict(params)["phone_number"])
        otp = OTPWriter.create_new_otp(params=params)

        send_sms_params = SendSMSParams(
            message_body=f"{otp.otp_code} is your One Time Password (OTP) for verification.",
            recipient_phone=recipient_phone_number,
        )
        if not OTPUtil.is_default_otp_enabled():
            SMSService.send_sms_for_account(params=send_sms_params)

        return otp

    @staticmethod
    def verify_otp(*, params: VerifyOTPParams) -> OTP:
        return OTPWriter.verify_otp(params=params)
