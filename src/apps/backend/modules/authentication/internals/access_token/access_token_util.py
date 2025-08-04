from datetime import datetime, timedelta

import jwt

from modules.account.types import Account
from modules.authentication.errors import AccessTokenExpiredError, AccessTokenInvalidError, OTPIncorrectError
from modules.authentication.types import AccessToken, AccessTokenPayload, OTP, OTPStatus
from modules.config.config_service import ConfigService


class AccessTokenUtil:
    @staticmethod
    def generate_access_token(*, account: Account) -> AccessToken:
        jwt_signing_key = ConfigService[str].get_value(key="accounts.token_signing_key")
        jwt_expiry = timedelta(days=ConfigService[int].get_value(key="accounts.token_expiry_days"))
        expiry_time = datetime.now() + jwt_expiry

        payload = {"account_id": account.id, "exp": expiry_time.timestamp()}
        jwt_token = jwt.encode(payload, jwt_signing_key, algorithm="HS256")

        return AccessToken(token=jwt_token, account_id=account.id, expires_at=expiry_time.isoformat())

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
    def validate_otp_for_access_token(*, otp: OTP) -> None:
        if otp.status != OTPStatus.SUCCESS:
            raise OTPIncorrectError()
