import os
from datetime import datetime, timedelta
from typing import Any, ClassVar

import jwt

from modules.account.types import Account
from modules.authentication.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    AccessTokenSigningKeyInsecureError,
    OTPIncorrectError,
)
from modules.authentication.types import OTP, AccessToken, AccessTokenPayload, OTPStatus
from modules.core.config.config_service import ConfigService


class AccessTokenUtil:
    SIGNING_KEY_CONFIG_KEY: ClassVar[str] = "accounts.token_signing_key"
    VERIFICATION_KEYS_CONFIG_KEY: ClassVar[str] = "accounts.token_verification_keys"
    LOCAL_APP_ENVS: ClassVar[frozenset[str]] = frozenset({"development", "testing"})
    INSECURE_SIGNING_KEYS: ClassVar[frozenset[str]] = frozenset({"", "JWT_TOKEN"})

    @staticmethod
    def validate_signing_key() -> None:
        app_env = os.environ.get("APP_ENV", "development")
        if app_env in AccessTokenUtil.LOCAL_APP_ENVS:
            return

        signing_key = ConfigService[str].get_value(key=AccessTokenUtil.SIGNING_KEY_CONFIG_KEY, default="")
        for key in [signing_key, *AccessTokenUtil._get_configured_verification_keys()]:
            if key.strip() in AccessTokenUtil.INSECURE_SIGNING_KEYS:
                raise AccessTokenSigningKeyInsecureError()

    @staticmethod
    def generate_access_token(*, account: Account) -> AccessToken:
        jwt_signing_key = ConfigService[str].get_value(key=AccessTokenUtil.SIGNING_KEY_CONFIG_KEY).strip()
        jwt_expiry = timedelta(days=ConfigService[int].get_value(key="accounts.token_expiry_days"))
        expiry_time = datetime.now() + jwt_expiry

        payload = {"account_id": account.id, "exp": expiry_time.timestamp()}
        jwt_token = jwt.encode(payload, jwt_signing_key, algorithm="HS256")

        return AccessToken(token=jwt_token, account_id=account.id, expires_at=expiry_time.isoformat())

    @staticmethod
    def _get_configured_verification_keys() -> list[str]:
        configured_keys = ConfigService[list[str]].get_value(
            key=AccessTokenUtil.VERIFICATION_KEYS_CONFIG_KEY, default=[]
        )

        return [stripped_key for key in configured_keys if (stripped_key := key.strip())]

    @staticmethod
    def _get_accepted_verification_keys() -> list[str]:
        signing_key = ConfigService[str].get_value(key=AccessTokenUtil.SIGNING_KEY_CONFIG_KEY).strip()

        accepted_keys = [signing_key]
        for key in AccessTokenUtil._get_configured_verification_keys():
            if key not in accepted_keys:
                accepted_keys.append(key)

        return accepted_keys

    @staticmethod
    def _decode_with_accepted_keys(token: str) -> dict[str, Any]:
        accepted_keys = AccessTokenUtil._get_accepted_verification_keys()

        for key in accepted_keys:
            try:
                return jwt.decode(token, key, algorithms=["HS256"])
            except jwt.exceptions.InvalidSignatureError:
                continue
            except jwt.ExpiredSignatureError:
                raise AccessTokenExpiredError(message="Access token has expired. Please login again.")
            except jwt.exceptions.DecodeError:
                raise AccessTokenInvalidError("Invalid access token")

        raise AccessTokenInvalidError("Invalid access token")

    @staticmethod
    def verify_access_token(*, token: str) -> AccessTokenPayload:
        verified_token = AccessTokenUtil._decode_with_accepted_keys(token)

        account_id = verified_token.get("account_id")
        if not account_id or not isinstance(account_id, str):
            raise AccessTokenInvalidError("Invalid access token payload")

        return AccessTokenPayload(account_id=account_id)

    @staticmethod
    def validate_otp_for_access_token(*, otp: OTP) -> None:
        if otp.status != OTPStatus.SUCCESS:
            raise OTPIncorrectError()
