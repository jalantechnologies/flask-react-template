from dataclasses import dataclass
from typing import Optional, Union


@dataclass(frozen=True)
class SearchAccountParams:
    password: str
    username: str


@dataclass(frozen=True)
class SearchAccountByIdParams:
    id: str


@dataclass(frozen=True)
class CreateAccountByUsernameAndPasswordParams:
    first_name: str
    last_name: str
    password: str
    username: str


@dataclass(frozen=True)
class PhoneNumber:
    country_code: str
    phone_number: str

    def __str__(self) -> str:
        return f"{self.country_code} {self.phone_number}"


@dataclass(frozen=True)
class CreateAccountByPhoneNumberParams:
    phone_number: PhoneNumber


CreateAccountParams = Union[CreateAccountByUsernameAndPasswordParams, CreateAccountByPhoneNumberParams]


@dataclass(frozen=True)
class AccountInfo:
    id: str
    username: str


@dataclass(frozen=True)
class Account:
    id: str
    first_name: str
    last_name: str
    username: str
    phone_number: Optional[PhoneNumber] = None


@dataclass(frozen=True)
class ResetPasswordParams:
    account_id: str
    new_password: str
    token: str


@dataclass(frozen=True)
class AccountErrorCode:
    INVALID_CREDENTIALS: str = "ACCOUNT_ERR_03"
    NOT_FOUND: str = "ACCOUNT_ERR_02"
    USERNAME_ALREADY_EXISTS: str = "ACCOUNT_ERR_01"
    BAD_REQUEST: str = "ACCOUNT_ERR_04"
    PHONE_NUMBER_ALREADY_EXISTS: str = "ACCOUNT_ERR_05"
