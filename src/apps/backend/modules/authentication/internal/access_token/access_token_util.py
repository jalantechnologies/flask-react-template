import os
from datetime import datetime, timedelta
from typing import ClassVar

import jwt

from modules.account.types import Account
from modules.authentication.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    AccessTokenSigningKeyInsecureError,
    OTPIncorrectError,
)
from modules.authentication.types import OTP, AccessToken, AccessTokenPayload, OTPStatus
from modules.config.config_service import ConfigService


class AccessTokenUtil:
    SIGNING_KEY_CONFIG_KEY: ClassVar[str] = "accounts.token_signing_key"
    LOCAL_APP_ENVS: ClassVar[frozenset[str]] = frozenset({"development", "testing"})
    INSECURE_SIGNING_KEYS: ClassVar[frozenset[str]] = frozenset({"", "JWT_TOKEN"})

    @staticmethod
    def validate_signing_key() -> None:
        app_env = os.environ.get("APP_ENV", "development")
        if app_env in AccessTokenUtil.LOCAL_APP_ENVS:
            return

        signing_key = ConfigService[str].get_value(key=AccessTokenUtil.SIGNING_KEY_CONFIG_KEY, default="")
        if signing_key.strip() in AccessTokenUtil.INSECURE_SIGNING_KEYS:
            raise AccessTokenSigningKeyInsecureError()

    @staticmethod
    def generate_access_token(*, account: Account) -> AccessToken:
        jwt_signing_key = ConfigService[str].get_value(key=AccessTokenUtil.SIGNING_KEY_CONFIG_KEY)
        jwt_expiry = timedelta(days=ConfigService[int].get_value(key="accounts.token_expiry_days"))
        expiry_time = datetime.now() + jwt_expiry

        payload = {"account_id": account.id, "exp": expiry_time.timestamp()}
        jwt_token = jwt.encode(payload, jwt_signing_key, algorithm="HS256")

        return AccessToken(token=jwt_token, account_id=account.id, expires_at=expiry_time.isoformat())

    @staticmethod
    def verify_access_token(*, token: str) -> AccessTokenPayload:
        jwt_signing_key = ConfigService[str].get_value(key=AccessTokenUtil.SIGNING_KEY_CONFIG_KEY)

        try:
            verified_token = jwt.decode(token, jwt_signing_key, algorithms=["HS256"])
        except jwt.exceptions.DecodeError:
            raise AccessTokenInvalidError("Invalid access token")
        except jwt.ExpiredSignatureError:
            raise AccessTokenExpiredError(message="Access token has expired. Please login again.")

        account_id = verified_token.get("account_id")
        if not account_id or not isinstance(account_id, str):
            raise AccessTokenInvalidError("Invalid access token payload")

        return AccessTokenPayload(account_id=account_id)

    @staticmethod
    def validate_otp_for_access_token(*, otp: OTP) -> None:
        if otp.status != OTPStatus.SUCCESS:
            raise OTPIncorrectError()
