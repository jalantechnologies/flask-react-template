from modules.account.types import AccountErrorCode, PhoneNumber
from modules.application.errors import AppError


class AccountWithUserNameExistsError(AppError):
    def __init__(self, username: str) -> None:
        super().__init__(
            code=AccountErrorCode.USERNAME_ALREADY_EXISTS,
            http_status_code=409,
            message=f"An account with the username {username} already exists. Try logging in or use a different username.",
        )


class AccountNotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=AccountErrorCode.NOT_FOUND, http_status_code=404, message=message)


class AccountWithUsernameNotFoundError(AccountNotFoundError):
    def __init__(self, username: str) -> None:
        super().__init__(
            message=f"We could not find an account associated with username: {username}. Please verify it or you can create a new account."
        )


class AccountWithIdNotFoundError(AccountNotFoundError):
    def __init__(self, id: str) -> None:
        super().__init__(message=f"We could not find an account with id: {id}. Please verify and try again.")


class AccountWithPhoneNumberNotFoundError(AccountNotFoundError):
    def __init__(self, phone_number: PhoneNumber) -> None:
        super().__init__(
            message=f"We could not find an account phone number: {phone_number}. Please verify it or you can create a new account."
        )


class AccountInvalidPasswordError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code=AccountErrorCode.INVALID_CREDENTIALS,
            http_status_code=401,
            message="Incorrect password. Please try again or Reset your password if you’ve forgotten it.",
        )


class AccountBadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(code=AccountErrorCode.BAD_REQUEST, http_status_code=400, message=message)


class AccountWithPhoneNumberExistsError(AppError):
    def __init__(self, phone_number: PhoneNumber) -> None:
        super().__init__(
            code=AccountErrorCode.PHONE_NUMBER_ALREADY_EXISTS,
            http_status_code=409,
            message=f"An account with the phone number {phone_number} already exists. Try logging in or use a different phone number.",
        )
