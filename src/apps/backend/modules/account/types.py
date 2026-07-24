from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

from modules.core.common.types import QueryParams
from modules.core.errors import AppError


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

    @classmethod
    def from_dict(cls, request_data: dict[str, Any]) -> "CreateAccountByUsernameAndPasswordParams":
        for field in ["first_name", "last_name", "password", "username"]:
            if not isinstance(request_data.get(field), str):
                raise AppError(
                    code=AccountErrorCode.BAD_REQUEST, http_status_code=400, message=f"{field} must be a string"
                )
        return cls(
            first_name=request_data["first_name"],
            last_name=request_data["last_name"],
            password=request_data["password"],
            username=request_data["username"],
        )


@dataclass(frozen=True)
class PhoneNumber:
    country_code: str
    phone_number: str

    def __str__(self) -> str:
        return f"{self.country_code} {self.phone_number}"

    @classmethod
    def from_dict(cls, phone_number_data: Any) -> "PhoneNumber":
        if not isinstance(phone_number_data, dict):
            raise AppError(
                code=AccountErrorCode.BAD_REQUEST, http_status_code=400, message="phone_number must be a JSON object"
            )
        for field in ["country_code", "phone_number"]:
            if not isinstance(phone_number_data.get(field), str):
                raise AppError(
                    code=AccountErrorCode.BAD_REQUEST,
                    http_status_code=400,
                    message=f"phone_number.{field} must be a string",
                )
        return cls(country_code=phone_number_data["country_code"], phone_number=phone_number_data["phone_number"])


@dataclass(frozen=True)
class CreateAccountByPhoneNumberParams:
    phone_number: PhoneNumber

    @classmethod
    def from_dict(cls, request_data: dict[str, Any]) -> "CreateAccountByPhoneNumberParams":
        return cls(phone_number=PhoneNumber.from_dict(request_data.get("phone_number")))


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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class AccountQuery(QueryParams):
    id: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None
    # Accounts are soft-deleted via `active`; reads default to active records only.
    active: Optional[bool] = True


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
    PASSWORD_TOO_WEAK: str = "ACCOUNT_ERR_06"


@dataclass(frozen=True)
class UpdateAccountProfileParams:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
