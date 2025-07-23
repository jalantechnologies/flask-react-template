from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union


@dataclass(frozen=True)
class AccountSearchParams:
    password: str
    username: str


@dataclass(frozen=True)
class AccountSearchByIdParams:
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
    hashed_password: str
    phone_number: Optional[PhoneNumber]
    username: str


@dataclass(frozen=True)
class ResetPasswordParams:
    account_id: str
    new_password: str
    token: str


@dataclass(frozen=True)
class AccountDeletionResult:
    account_id: str
    deleted_at: datetime
    success: bool


@dataclass(frozen=True)
class AccountErrorCode:
    INVALID_CREDENTIALS: str = "ACCOUNT_ERR_03"
    NOT_FOUND: str = "ACCOUNT_ERR_02"
    USERNAME_ALREADY_EXISTS: str = "ACCOUNT_ERR_01"
    BAD_REQUEST: str = "ACCOUNT_ERR_04"
    PHONE_NUMBER_ALREADY_EXISTS: str = "ACCOUNT_ERR_05"


@dataclass(frozen=True)
class UpdateAccountProfileParams:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
