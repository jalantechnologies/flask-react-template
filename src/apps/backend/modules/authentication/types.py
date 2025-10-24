from dataclasses import dataclass
from enum import StrEnum
from typing import Union

from modules.account.types import PhoneNumber


@dataclass(frozen=True)
class AccessToken:
    token: str
    account_id: str
    expires_at: str


@dataclass(frozen=True)
class AccessTokenPayload:
    account_id: str


@dataclass(frozen=True)
class EmailBasedAuthAccessTokenRequestParams:
    password: str
    username: str


@dataclass(frozen=True)
class OTPBasedAuthAccessTokenRequestParams:
    otp_code: str
    phone_number: PhoneNumber


CreateAccessTokenParams = Union[EmailBasedAuthAccessTokenRequestParams, OTPBasedAuthAccessTokenRequestParams]


@dataclass(frozen=True)
class AccessTokenErrorCode:
    UNAUTHORIZED_ACCESS: str = "ACCESS_TOKEN_ERR_01"
    ACCESS_TOKEN_EXPIRED: str = "ACCESS_TOKEN_ERR_02"
    AUTHORIZATION_HEADER_NOT_FOUND: str = "ACCESS_TOKEN_ERR_03"
    INVALID_AUTHORIZATION_HEADER: str = "ACCESS_TOKEN_ERR_04"
    ACCESS_TOKEN_INVALID: str = "ACCESS_TOKEN_ERR_05"


from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordResetToken:
    id: str
    account: str
    expires_at: str
    is_expired: bool
    is_used: bool
    token: str


@dataclass(frozen=True)
class CreatePasswordResetTokenParams:
    username: str


@dataclass(frozen=True)
class PasswordResetTokenErrorCode:
    PASSWORD_RESET_TOKEN_NOT_FOUND: str = "PASSWORD_RESET_TOKEN_ERR_01"


@dataclass(frozen=True)
class OTPStatus(StrEnum):
    EXPIRED: str = "EXPIRED"
    PENDING: str = "PENDING"
    SUCCESS: str = "SUCCESS"


@dataclass(frozen=True)
class OTP:
    id: str
    otp_code: str
    phone_number: PhoneNumber
    status: str


@dataclass(frozen=True)
class OTPErrorCode:
    INCORRECT_OTP: str = "OTP_ERR_01"
    OTP_EXPIRED: str = "OTP_ERR_02"
    REQUEST_FAILED: str = "OTP_ERR_03"


@dataclass(frozen=True)
class CreateOTPParams:
    phone_number: PhoneNumber


@dataclass(frozen=True)
class VerifyOTPParams:
    otp_code: str
    phone_number: PhoneNumber
