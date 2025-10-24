from modules.application.errors import AppError
from modules.authentication.types import AccessTokenErrorCode, OTPErrorCode, PasswordResetTokenErrorCode


class AccessTokenInvalidError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=AccessTokenErrorCode.ACCESS_TOKEN_INVALID, http_status_code=401, message=message)


class AccessTokenExpiredError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=AccessTokenErrorCode.ACCESS_TOKEN_EXPIRED, http_status_code=401, message=message)


class UnauthorizedAccessError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=AccessTokenErrorCode.UNAUTHORIZED_ACCESS, http_status_code=401, message=message)


class AuthorizationHeaderNotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code=AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND, http_status_code=401, message=message
        )


class InvalidAuthorizationHeaderError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=AccessTokenErrorCode.INVALID_AUTHORIZATION_HEADER, http_status_code=401, message=message)


class PasswordResetTokenNotFoundError(AppError):

    def __init__(self) -> None:
        super().__init__(
            code=PasswordResetTokenErrorCode.PASSWORD_RESET_TOKEN_NOT_FOUND,
            http_status_code=404,
            message=f"System is unable to find a token with this account",
        )


class OTPIncorrectError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code=OTPErrorCode.INCORRECT_OTP, http_status_code=400, message="Please provide the correct OTP to login."
        )


class OTPExpiredError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code=OTPErrorCode.OTP_EXPIRED,
            http_status_code=400,
            message="The OTP has expired. Please request a new OTP.",
        )


class OTPRequestFailedError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code=OTPErrorCode.REQUEST_FAILED, http_status_code=400, message="Please provide a valid phone number."
        )
